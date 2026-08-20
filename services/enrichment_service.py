from models.annotation import (
    Annotation,
)

from models.author import Author

from models.candidates import (
    OrcidCandidate,
    ViafCandidate,
    GettyCandidate,
)

from models.publication import (
    Publication,
)

from services.orcid_service import (
    OrcidService,
)

from services.viaf_service import (
    ViafService,
)

from services.getty_service import (
    GettyService,
)


class EnrichmentService:

    def __init__(
        self,
        orcid_service: OrcidService,
        viaf_service: ViafService,
        getty_service: GettyService,
    ):
        self.orcid = orcid_service
        self.viaf = viaf_service
        self.getty = getty_service

    # -------------------------
    # ORCID
    # -------------------------

    def search_author_orcid(
        self,
        author: Author,
    ) -> list[OrcidCandidate]:

        return self.orcid.search_person(
            given_names=author.given_name,
            family_name=author.family_name,
        )

    def enrich_author_with_orcid(
        self,
        author: Author,
        candidate: OrcidCandidate,
        load_record: bool = True,
    ):
        author.orcid_id = (
            candidate.orcid_id
        )

        author.resolved_name = (
            candidate.display_name
        )

        self._merge_unique(
            author.other_names,
            candidate.other_names,
        )

        self._merge_unique(
            author.institutions,
            candidate.institutions,
        )

        author.add_source(
            "orcid"
        )

        if not load_record:
            return

        record = self.orcid.get_record(
            candidate.orcid_id
        )

        normalized = (
            self.orcid.normalize_record(
                record
            )
        )

        self._merge_unique(
            author.other_names,
            normalized.get(
                "other_names",
                [],
            ),
        )

        external_ids = normalized.get(
            "external_identifiers",
            {},
        )

        author.external_identifiers.update(
            external_ids
        )

    # -------------------------
    # VIAF
    # -------------------------

    def search_author_viaf(
        self,
        author: Author,
    ) -> list[ViafCandidate]:

        search_name = (
            author.resolved_name
            or author.display_name
        )

        return self.viaf.search_person(
            search_name
        )

    def enrich_author_with_viaf(
        self,
        author: Author,
        candidate: ViafCandidate,
        load_record: bool = True,
    ):
        author.viaf_id = (
            candidate.viaf_id
        )

        if not author.resolved_name:
            author.resolved_name = (
                candidate.display_name
            )

        author.add_source(
            "viaf"
        )

        if not load_record:
            return

        record = self.viaf.get_record(
            candidate.viaf_id
        )

        normalized = (
            self.viaf.normalize_record(
                record
            )
        )

        self._merge_unique(
            author.other_names,
            normalized.get(
                "preferred_names",
                [],
            ),
        )

        for (
            source,
            identifier,
        ) in normalized.get(
            "source_identifiers",
            {},
        ).items():

            author.external_identifiers[
                source
            ] = identifier

    # -------------------------
    # GETTY
    # -------------------------

    def search_getty_aat(
        self,
        query: str,
    ) -> list[GettyCandidate]:

        return self.getty.search_aat(
            query=query,
            limit=10,
        )

    def add_getty_annotation(
        self,
        publication: Publication,
        candidate: GettyCandidate,
    ):
        annotation = Annotation(
            annotation_type="theme",
            source="Getty AAT",
            external_id=(
                candidate.external_id
            ),
            label=candidate.name,
            uri=candidate.uri,
        )

        publication.add_annotation(
            annotation
        )

    # -------------------------

    @staticmethod
    def _merge_unique(
        target: list,
        values: list,
    ):
        for value in values:
            if (
                value
                and value not in target
            ):
                target.append(value)