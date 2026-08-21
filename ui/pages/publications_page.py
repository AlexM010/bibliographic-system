from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QMessageBox
from cloud.storage_client import StorageClient, StorageClientError
from ui.widgets.publication_card import PublicationCard
from ui.pages.edit_publication_page import EditPublicationDialog
from ui.pages.view_publication_page import ViewPublicationDialog

class PublicationsPage(QWidget):

    # Initialize the publication library page for the signed-in user.
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.storage = StorageClient()
        self.publications = []
        self._build_ui()
        self.load_publications()

    # Build the page header, search box and publication list area.
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(16)
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel('My Publications')
        title.setObjectName('pageTitle')
        self.count_label = QLabel('0 publications')
        self.count_label.setObjectName('muted')
        title_box.addWidget(title)
        title_box.addWidget(self.count_label)
        header.addLayout(title_box)
        header.addStretch()
        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(self.load_publications)
        header.addWidget(refresh_button)
        layout.addLayout(header)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search by title, author, DOI, journal or annotation...')
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.apply_filter)
        layout.addWidget(self.search)
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(8)
        layout.addWidget(self.list_widget, 1)

    # Load publications from the backend and refresh the page.
    def load_publications(self):
        try:
            self.publications = self.storage.list_publications(self.user.id_token)
        except StorageClientError as error:
            QMessageBox.critical(self, 'Could not load publications', str(error))
            return
        self.count_label.setText(self._publication_count_text(len(self.publications)))
        self.apply_filter()

    # Filter loaded publications using the current search text.
    def apply_filter(self):
        query = self.search.text().strip().lower()
        if not query:
            self._render(self.publications)
            return
        filtered = []
        for publication in self.publications:
            searchable_values = [publication.get('title') or '', publication.get('journal') or '', publication.get('doi') or '', str(publication.get('year') or '')]
            for author in publication.get('authors') or []:
                searchable_values.extend([author.get('display_name') or '', author.get('resolved_name') or '', author.get('given_name') or '', author.get('family_name') or '', author.get('orcid_id') or '', author.get('viaf_id') or ''])
                identifiers = author.get('identifiers') or {}
                if isinstance(identifiers, dict):
                    searchable_values.extend([identifiers.get('orcid') or '', identifiers.get('viaf') or ''])
                for other_name in author.get('other_names') or []:
                    if isinstance(other_name, str):
                        searchable_values.append(other_name)
            user_metadata = publication.get('user_metadata') or {}
            searchable_values.append(user_metadata.get('notes') or '')
            tags = user_metadata.get('tags') or []
            searchable_values.extend((str(tag) for tag in tags))
            for annotation in publication.get('annotations') or []:
                searchable_values.extend([annotation.get('label') or '', annotation.get('source') or '', annotation.get('external_id') or ''])
            searchable_text = ' '.join((str(value) for value in searchable_values if value)).lower()
            if query in searchable_text:
                filtered.append(publication)
        self._render(filtered)

    # Rebuild the publication cards shown on the page.
    def _render(self, publications):
        self.list_widget.clear()
        if not publications:
            item = QListWidgetItem('No publications found.')
            item.setSizeHint(QSize(100, 70))
            self.list_widget.addItem(item)
            return
        for publication in publications:
            item = QListWidgetItem()
            card = PublicationCard(publication)
            card.view_requested.connect(self.view_publication)
            card.edit_requested.connect(self.edit_publication)
            card.delete_requested.connect(self.delete_publication)
            item.setSizeHint(QSize(100, 145))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)

    # Open the read-only publication details dialog.
    def view_publication(self, publication):
        dialog = ViewPublicationDialog(publication=publication, parent=self)
        dialog.exec()

    # Open the edit dialog and refresh the list after a successful save.
    def edit_publication(self, publication):
        dialog = EditPublicationDialog(publication=publication, user=self.user, parent=self)
        result = dialog.exec()
        if result:
            self.load_publications()

    # Confirm and delete a publication from the backend.
    def delete_publication(self, publication):
        publication_id = publication.get('id')
        if not publication_id:
            QMessageBox.critical(self, 'Delete Publication', 'The publication does not have an ID.')
            return
        title = publication.get('title') or 'Untitled publication'
        answer = QMessageBox.question(self, 'Delete Publication', f'Are you sure you want to permanently delete this publication?\n\n{title}\n\nThis action cannot be undone.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer != QMessageBox.Yes:
            return
        try:
            self.storage.delete_publication(publication_id=publication_id, id_token=self.user.id_token)
        except StorageClientError as error:
            QMessageBox.critical(self, 'Delete Failed', str(error))
            return
        self.load_publications()

    @staticmethod
    # Return the singular or plural text used for the publication count.
    def _publication_count_text(count):
        if count == 1:
            return '1 publication'
        return f'{count} publications'
