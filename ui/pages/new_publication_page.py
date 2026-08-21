from PySide6.QtCore import (
    Signal,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QMessageBox,
    QGroupBox,
    QListWidget,
    QInputDialog,
    QScrollArea,
)

from config.settings import (
    CROSSREF_EMAIL,
)

from parsers.apa_parser import (
    ApaParser,
    ApaParseError,
)

from services.crossref_service import (
    CrossrefService,
)

from services.publication_service import (
    PublicationService,
)

from services.orcid_service import (
    OrcidService,
    OrcidServiceError,
)

from services.viaf_service import (
    ViafService,
    ViafServiceError,
)

from services.getty_service import (
    GettyService,
    GettyServiceError,
)

from services.enrichment_service import (
    EnrichmentService,
)

from cloud.storage_client import (
    StorageClient,
    StorageClientError,
)

from ui.dialogs.candidate_dialog import (
    CandidateDialog,
)

from ui.widgets.full_text_widget import (
    FullTextWidget,
)


class NewPublicationPage(QWidget):

    publication_saved = Signal()

    def __init__(
        self,
        user,
    ):
        super().__init__()

        self.user = user

        self.publication = None

        self.storage = (
            StorageClient()
        )

        self._build_services()
        self._build_ui()

    def _build_services(self):

        parser = ApaParser()

        crossref = CrossrefService(
            user_email=CROSSREF_EMAIL
        )

        self.publication_service = (
            PublicationService(
                apa_parser=parser,
                crossref_service=crossref,
            )
        )

        self.enrichment = (
            EnrichmentService(
                orcid_service=OrcidService(),
                viaf_service=ViafService(),
                getty_service=GettyService(),
            )
        )

    def _build_ui(self):

        root_layout = QVBoxLayout(
            self
        )

        root_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        content = QWidget()
        content.setObjectName("pageContent")

        layout = QVBoxLayout(
            content
        )

        layout.setContentsMargins(
            30,
            26,
            30,
            30,
        )

        layout.setSpacing(
            18
        )

        # =====================
        # HEADER
        # =====================

        title = QLabel(
            "New Publication"
        )

        title.setObjectName(
            "pageTitle"
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Paste an APA citation, review the "
            "detected metadata and choose which "
            "external sources should enrich it."
        )

        subtitle.setObjectName(
            "muted"
        )

        layout.addWidget(
            subtitle
        )

        # =====================
        # APA
        # =====================

        apa_group = QGroupBox(
            "APA Citation"
        )

        apa_layout = QVBoxLayout(
            apa_group
        )

        self.apa_input = QTextEdit()

        self.apa_input.setPlaceholderText(
            "Paste APA citation here..."
        )

        self.apa_input.setMaximumHeight(
            120
        )

        apa_layout.addWidget(
            self.apa_input
        )

        parse_button = QPushButton(
            "Parse citation"
        )

        parse_button.setObjectName(
            "primaryButton"
        )

        parse_button.clicked.connect(
            self.parse_citation
        )

        apa_layout.addWidget(
            parse_button
        )

        layout.addWidget(
            apa_group
        )

        # =====================
        # METADATA
        # =====================

        metadata_group = QGroupBox(
            "Bibliographic Metadata"
        )

        form = QFormLayout(
            metadata_group
        )

        self.title_input = QLineEdit()
        self.year_input = QLineEdit()
        self.journal_input = QLineEdit()
        self.volume_input = QLineEdit()
        self.issue_input = QLineEdit()
        self.pages_input = QLineEdit()
        self.doi_input = QLineEdit()

        form.addRow(
            "Title",
            self.title_input,
        )

        form.addRow(
            "Year",
            self.year_input,
        )

        form.addRow(
            "Journal",
            self.journal_input,
        )

        form.addRow(
            "Volume",
            self.volume_input,
        )

        form.addRow(
            "Issue",
            self.issue_input,
        )

        form.addRow(
            "Pages",
            self.pages_input,
        )

        form.addRow(
            "DOI",
            self.doi_input,
        )

        layout.addWidget(
            metadata_group
        )

        # =====================
        # AUTHORS
        # =====================

        authors_group = QGroupBox(
            "Authors"
        )

        authors_layout = QVBoxLayout(
            authors_group
        )

        self.authors_list = QListWidget()

        self.authors_list.setMaximumHeight(
            200
        )

        authors_layout.addWidget(
            self.authors_list
        )

        layout.addWidget(
            authors_group
        )

        # =====================
        # FULL PAPER
        # =====================

        full_text_group = QGroupBox(
            "Full Paper"
        )

        full_text_layout = QVBoxLayout(
            full_text_group
        )

        full_text_description = QLabel(
            "Optionally reference the complete paper "
            "from this computer or from an online location."
        )

        full_text_description.setObjectName(
            "muted"
        )

        full_text_description.setWordWrap(
            True
        )

        full_text_layout.addWidget(
            full_text_description
        )

        self.full_text_widget = (
            FullTextWidget()
        )

        full_text_layout.addWidget(
            self.full_text_widget
        )

        layout.addWidget(
            full_text_group
        )

        # =====================
        # ENRICHMENT
        # =====================

        enrichment_group = QGroupBox(
            "Metadata Enrichment"
        )

        enrichment_layout = QVBoxLayout(
            enrichment_group
        )

        description = QLabel(
            "Select only the vocabularies and "
            "authority services you want to use."
        )

        description.setObjectName(
            "muted"
        )

        enrichment_layout.addWidget(
            description
        )

        self.orcid_checkbox = QCheckBox(
            "ORCID — researcher identifiers"
        )

        self.viaf_checkbox = QCheckBox(
            "VIAF — author authority identifiers"
        )

        self.getty_checkbox = QCheckBox(
            "Getty AAT — thematic annotations"
        )

        enrichment_layout.addWidget(
            self.orcid_checkbox
        )

        enrichment_layout.addWidget(
            self.viaf_checkbox
        )

        enrichment_layout.addWidget(
            self.getty_checkbox
        )

        enrich_button = QPushButton(
            "Find selected enrichments"
        )

        enrich_button.clicked.connect(
            self.run_enrichments
        )

        enrichment_layout.addWidget(
            enrich_button
        )

        self.status_label = QLabel(
            "Parse a citation first."
        )

        self.status_label.setObjectName(
            "muted"
        )

        enrichment_layout.addWidget(
            self.status_label
        )

        layout.addWidget(
            enrichment_group
        )

        # =====================
        # GETTY ANNOTATIONS
        # =====================

        annotations_group = QGroupBox(
            "Selected Annotations"
        )

        annotation_layout = QVBoxLayout(
            annotations_group
        )

        self.annotations_list = QListWidget()

        self.annotations_list.setMaximumHeight(
            130
        )

        annotation_layout.addWidget(
            self.annotations_list
        )

        layout.addWidget(
            annotations_group
        )

        # =====================
        # USER METADATA
        # =====================

        metadata_user_group = QGroupBox(
            "Personal Metadata"
        )

        user_layout = QVBoxLayout(
            metadata_user_group
        )

        user_layout.addWidget(
            QLabel("Notes")
        )

        self.notes_input = QTextEdit()

        self.notes_input.setMaximumHeight(
            100
        )

        user_layout.addWidget(
            self.notes_input
        )

        user_layout.addWidget(
            QLabel("Tags")
        )

        self.tags_input = QLineEdit()

        self.tags_input.setPlaceholderText(
            "security, networks, thesis"
        )

        user_layout.addWidget(
            self.tags_input
        )

        layout.addWidget(
            metadata_user_group
        )

        # =====================
        # ACTIONS
        # =====================

        actions = QHBoxLayout()

        actions.addStretch()

        clear_button = QPushButton(
            "Clear"
        )

        clear_button.clicked.connect(
            self.clear_form
        )

        self.save_button = QPushButton(
            "Save publication"
        )

        self.save_button.setObjectName(
            "primaryButton"
        )

        self.save_button.setEnabled(
            False
        )

        self.save_button.clicked.connect(
            self.save_publication
        )

        actions.addWidget(
            clear_button
        )

        actions.addWidget(
            self.save_button
        )

        layout.addLayout(
            actions
        )

        layout.addStretch()

        scroll.setWidget(
            content
        )

        root_layout.addWidget(
            scroll
        )

    # ==================================================
    # PARSE
    # ==================================================

    def parse_citation(self):

        citation = (
            self.apa_input
            .toPlainText()
            .strip()
        )

        if not citation:

            QMessageBox.warning(
                self,
                "Missing citation",
                "Paste an APA citation first.",
            )

            return

        try:

            self.publication = (
                self.publication_service
                .create_from_apa(
                    citation
                )
            )

        except ApaParseError as error:

            QMessageBox.critical(
                self,
                "APA parsing error",
                str(error),
            )

            return

        self.title_input.setText(
            self.publication.title
            or ""
        )

        self.year_input.setText(
            str(
                self.publication.year
                or ""
            )
        )

        self.journal_input.setText(
            self.publication.journal
            or ""
        )

        self.volume_input.setText(
            self.publication.volume
            or ""
        )

        self.issue_input.setText(
            self.publication.issue
            or ""
        )

        self.pages_input.setText(
            self.publication.pages
            or ""
        )

        self.doi_input.setText(
            self.publication.doi
            or ""
        )

        self._refresh_authors()
        self._refresh_annotations()

        self.status_label.setText(
            "Citation parsed. Review the metadata "
            "and optionally run enrichments."
        )

        self.save_button.setEnabled(
            True
        )

    # ==================================================
    # ENRICHMENTS
    # ==================================================

    def run_enrichments(self):

        if not self.publication:

            QMessageBox.warning(
                self,
                "No publication",
                "Parse a citation first.",
            )

            return

        if not (
            self.orcid_checkbox.isChecked()
            or self.viaf_checkbox.isChecked()
            or self.getty_checkbox.isChecked()
        ):

            QMessageBox.information(
                self,
                "Enrichment",
                "Select at least one enrichment source.",
            )

            return

        if self.orcid_checkbox.isChecked():
            self._run_orcid()

        if self.viaf_checkbox.isChecked():
            self._run_viaf()

        if self.getty_checkbox.isChecked():
            self._run_getty()

        self._refresh_authors()
        self._refresh_annotations()

        self.status_label.setText(
            "Enrichment finished."
        )

    def _run_orcid(self):

        for author in self.publication.authors:

            if author.orcid_id:
                continue

            self.status_label.setText(
                f"Searching ORCID for "
                f"{author.display_name}..."
            )

            try:

                candidates = (
                    self.enrichment
                    .search_author_orcid(
                        author
                    )
                )

            except OrcidServiceError as error:

                QMessageBox.warning(
                    self,
                    "ORCID",
                    str(error),
                )

                continue

            selected = CandidateDialog.choose(
                parent=self,

                title=(
                    f"ORCID — "
                    f"{author.display_name}"
                ),

                candidates=candidates,

                formatter=lambda c: (
                    f"{c.display_name}\n"
                    f"ORCID: {c.orcid_id}"
                    + (
                        "\n"
                        + ", ".join(
                            c.institutions[:3]
                        )
                        if c.institutions
                        else ""
                    )
                ),
            )

            if selected:

                self.enrichment.enrich_author_with_orcid(
                    author,
                    selected,
                )

    def _run_viaf(self):

        for author in self.publication.authors:

            if author.viaf_id:
                continue

            self.status_label.setText(
                f"Searching VIAF for "
                f"{author.display_name}..."
            )

            try:

                candidates = (
                    self.enrichment
                    .search_author_viaf(
                        author
                    )
                )

            except ViafServiceError as error:

                QMessageBox.warning(
                    self,
                    "VIAF",
                    str(error),
                )

                continue

            selected = CandidateDialog.choose(
                parent=self,

                title=(
                    f"VIAF — "
                    f"{author.display_name}"
                ),

                candidates=candidates,

                formatter=lambda c: (
                    f"{c.display_name}\n"
                    f"VIAF: {c.viaf_id}"
                ),
            )

            if selected:

                self.enrichment.enrich_author_with_viaf(
                    author,
                    selected,
                )

    def _run_getty(self):

        while True:

            query, ok = QInputDialog.getText(
                self,
                "Getty AAT",
                "Search term:",
            )

            query = query.strip()

            if not ok or not query:
                return

            try:

                candidates = (
                    self.enrichment
                    .search_getty_aat(
                        query
                    )
                )

            except GettyServiceError as error:

                QMessageBox.warning(
                    self,
                    "Getty AAT",
                    str(error),
                )

                return

            selected = CandidateDialog.choose(
                parent=self,

                title=(
                    f"Getty AAT — {query}"
                ),

                candidates=candidates,

                formatter=lambda c: (
                    f"{c.name}\n"
                    f"{c.external_id}  ·  "
                    f"score={c.score}"
                ),
            )

            if selected:

                self.enrichment.add_getty_annotation(
                    self.publication,
                    selected,
                )

                self._refresh_annotations()

            again = QMessageBox.question(
                self,
                "Getty AAT",
                "Add another Getty annotation?",
                QMessageBox.Yes
                | QMessageBox.No,
            )

            if again != QMessageBox.Yes:
                break

    # ==================================================
    # DISPLAY
    # ==================================================

    def _refresh_authors(self):

        self.authors_list.clear()

        if not self.publication:
            return

        for author in (
            self.publication.authors
        ):

            lines = [
                author.display_name
            ]

            if author.orcid_id:

                lines.append(
                    f"ORCID: {author.orcid_id}"
                )

            if author.viaf_id:

                lines.append(
                    f"VIAF: {author.viaf_id}"
                )

            self.authors_list.addItem(
                "\n".join(lines)
            )

    def _refresh_annotations(self):

        self.annotations_list.clear()

        if not self.publication:
            return

        for annotation in (
            self.publication.annotations
        ):

            self.annotations_list.addItem(
                f"{annotation.label} "
                f"· {annotation.source}"
            )

    # ==================================================
    # SAVE
    # ==================================================

    def save_publication(self):

        if not self.publication:
            return

        self.publication.title = (
            self.title_input
            .text()
            .strip()
        )

        year = (
            self.year_input
            .text()
            .strip()
        )

        self.publication.year = (
            int(year)
            if year.isdigit()
            else None
        )

        self.publication.journal = (
            self.journal_input
            .text()
            .strip()
            or None
        )

        self.publication.volume = (
            self.volume_input
            .text()
            .strip()
            or None
        )

        self.publication.issue = (
            self.issue_input
            .text()
            .strip()
            or None
        )

        self.publication.pages = (
            self.pages_input
            .text()
            .strip()
            or None
        )

        self.publication.doi = (
            self.doi_input
            .text()
            .strip()
            or None
        )

        self.publication.full_text = (
            self.full_text_widget.value()
        )

        self.publication.user_metadata[
            "notes"
        ] = (
            self.notes_input
            .toPlainText()
            .strip()
        )

        self.publication.user_metadata[
            "tags"
        ] = [
            tag.strip()
            for tag in (
                self.tags_input
                .text()
                .split(",")
            )
            if tag.strip()
        ]

        try:

            publication_id = (
                self.storage
                .save_publication(
                    self.publication,
                    self.user.id_token,
                )
            )

        except StorageClientError as error:

            QMessageBox.critical(
                self,
                "Save failed",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Publication saved",
            (
                "The publication was added "
                "to your library."
            ),
        )

        self.publication_saved.emit()

        self.clear_form()

    # ==================================================
    # CLEAR
    # ==================================================

    def clear_form(self):

        self.publication = None

        self.apa_input.clear()
        self.title_input.clear()
        self.year_input.clear()
        self.journal_input.clear()
        self.volume_input.clear()
        self.issue_input.clear()
        self.pages_input.clear()
        self.doi_input.clear()

        self.full_text_widget.clear()

        self.authors_list.clear()
        self.annotations_list.clear()

        self.notes_input.clear()
        self.tags_input.clear()

        self.orcid_checkbox.setChecked(
            False
        )

        self.viaf_checkbox.setChecked(
            False
        )

        self.getty_checkbox.setChecked(
            False
        )

        self.save_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Parse a citation first."
        )