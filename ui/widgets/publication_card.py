from PySide6.QtCore import (
    Signal,
)

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)


class PublicationCard(QFrame):

    view_requested = Signal(dict)
    edit_requested = Signal(dict)
    delete_requested = Signal(dict)

    def __init__(
        self,
        publication,
        parent=None,
    ):
        super().__init__(parent)

        self.publication = (
            publication
        )

        self.setObjectName(
            "publicationCard"
        )

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            16,
            12,
            16,
            12,
        )

        layout.setSpacing(
            7
        )

        # ====================================================
        # TOP
        # ====================================================

        top_layout = QHBoxLayout()

        title = QLabel(
            self.publication.get(
                "title"
            )
            or "Untitled publication"
        )

        title.setObjectName(
            "publicationCardTitle"
        )

        title.setWordWrap(
            True
        )

        top_layout.addWidget(
            title,
            1,
        )

        layout.addLayout(
            top_layout
        )

        # ====================================================
        # METADATA
        # ====================================================

        year = (
            self.publication.get(
                "year"
            )
            or ""
        )

        journal = (
            self.publication.get(
                "journal"
            )
            or ""
        )

        metadata_parts = []

        if year:
            metadata_parts.append(
                str(year)
            )

        if journal:
            metadata_parts.append(
                str(journal)
            )

        metadata_label = QLabel(
            " · ".join(
                metadata_parts
            )
        )

        metadata_label.setObjectName(
            "muted"
        )

        layout.addWidget(
            metadata_label
        )

        # ====================================================
        # AUTHORS
        # ====================================================

        authors = (
            self.publication.get(
                "authors"
            )
            or []
        )

        author_names = []

        for author in authors[:4]:

            name = (
                author.get(
                    "resolved_name"
                )
                or author.get(
                    "display_name"
                )
            )

            if not name:

                given = (
                    author.get(
                        "given_name"
                    )
                    or ""
                )

                family = (
                    author.get(
                        "family_name"
                    )
                    or ""
                )

                name = (
                    f"{given} {family}"
                    .strip()
                )

            if name:
                author_names.append(
                    name
                )

        authors_text = (
            ", ".join(
                author_names
            )
        )

        if len(authors) > 4:

            authors_text += (
                f" +{len(authors) - 4}"
            )

        if authors_text:

            authors_label = QLabel(
                authors_text
            )

            authors_label.setObjectName(
                "muted"
            )

            authors_label.setWordWrap(
                True
            )

            layout.addWidget(
                authors_label
            )

        # ====================================================
        # BUTTONS
        # ====================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        view_button = QPushButton(
            "View"
        )

        edit_button = QPushButton(
            "Edit"
        )

        delete_button = QPushButton(
            "Delete"
        )

        delete_button.setObjectName(
            "dangerButton"
        )

        view_button.clicked.connect(
            self._request_view
        )

        edit_button.clicked.connect(
            self._request_edit
        )

        delete_button.clicked.connect(
            self._request_delete
        )

        buttons.addWidget(
            view_button
        )

        buttons.addWidget(
            edit_button
        )

        buttons.addWidget(
            delete_button
        )

        layout.addLayout(
            buttons
        )

    # ========================================================
    # SIGNALS
    # ========================================================

    def _request_view(self):

        self.view_requested.emit(
            self.publication
        )

    def _request_edit(self):

        self.edit_requested.emit(
            self.publication
        )

    def _request_delete(self):

        self.delete_requested.emit(
            self.publication
        )