from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OrcidCandidate:
    orcid_id: str
    given_names: str
    family_names: str

    credit_name: Optional[str] = None

    other_names: list[str] = field(
        default_factory=list
    )

    institutions: list[str] = field(
        default_factory=list
    )

    emails: list[str] = field(
        default_factory=list
    )

    @property
    def display_name(self) -> str:
        if self.credit_name:
            return self.credit_name

        return (
            f"{self.given_names} "
            f"{self.family_names}"
        ).strip()


@dataclass
class ViafCandidate:
    viaf_id: str
    display_name: str

    term: Optional[str] = None
    name_type: Optional[str] = None
    lc: Optional[str] = None
    score: Optional[str] = None


@dataclass
class GettyCandidate:
    external_id: str
    name: str

    score: Optional[float] = None
    match: bool = False
    uri: Optional[str] = None