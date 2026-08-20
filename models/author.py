from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Author:
    family_name: str
    given_name: str = ""

    orcid_id: Optional[str] = None
    viaf_id: Optional[str] = None

    resolved_name: Optional[str] = None

    other_names: list[str] = field(
        default_factory=list
    )

    institutions: list[str] = field(
        default_factory=list
    )

    external_identifiers: dict = field(
        default_factory=dict
    )

    enrichment_sources: list[str] = field(
        default_factory=list
    )

    @property
    def display_name(self) -> str:
        if self.resolved_name:
            return self.resolved_name

        return (
            f"{self.given_name} "
            f"{self.family_name}"
        ).strip()

    def add_source(self, source: str):
        if source not in self.enrichment_sources:
            self.enrichment_sources.append(
                source
            )

    def to_dict(self) -> dict:
        return {
            "family_name": self.family_name,
            "given_name": self.given_name,
            "display_name": self.display_name,
            "resolved_name": self.resolved_name,

            "identifiers": {
                "orcid": self.orcid_id,
                "viaf": self.viaf_id,
            },

            "other_names": self.other_names,
            "institutions": self.institutions,

            "external_identifiers":
                self.external_identifiers,

            "enrichment_sources":
                self.enrichment_sources,
        }