from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit, QLabel, QPushButton, QMessageBox, QGroupBox, QScrollArea, QWidget, QInputDialog
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from models.author import Author
from services.orcid_service import OrcidService, OrcidServiceError
from services.viaf_service import ViafService, ViafServiceError
from services.getty_service import GettyService, GettyServiceError
from services.enrichment_service import EnrichmentService
from cloud.storage_client import StorageClient, StorageClientError
from ui.dialogs.candidate_dialog import CandidateDialog
from ui.widgets.full_text_widget import FullTextWidget

class EditPublicationDialog(QDialog):

    # Initialize the edit dialog and the services used by its enrichment actions.
    def __init__(self, publication, user, parent=None):
        super().__init__(parent)
        self.publication = publication
        self.user = user
        self.storage = StorageClient()
        self.enrichment = EnrichmentService(orcid_service=OrcidService(), viaf_service=ViafService(), getty_service=GettyService())
        self.setWindowTitle('Edit Publication')
        self.resize(820, 780)
        self._build_ui()

    # Build the editable metadata, full-paper, author and annotation sections.
    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName('pageContent')
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(18)
        title = QLabel('Edit Publication')
        title.setObjectName('pageTitle')
        self.content_layout.addWidget(title)
        subtitle = QLabel('Edit bibliographic metadata and manage authority identifiers and annotations.')
        subtitle.setObjectName('muted')
        self.content_layout.addWidget(subtitle)
        metadata_group = QGroupBox('Bibliographic Metadata')
        form = QFormLayout(metadata_group)
        self.title_input = QLineEdit(self.publication.get('title', ''))
        self.year_input = QLineEdit(str(self.publication.get('year') or ''))
        self.journal_input = QLineEdit(self.publication.get('journal') or '')
        self.volume_input = QLineEdit(self.publication.get('volume') or '')
        self.issue_input = QLineEdit(self.publication.get('issue') or '')
        self.pages_input = QLineEdit(self.publication.get('pages') or '')
        self.doi_input = QLineEdit(self.publication.get('doi') or '')
        form.addRow('Title', self.title_input)
        form.addRow('Year', self.year_input)
        form.addRow('Journal', self.journal_input)
        form.addRow('Volume', self.volume_input)
        form.addRow('Issue', self.issue_input)
        form.addRow('Pages', self.pages_input)
        form.addRow('DOI', self.doi_input)
        self.content_layout.addWidget(metadata_group)
        full_text_group = QGroupBox('Full Paper')
        full_text_layout = QVBoxLayout(full_text_group)
        full_text_description = QLabel('Reference the complete paper from a local PDF or from an online location.')
        full_text_description.setObjectName('muted')
        full_text_description.setWordWrap(True)
        full_text_layout.addWidget(full_text_description)
        self.full_text_widget = FullTextWidget(full_text=self.publication.get('full_text'))
        full_text_layout.addWidget(self.full_text_widget)
        self.content_layout.addWidget(full_text_group)
        self.authors_group = QGroupBox('Authors & Authority Identifiers')
        authors_outer_layout = QVBoxLayout(self.authors_group)
        self.authors_scroll = QScrollArea()
        self.authors_scroll.setWidgetResizable(True)
        self.authors_scroll.setMinimumHeight(250)
        self.authors_scroll.setMaximumHeight(420)
        self.authors_container = QWidget()
        self.authors_layout = QVBoxLayout(self.authors_container)
        self.authors_layout.setSpacing(10)
        self.authors_scroll.setWidget(self.authors_container)
        authors_outer_layout.addWidget(self.authors_scroll)
        self.content_layout.addWidget(self.authors_group)
        self._render_authors()
        self.annotations_group = QGroupBox('Getty AAT Annotations')
        self.annotations_layout = QVBoxLayout(self.annotations_group)
        self.annotations_container = QWidget()
        self.annotation_items_layout = QVBoxLayout(self.annotations_container)
        self.annotations_layout.addWidget(self.annotations_container)
        add_getty_button = QPushButton('Add Getty AAT annotation')
        add_getty_button.clicked.connect(self.add_getty_annotation)
        self.annotations_layout.addWidget(add_getty_button)
        self.content_layout.addWidget(self.annotations_group)
        self._render_annotations()
        user_metadata = self.publication.get('user_metadata') or {}
        personal_group = QGroupBox('Personal Metadata')
        personal_layout = QVBoxLayout(personal_group)
        personal_layout.addWidget(QLabel('Notes'))
        self.notes_input = QTextEdit()
        self.notes_input.setPlainText(user_metadata.get('notes', ''))
        self.notes_input.setMaximumHeight(120)
        personal_layout.addWidget(self.notes_input)
        personal_layout.addWidget(QLabel('Tags'))
        self.tags_input = QLineEdit(', '.join(user_metadata.get('tags', [])))
        personal_layout.addWidget(self.tags_input)
        self.content_layout.addWidget(personal_group)
        self.content_layout.addStretch()
        scroll.setWidget(content)
        root_layout.addWidget(scroll)
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton('Cancel')
        save = QPushButton('Save changes')
        save.setObjectName('primaryButton')
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.save_changes)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        root_layout.addLayout(buttons)

    # Remove all widgets currently stored in a layout.
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # Rebuild the author cards from the current publication data.
    def _render_authors(self):
        self._clear_layout(self.authors_layout)
        authors = self.publication.get('authors') or []
        for index, author in enumerate(authors):
            card = QGroupBox()
            card_layout = QVBoxLayout(card)
            name = author.get('resolved_name') or author.get('display_name') or f"{author.get('given_name', '')} {author.get('family_name', '')}".strip()
            name_label = QLabel(f'<b>{name}</b>')
            card_layout.addWidget(name_label)
            identifiers = author.get('identifiers') or {}
            orcid = identifiers.get('orcid')
            viaf = identifiers.get('viaf')
            ids_label = QLabel(f"ORCID: {orcid or '-'}\nVIAF: {viaf or '-'}")
            ids_label.setObjectName('muted')
            card_layout.addWidget(ids_label)
            buttons = QHBoxLayout()
            if orcid:
                open_orcid_button = QPushButton('Open ORCID')
                open_orcid_button.clicked.connect(lambda checked=False, value=orcid: QDesktopServices.openUrl(QUrl(f'https://orcid.org/{value}')))
                buttons.addWidget(open_orcid_button)
            orcid_button = QPushButton('Change ORCID' if orcid else 'Add ORCID')
            viaf_button = QPushButton('Change VIAF' if viaf else 'Add VIAF')
            if viaf:
                open_viaf_button = QPushButton('Open VIAF')
                open_viaf_button.clicked.connect(lambda checked=False, value=viaf: QDesktopServices.openUrl(QUrl(f'https://viaf.org/viaf/{value}')))
                buttons.addWidget(open_viaf_button)
            clear_orcid_button = QPushButton('Remove ORCID')
            clear_viaf_button = QPushButton('Remove VIAF')
            orcid_button.clicked.connect(lambda checked=False, i=index: self.edit_orcid(i))
            viaf_button.clicked.connect(lambda checked=False, i=index: self.edit_viaf(i))
            clear_orcid_button.clicked.connect(lambda checked=False, i=index: self.remove_orcid(i))
            clear_viaf_button.clicked.connect(lambda checked=False, i=index: self.remove_viaf(i))
            buttons.addWidget(orcid_button)
            buttons.addWidget(viaf_button)
            if orcid:
                buttons.addWidget(clear_orcid_button)
            if viaf:
                buttons.addWidget(clear_viaf_button)
            buttons.addStretch()
            card_layout.addLayout(buttons)
            self.authors_layout.addWidget(card)
        self.authors_layout.addStretch()

    # Convert a stored author dictionary back to an Author object.
    def _author_object(self, author_data) -> Author:
        identifiers = author_data.get('identifiers') or {}
        return Author(family_name=author_data.get('family_name', ''), given_name=author_data.get('given_name', ''), orcid_id=identifiers.get('orcid'), viaf_id=identifiers.get('viaf'), resolved_name=author_data.get('resolved_name'), other_names=author_data.get('other_names') or [], institutions=author_data.get('institutions') or [], external_identifiers=author_data.get('external_identifiers') or {}, enrichment_sources=author_data.get('enrichment_sources') or [])

    # Search ORCID and replace the selected author ORCID data.
    def edit_orcid(self, index):
        author_data = self.publication['authors'][index]
        author = self._author_object(author_data)
        try:
            candidates = self.enrichment.search_author_orcid(author)
        except OrcidServiceError as error:
            QMessageBox.warning(self, 'ORCID', str(error))
            return
        selected = CandidateDialog.choose(parent=self, title=f'ORCID — {author.display_name}', candidates=candidates, formatter=lambda c: f'{c.display_name}\nORCID: {c.orcid_id}' + ('\n' + ', '.join(c.institutions[:3]) if c.institutions else ''))
        if not selected:
            return
        self.enrichment.enrich_author_with_orcid(author, selected)
        self.publication['authors'][index] = author.to_dict()
        self._render_authors()

    # Search VIAF and replace the selected author VIAF data.
    def edit_viaf(self, index):
        author_data = self.publication['authors'][index]
        author = self._author_object(author_data)
        try:
            candidates = self.enrichment.search_author_viaf(author)
        except ViafServiceError as error:
            QMessageBox.warning(self, 'VIAF', str(error))
            return
        selected = CandidateDialog.choose(parent=self, title=f'VIAF — {author.display_name}', candidates=candidates, formatter=lambda c: f'{c.display_name}\nVIAF: {c.viaf_id}')
        if not selected:
            return
        self.enrichment.enrich_author_with_viaf(author, selected)
        self.publication['authors'][index] = author.to_dict()
        self._render_authors()

    # Remove the ORCID identifier from one author.
    def remove_orcid(self, index):
        author = self.publication['authors'][index]
        identifiers = author.setdefault('identifiers', {})
        identifiers['orcid'] = None
        self._render_authors()

    # Remove the VIAF identifier from one author.
    def remove_viaf(self, index):
        author = self.publication['authors'][index]
        identifiers = author.setdefault('identifiers', {})
        identifiers['viaf'] = None
        self._render_authors()

    # Rebuild the list of publication annotations.
    def _render_annotations(self):
        self._clear_layout(self.annotation_items_layout)
        annotations = self.publication.get('annotations') or []
        if not annotations:
            label = QLabel('No Getty annotations.')
            label.setObjectName('muted')
            self.annotation_items_layout.addWidget(label)
            return
        for index, annotation in enumerate(annotations):
            row = QHBoxLayout()
            label = QLabel(f"{annotation.get('label', '-')} · {annotation.get('source', '-')}")
            remove = QPushButton('Remove')
            remove.clicked.connect(lambda checked=False, i=index: self.remove_annotation(i))
            row.addWidget(label, 1)
            row.addWidget(remove)
            self.annotation_items_layout.addLayout(row)

    # Search Getty AAT and add the term selected by the user.
    def add_getty_annotation(self):
        query, ok = QInputDialog.getText(self, 'Getty AAT', 'Search term:')
        query = query.strip()
        if not ok or not query:
            return
        try:
            candidates = self.enrichment.search_getty_aat(query)
        except GettyServiceError as error:
            QMessageBox.warning(self, 'Getty AAT', str(error))
            return
        selected = CandidateDialog.choose(parent=self, title=f'Getty AAT — {query}', candidates=candidates, formatter=lambda c: f'{c.name}\n{c.external_id} · score={c.score}')
        if not selected:
            return
        annotations = self.publication.setdefault('annotations', [])
        for annotation in annotations:
            if annotation.get('source') == 'getty_aat' and annotation.get('external_id') == selected.external_id:
                return
        annotations.append({'type': 'theme', 'source': 'getty_aat', 'external_id': selected.external_id, 'label': selected.name, 'uri': selected.uri})
        self._render_annotations()

    # Remove one annotation from the publication.
    def remove_annotation(self, index):
        annotations = self.publication.get('annotations') or []
        if 0 <= index < len(annotations):
            annotations.pop(index)
        self._render_annotations()

    # Copy the edited values to the publication and save it to the backend.
    def save_changes(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, 'Missing title', 'Title cannot be empty.')
            return
        self.publication['title'] = title
        year = self.year_input.text().strip()
        self.publication['year'] = int(year) if year.isdigit() else None
        self.publication['journal'] = self.journal_input.text().strip() or None
        self.publication['volume'] = self.volume_input.text().strip() or None
        self.publication['issue'] = self.issue_input.text().strip() or None
        self.publication['pages'] = self.pages_input.text().strip() or None
        self.publication['doi'] = self.doi_input.text().strip() or None
        self.publication['full_text'] = self.full_text_widget.value()
        metadata = self.publication.setdefault('user_metadata', {})
        metadata['notes'] = self.notes_input.toPlainText().strip()
        metadata['tags'] = [tag.strip() for tag in self.tags_input.text().split(',') if tag.strip()]
        try:
            self.storage.save_publication(self.publication, self.user.id_token)
        except StorageClientError as error:
            QMessageBox.critical(self, 'Save failed', str(error))
            return
        QMessageBox.information(self, 'Saved', 'Publication updated successfully.')
        self.accept()
