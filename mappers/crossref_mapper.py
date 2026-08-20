from typing import Optional

from models.author import Author
from models.publication import Publication


def _normalize_orcid(
    value: Optional[str],
) -> Optional[str]:
    """
    Μετατρέπει π.χ.

    https://orcid.org/0000-0002-1520-4327

    σε

    0000-0002-1520-4327
    """

    if not value:
        return None

    value = value.strip()

    if "/" in value:
        value = value.rstrip("/").split("/")[-1]

    return value or None


def _extract_year(
    data: dict,
) -> Optional[int]:

    possible_dates = [
        data.get("published-print"),
        data.get("published-online"),
        data.get("published"),
        data.get("issued"),
    ]

    for date_object in possible_dates:

        if not isinstance(date_object, dict):
            continue

        date_parts = date_object.get(
            "date-parts"
        )

        if not date_parts:
            continue

        if not date_parts[0]:
            continue

        year = date_parts[0][0]

        if isinstance(year, int):
            return year

    return None


def _map_publication_type(
    crossref_type: Optional[str],
) -> str:

    mapping = {
        "journal-article": "journal_article",
        "proceedings-article": "conference_paper",
        "book-chapter": "book_chapter",
        "book": "book",
        "dissertation": "dissertation",
        "posted-content": "posted_content",
        "report": "report",
        "dataset": "dataset",
        "reference-entry": "reference_entry",
    }

    if not crossref_type:
        return "unknown"

    return mapping.get(
        crossref_type,
        crossref_type.replace("-", "_"),
    )


def _extract_title(
    data: dict,
) -> str:

    titles = data.get(
        "title",
        []
    )

    if isinstance(titles, list) and titles:
        return titles[0].strip()

    if isinstance(titles, str):
        return titles.strip()

    return "Unknown Title"


def _extract_journal(
    data: dict,
) -> Optional[str]:

    containers = data.get(
        "container-title",
        []
    )

    if isinstance(containers, list) and containers:
        return containers[0].strip()

    if isinstance(containers, str):
        return containers.strip()

    return None


def _map_authors(
    data: dict,
) -> list[Author]:

    authors = []

    for author_data in data.get(
        "author",
        []
    ):
        family_name = (
            author_data.get(
                "family"
            )
            or ""
        ).strip()

        given_name = (
            author_data.get(
                "given"
            )
            or ""
        ).strip()

        orcid_id = _normalize_orcid(
            author_data.get(
                "ORCID"
            )
        )

        # Το Crossref συνήθως μας δίνει ήδη
        # πολύ καλύτερο όνομα από το APA.
        #
        # APA:
        # Zabulis, X.
        #
        # Crossref:
        # Xenophon Zabulis

        resolved_name = (
            f"{given_name} {family_name}"
        ).strip()

        author = Author(
            family_name=family_name,
            given_name=given_name,

            orcid_id=orcid_id,

            resolved_name=(
                resolved_name
                if resolved_name
                else None
            ),

            enrichment_sources=[
                "crossref"
            ],
        )

        authors.append(
            author
        )

    return authors


def crossref_to_publication(
    data: dict,
    raw_citation: str,
) -> Publication:

    publication = Publication(
        raw_citation=raw_citation,

        title=_extract_title(
            data
        ),

        year=_extract_year(
            data
        ),

        authors=_map_authors(
            data
        ),

        publication_type=(
            _map_publication_type(
                data.get(
                    "type"
                )
            )
        ),

        journal=_extract_journal(
            data
        ),

        volume=data.get(
            "volume"
        ),

        issue=data.get(
            "issue"
        ),

        pages=data.get(
            "page"
        ),

        doi=data.get(
            "DOI"
        ),

        metadata_sources=[
            "crossref"
        ],
    )

    return publication