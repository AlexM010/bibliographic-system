import re
import requests
from typing import Optional
from models.author import Author
from models.publication import Publication


class ApaParseError(ValueError):
    pass

class ApaParser:

    # Prepare the HTTP headers used for optional Crossref lookups.
    def __init__(self, user_email: Optional[str]=None):
        self.headers = {'User-Agent': f"PublicationParser/1.0 (mailto:{(user_email if user_email else 'anonymous@example.com')})"}

    # Parse an APA citation locally and improve it with Crossref when possible.
    def parse(self, citation: str) -> Publication:
        citation = citation.strip()
        if not citation:
            raise ApaParseError('Citation cannot be empty.')
        local_pub = self._parse_locally(citation)
        # A DOI is the most reliable way to replace the local parse with structured metadata.
        if local_pub.doi:
            remote_pub = self._fetch_from_crossref_by_doi(local_pub.doi, citation)
            if remote_pub:
                return remote_pub
        # Use title search only when important fields are still missing.
        if local_pub.title and (not local_pub.journal or not local_pub.year):
            remote_pub = self._search_crossref_by_title(local_pub.title, citation)
            if remote_pub:
                return remote_pub
        return local_pub

    # Extract DOI, year, authors and journal details from the citation text.
    def _parse_locally(self, citation: str) -> Publication:
        work_text = citation
        print(f'Parsing citation locally: {work_text}')
        doi = None
        doi_match = re.search('(?:https?://(?:dx\\.)?doi\\.org/|doi:\\s*)(10\\.\\d{4,9}/[-._;()/:A-Za-z0-9]+)', work_text, re.IGNORECASE)
        if doi_match:
            doi = doi_match.group(1).rstrip('.')
            work_text = work_text.replace(doi_match.group(0), '').strip()
        year = None
        year_match = re.search('\\((?P<year>\\d{4}[a-z]?|n\\.d\\.)\\)', work_text)
        if year_match:
            raw_year = year_match.group('year')
            if raw_year[:4].isdigit():
                year = int(raw_year[:4])
            authors_part = work_text[:year_match.start()].strip()
            rest_part = work_text[year_match.end():].strip().lstrip('.')
        else:
            authors_part = ''
            rest_part = work_text
        authors = self._parse_authors_flexible(authors_part) if authors_part else []
        parts = [p.strip() for p in rest_part.split('.') if p.strip()]
        title = parts[0] if len(parts) > 0 else 'Unknown Title'
        journal, volume, issue, pages = (None, None, None, None)
        if len(parts) > 1:
            source_info = parts[1]
            details_match = re.search('(?P<journal>.+?),\\s*(?P<volume>\\d+)(?:\\((?P<issue>[^)]+)\\))?(?:,\\s*(?P<pages>[\\d\\s–-]+))?', source_info)
            if details_match:
                journal = details_match.group('journal').strip()
                volume = details_match.group('volume')
                issue = details_match.group('issue')
                pages = details_match.group('pages')
                if pages:
                    pages = pages.replace('–', '-').replace('—', '-').strip()
            else:
                journal = source_info
        return Publication(raw_citation=citation, title=title, year=year, authors=authors, journal=journal, volume=volume, issue=issue, pages=pages, doi=doi)

    # Extract APA-style author surnames and initials from the author section.
    def _parse_authors_flexible(self, authors_text: str) -> list[Author]:
        authors = []
        pattern = re.compile("(?P<family>[A-Za-zÀ-ÖØ-öø-ÿΑ-Ωα-ωΆ-ώ'’\\-]+(?:\\s+[A-Za-zÀ-ÖØ-öø-ÿΑ-Ωα-ωΆ-ώ'’\\-]+)*),\\s*(?P<given>(?:[A-ZΑ-Ω]\\.(?:\\s*[A-ZΑ-Ω]\\.)*))")
        for match in pattern.finditer(authors_text):
            family_name = match.group('family').strip()
            given_name = match.group('given').strip()
            authors.append(Author(family_name=family_name, given_name=given_name))
        return authors

    # Look up a publication in Crossref using its DOI.
    def _fetch_from_crossref_by_doi(self, doi: str, raw_citation: str) -> Optional[Publication]:
        url = f'https://api.crossref.org/works/{doi}'
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                data = response.json()['message']
                return self._map_crossref_to_publication(data, raw_citation)
        except requests.RequestException:
            # Network failure should not stop the local APA parser.
            pass
        return None

    # Search Crossref by title when key local metadata is missing.
    def _search_crossref_by_title(self, title: str, raw_citation: str) -> Optional[Publication]:
        url = 'https://api.crossref.org/works'
        params = {'query.title': title, 'rows': 1}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=5)
            if response.status_code == 200:
                items = response.json()['message']['items']
                if items:
                    return self._map_crossref_to_publication(items[0], raw_citation)
        except requests.RequestException:
            pass
        return None

    # Convert the Crossref response used by this parser to a Publication.
    def _map_crossref_to_publication(self, data: dict, raw_citation: str) -> Publication:
        titles = data.get('title', [])
        title = titles[0] if titles else 'Unknown Title'
        published = data.get('published-print') or data.get('published-online') or {}
        date_parts = published.get('date-parts', [[None]])[0]
        year = date_parts[0] if date_parts and date_parts[0] else None
        containers = data.get('container-title', [])
        journal = containers[0] if containers else None
        authors = []
        for a in data.get('author', []):
            authors.append(Author(family_name=a.get('family', ''), given_name=a.get('given', '')))
        return Publication(raw_citation=raw_citation, title=title, year=year, authors=authors, journal=journal, volume=data.get('volume'), issue=data.get('issue'), pages=data.get('page'), doi=data.get('DOI'))
