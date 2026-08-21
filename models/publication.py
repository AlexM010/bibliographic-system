from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4
from models.author import Author
from models.annotation import Annotation

@dataclass
class Publication:
    raw_citation: str
    title: str
    year: Optional[int]
    authors: List[Author]
    publication_type: str = 'journal_article'
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    # This stores only a local path or URL; the PDF is never uploaded.
    full_text: Optional[dict] = None
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata_sources: list[str] = field(default_factory=list)
    annotations: list[Annotation] = field(default_factory=list)
    user_metadata: dict = field(default_factory=lambda: {'notes': '', 'tags': []})

    # Add an annotation only when the same source ID is not already present.
    def add_annotation(self, annotation: Annotation):
        for existing in self.annotations:
            if existing.source == annotation.source and existing.external_id == annotation.external_id:
                return
        self.annotations.append(annotation)

    # Convert the publication and nested objects to a storage dictionary.
    def to_dict(self) -> dict:
        return {'id': self.id, 'raw_citation': self.raw_citation, 'type': self.publication_type, 'title': self.title, 'year': self.year, 'authors': [author.to_dict() for author in self.authors], 'journal': self.journal, 'volume': self.volume, 'issue': self.issue, 'pages': self.pages, 'doi': self.doi, 'full_text': self.full_text, 'metadata_sources': self.metadata_sources, 'annotations': [annotation.to_dict() for annotation in self.annotations], 'user_metadata': self.user_metadata}
