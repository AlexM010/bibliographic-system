from models.publication import Publication
from parsers.apa_parser import ApaParser
from services.crossref_service import CrossrefService
from mappers.crossref_mapper import crossref_to_publication

class PublicationService:

    # Keep the APA parser and Crossref service used to create publications.
    def __init__(self, apa_parser: ApaParser, crossref_service: CrossrefService):
        self.apa_parser = apa_parser
        self.crossref_service = crossref_service

    # Create a publication from APA text and enrich it with Crossref when possible.
    def create_from_apa(self, citation: str) -> Publication:
        local_publication = self.apa_parser.parse(citation)
        if local_publication.doi:
            crossref_data = self.crossref_service.get_by_doi(local_publication.doi)
            if crossref_data:
                remote_publication = crossref_to_publication(crossref_data, citation)
                return self._merge_publications(local_publication, remote_publication)
        return local_publication

    # Search Crossref candidates for the current publication title.
    def search_crossref_candidates(self, publication: Publication, limit: int=5) -> list[Publication]:
        if not publication.title:
            return []
        results = self.crossref_service.search_by_title(publication.title, rows=limit)
        candidates = []
        for data in results:
            candidate = crossref_to_publication(data, publication.raw_citation)
            candidates.append(candidate)
        return candidates

    # Merge Crossref metadata into a publication while keeping its local identity.
    def _merge_publications(self, local: Publication, remote: Publication) -> Publication:
        # Keep the local ID so replacing metadata does not create a new publication.
        remote.id = local.id
        remote.raw_citation = local.raw_citation
        if not remote.title or remote.title == 'Unknown Title':
            remote.title = local.title
        if remote.year is None:
            remote.year = local.year
        if not remote.authors:
            remote.authors = local.authors
        if not remote.journal:
            remote.journal = local.journal
        if not remote.volume:
            remote.volume = local.volume
        if not remote.issue:
            remote.issue = local.issue
        if not remote.pages:
            remote.pages = local.pages
        if not remote.doi:
            remote.doi = local.doi
        remote.annotations = local.annotations
        remote.user_metadata = local.user_metadata
        remote.metadata_sources = list(dict.fromkeys(local.metadata_sources + remote.metadata_sources))
        return remote
