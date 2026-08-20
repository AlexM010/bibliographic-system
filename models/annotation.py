from dataclasses import dataclass
from typing import Optional


@dataclass
class Annotation:
    annotation_type: str
    source: str
    external_id: str
    label: str

    uri: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": self.annotation_type,
            "source": self.source,
            "external_id": self.external_id,
            "label": self.label,
            "uri": self.uri,
        }