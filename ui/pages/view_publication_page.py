import html
import os

from PySide6.QtCore import (
    Qt,
    QUrl,
)

from PySide6.QtGui import (
    QDesktopServices,
)

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QScrollArea,
    QWidget,
)


class ViewPublicationDialog(
    QDialog
):

    def __init__(
        self,
        publication,
        parent=None,
    ):
        super().__init__(parent)

        self.publication = (
            publication
        )

        self.setWindowTitle(
            "Publication Details"
        )

        self.resize(
            820,
            800,
        )

        self._build_ui()

    # ========================================================
    # UI
    # ========================================================

    def _build_ui(self):

        root_layout = QVBoxLayout(
            self
        )

        # ====================================================
        # SCROLL AREA
        # ====================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        content = QWidget()

        content.setObjectName(
            "pageContent"
        )

        layout = QVBoxLayout(
            content
        )

        layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        layout.setSpacing(
            16
        )

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel(
            self.publication.get(
                "title"
            )
            or "Untitled publication"
        )

        title.setObjectName(
            "pageTitle"
        )

        title.setWordWrap(
            True
        )

        layout.addWidget(
            title
        )

        publication_type = (
            self.publication.get(
                "publication_type"
            )
            or self.publication.get(
                "type"
            )
        )

        if publication_type:

            type_label = QLabel(
                str(
                    publication_type
                )
                .replace(
                    "_",
                    " ",
                )
                .title()
            )

            type_label.setObjectName(
                "muted"
            )

            layout.addWidget(
                type_label
            )

        # ====================================================
        # BIBLIOGRAPHIC METADATA
        # ====================================================

        bibliographic_group = QGroupBox(
            "Bibliographic Metadata"
        )

        bibliographic_layout = QVBoxLayout(
            bibliographic_group
        )

        fields = [
            (
                "Year",
                self.publication.get(
                    "year"
                ),
            ),
            (
                "Journal / Venue",
                self.publication.get(
                    "journal"
                ),
            ),
            (
                "Volume",
                self.publication.get(
                    "volume"
                ),
            ),
            (
                "Issue",
                self.publication.get(
                    "issue"
                ),
            ),
            (
                "Pages",
                self.publication.get(
                    "pages"
                ),
            ),
        ]

        for (
            field_name,
            value,
        ) in fields:

            if value in (
                None,
                "",
            ):
                continue

            label = QLabel(
                "<b>"
                + html.escape(
                    field_name
                )
                + ":</b> "
                + html.escape(
                    str(value)
                )
            )

            label.setWordWrap(
                True
            )

            bibliographic_layout.addWidget(
                label
            )

        # ----------------------------------------------------
        # DOI
        # ----------------------------------------------------

        doi = (
            self.publication.get(
                "doi"
            )
        )

        if doi:

            clean_doi = (
                str(doi)
                .replace(
                    "https://doi.org/",
                    "",
                )
                .strip()
            )

            doi_url = (
                f"https://doi.org/"
                f"{clean_doi}"
            )

            doi_label = QLabel(
                "<b>DOI:</b> "
                f'<a href="{html.escape(doi_url)}">'
                f"{html.escape(clean_doi)}"
                "</a>"
            )

            doi_label.setOpenExternalLinks(
                True
            )

            doi_label.setTextInteractionFlags(
                Qt.TextBrowserInteraction
            )

            bibliographic_layout.addWidget(
                doi_label
            )

        layout.addWidget(
            bibliographic_group
        )

        # ====================================================
        # FULL PAPER
        # ====================================================

        full_text = (
            self.publication.get(
                "full_text"
            )
            or {}
        )

        if isinstance(full_text, dict):

            full_text_type = (
                full_text.get("type")
                or ""
            )

            location = (
                full_text.get("location")
                or ""
            )

            location = str(location).strip()

            if location:

                full_text_group = QGroupBox(
                    "Full Paper"
                )

                full_text_layout = QVBoxLayout(
                    full_text_group
                )

                if full_text_type == "local":

                    filename = (
                        os.path.basename(location)
                        or location
                    )

                    file_label = QLabel(
                        "<b>Local file:</b> "
                        + html.escape(filename)
                    )

                    file_label.setWordWrap(True)

                    full_text_layout.addWidget(
                        file_label
                    )

                    path_label = QLabel(
                        html.escape(location)
                    )

                    path_label.setObjectName(
                        "muted"
                    )

                    path_label.setWordWrap(True)

                    path_label.setTextInteractionFlags(
                        Qt.TextSelectableByMouse
                    )

                    full_text_layout.addWidget(
                        path_label
                    )

                    if os.path.exists(location):

                        open_button = QPushButton(
                            "Open Paper"
                        )

                        open_button.setObjectName(
                            "primaryButton"
                        )

                        open_button.clicked.connect(
                            lambda checked=False, path=location:
                            QDesktopServices.openUrl(
                                QUrl.fromLocalFile(path)
                            )
                        )

                        full_text_layout.addWidget(
                            open_button
                        )

                    else:

                        unavailable_label = QLabel(
                            "This local file is not available "
                            "on this computer."
                        )

                        unavailable_label.setObjectName(
                            "muted"
                        )

                        unavailable_label.setWordWrap(True)

                        full_text_layout.addWidget(
                            unavailable_label
                        )

                elif full_text_type == "url":

                    safe_location = html.escape(
                        location,
                        quote=True,
                    )

                    link_label = QLabel(
                        "<b>Online location:</b><br>"
                        f'<a href="{safe_location}">'
                        f"{html.escape(location)}"
                        "</a>"
                    )

                    link_label.setWordWrap(True)

                    link_label.setOpenExternalLinks(
                        True
                    )

                    link_label.setTextInteractionFlags(
                        Qt.TextBrowserInteraction
                    )

                    full_text_layout.addWidget(
                        link_label
                    )

                    open_button = QPushButton(
                        "Open Paper"
                    )

                    open_button.setObjectName(
                        "primaryButton"
                    )

                    open_button.clicked.connect(
                        lambda checked=False, url=location:
                        QDesktopServices.openUrl(
                            QUrl(url)
                        )
                    )

                    full_text_layout.addWidget(
                        open_button
                    )

                layout.addWidget(
                    full_text_group
                )

        # ====================================================
        # AUTHORS
        # ====================================================

        authors_group = QGroupBox(
            "Authors"
        )

        authors_layout = QVBoxLayout(
            authors_group
        )

        authors = (
            self.publication.get(
                "authors"
            )
            or []
        )

        if not authors:

            empty_label = QLabel(
                "No authors available."
            )

            empty_label.setObjectName(
                "muted"
            )

            authors_layout.addWidget(
                empty_label
            )

        for author in authors:

            author_label = QLabel(
                self._author_html(
                    author
                )
            )

            author_label.setWordWrap(
                True
            )

            author_label.setOpenExternalLinks(
                True
            )

            author_label.setTextInteractionFlags(
                Qt.TextBrowserInteraction
            )

            author_label.setStyleSheet(
                """
                QLabel {
                    padding: 14px;
                    background-color: #171a22;
                    border: 1px solid #292e3b;
                    border-radius: 8px;
                }

                QLabel a {
                    color: #8b84ff;
                }
                """
            )

            authors_layout.addWidget(
                author_label
            )

        layout.addWidget(
            authors_group
        )

        # ====================================================
        # ANNOTATIONS
        # ====================================================

        annotations_group = QGroupBox(
            "Annotations / Enrichments"
        )

        annotations_layout = QVBoxLayout(
            annotations_group
        )

        annotations = (
            self.publication.get(
                "annotations"
            )
            or []
        )

        if not annotations:

            empty = QLabel(
                "No annotations available."
            )

            empty.setObjectName(
                "muted"
            )

            annotations_layout.addWidget(
                empty
            )

        for annotation in annotations:

            label_text = (
                annotation.get(
                    "label"
                )
                or "-"
            )

            source = (
                annotation.get(
                    "source"
                )
                or "-"
            )

            external_id = (
                annotation.get(
                    "external_id"
                )
            )

            uri = (
                annotation.get(
                    "uri"
                )
            )

            text = (
                "<b>"
                + html.escape(
                    str(label_text)
                )
                + "</b>"
                + "<br>"
                + "Source: "
                + html.escape(
                    str(source)
                )
            )

            if external_id:

                if uri:

                    text += (
                        "<br>ID: "
                        f'<a href="{html.escape(str(uri))}">'
                        f"{html.escape(str(external_id))}"
                        "</a>"
                    )

                else:

                    text += (
                        "<br>ID: "
                        + html.escape(
                            str(
                                external_id
                            )
                        )
                    )

            annotation_label = QLabel(
                text
            )

            annotation_label.setWordWrap(
                True
            )

            annotation_label.setOpenExternalLinks(
                True
            )

            annotation_label.setTextInteractionFlags(
                Qt.TextBrowserInteraction
            )

            annotation_label.setStyleSheet(
                """
                QLabel {
                    padding: 12px;
                    background-color: #171a22;
                    border: 1px solid #292e3b;
                    border-radius: 8px;
                }

                QLabel a {
                    color: #8b84ff;
                }
                """
            )

            annotations_layout.addWidget(
                annotation_label
            )

        layout.addWidget(
            annotations_group
        )

        # ====================================================
        # PERSONAL METADATA
        # ====================================================

        user_metadata = (
            self.publication.get(
                "user_metadata"
            )
            or {}
        )

        notes = (
            user_metadata.get(
                "notes"
            )
        )

        tags = (
            user_metadata.get(
                "tags"
            )
            or []
        )

        if notes or tags:

            personal_group = QGroupBox(
                "Personal Metadata"
            )

            personal_layout = (
                QVBoxLayout(
                    personal_group
                )
            )

            if notes:

                notes_label = QLabel(
                    "<b>Notes:</b><br>"
                    + html.escape(
                        str(notes)
                    )
                )

                notes_label.setWordWrap(
                    True
                )

                personal_layout.addWidget(
                    notes_label
                )

            if tags:

                tags_label = QLabel(
                    "<b>Tags:</b> "
                    + html.escape(
                        ", ".join(
                            str(tag)
                            for tag in tags
                        )
                    )
                )

                tags_label.setWordWrap(
                    True
                )

                personal_layout.addWidget(
                    tags_label
                )

            layout.addWidget(
                personal_group
            )

        # ====================================================
        # METADATA SOURCES
        # ====================================================

        metadata_sources = (
            self.publication.get(
                "metadata_sources"
            )
            or []
        )

        if metadata_sources:

            sources_group = QGroupBox(
                "Publication Metadata Sources"
            )

            sources_layout = QVBoxLayout(
                sources_group
            )

            sources_label = QLabel(
                html.escape(
                    ", ".join(
                        str(source)
                        for source
                        in metadata_sources
                    )
                )
            )

            sources_label.setWordWrap(
                True
            )

            sources_layout.addWidget(
                sources_label
            )

            layout.addWidget(
                sources_group
            )

        # ====================================================
        # ORIGINAL CITATION
        # ====================================================

        raw_citation = (
            self.publication.get(
                "raw_citation"
            )
        )

        if raw_citation:

            raw_group = QGroupBox(
                "Original APA Citation"
            )

            raw_layout = QVBoxLayout(
                raw_group
            )

            raw_label = QLabel(
                html.escape(
                    str(raw_citation)
                )
            )

            raw_label.setWordWrap(
                True
            )

            raw_label.setTextInteractionFlags(
                Qt.TextSelectableByMouse
            )

            raw_layout.addWidget(
                raw_label
            )

            layout.addWidget(
                raw_group
            )

        layout.addStretch()

        scroll.setWidget(
            content
        )

        root_layout.addWidget(
            scroll,
            1,
        )

        # ====================================================
        # CLOSE
        # ====================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        close_button = QPushButton(
            "Close"
        )

        close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            close_button
        )

        root_layout.addLayout(
            buttons
        )

    # ========================================================
    # AUTHOR
    # ========================================================

    def _author_html(
        self,
        author,
    ):

        identifiers = (
            author.get(
                "identifiers"
            )
            or {}
        )

        name = (
            author.get(
                "resolved_name"
            )
            or author.get(
                "display_name"
            )
        )

        if not name:

            given_name = (
                author.get(
                    "given_name"
                )
                or ""
            )

            family_name = (
                author.get(
                    "family_name"
                )
                or ""
            )

            name = (
                f"{given_name} {family_name}"
                .strip()
            )

        if not name:
            name = "Unknown Author"

        text = (
            "<span style='font-size:15px;'>"
            "<b>"
            + html.escape(
                str(name)
            )
            + "</b>"
            "</span>"
        )

        # ====================================================
        # ORCID
        # ====================================================

        orcid = None

        if isinstance(
            identifiers,
            dict,
        ):
            orcid = (
                identifiers.get(
                    "orcid"
                )
            )

        orcid = (
            orcid
            or author.get(
                "orcid_id"
            )
        )

        if orcid:

            orcid = (
                str(orcid)
                .replace(
                    "https://orcid.org/",
                    "",
                )
                .strip()
            )

            orcid_url = (
                f"https://orcid.org/"
                f"{orcid}"
            )

            text += (
                "<br><br>"
                "<b>ORCID</b><br>"
                f'<a href="{html.escape(orcid_url)}">'
                f"{html.escape(orcid)}"
                "</a>"
            )

        # ====================================================
        # VIAF
        # ====================================================

        viaf = None

        if isinstance(
            identifiers,
            dict,
        ):
            viaf = (
                identifiers.get(
                    "viaf"
                )
            )

        viaf = (
            viaf
            or author.get(
                "viaf_id"
            )
        )

        if viaf:

            viaf = str(
                viaf
            ).strip()

            viaf_url = (
                f"https://viaf.org/viaf/"
                f"{viaf}"
            )

            text += (
                "<br><br>"
                "<b>VIAF</b><br>"
                f'<a href="{html.escape(viaf_url)}">'
                f"{html.escape(viaf)}"
                "</a>"
            )

        # ====================================================
        # ALTERNATIVE NAMES
        # ====================================================

        other_names = (
            self._format_values(
                author.get(
                    "other_names"
                )
            )
        )

        if other_names:

            text += (
                "<br><br>"
                "<b>Alternative names</b><br>"
                + html.escape(
                    other_names
                )
            )

        # ====================================================
        # INSTITUTIONS
        # ====================================================

        institutions = (
            self._format_values(
                author.get(
                    "institutions"
                )
            )
        )

        if institutions:

            text += (
                "<br><br>"
                "<b>Institutions</b><br>"
                + html.escape(
                    institutions
                )
            )

        # ====================================================
        # EXTERNAL IDENTIFIERS
        # ====================================================

        external_identifiers = (
            self._format_external_identifiers(
                author.get(
                    "external_identifiers"
                )
            )
        )

        if external_identifiers:

            text += (
                "<br><br>"
                "<b>Other identifiers</b><br>"
                + external_identifiers
            )

        # ====================================================
        # ENRICHMENT SOURCES
        # ====================================================

        enrichment_sources = (
            author.get(
                "enrichment_sources"
            )
            or []
        )

        if enrichment_sources:

            if isinstance(
                enrichment_sources,
                str,
            ):
                enrichment_sources = [
                    enrichment_sources
                ]

            sources = ", ".join(
                str(source).upper()
                for source
                in enrichment_sources
            )

            text += (
                "<br><br>"
                "<b>Enrichment sources</b><br>"
                + html.escape(
                    sources
                )
            )

        return text

    # ========================================================
    # FORMAT GENERIC LIST
    # ========================================================

    @staticmethod
    def _format_values(
        values,
    ):

        if not values:
            return None

        if isinstance(
            values,
            str,
        ):
            return values

        if isinstance(
            values,
            dict,
        ):
            values = [
                values
            ]

        if not isinstance(
            values,
            list,
        ):
            return str(values)

        result = []

        for value in values:

            if isinstance(
                value,
                str,
            ):

                if value.strip():
                    result.append(
                        value.strip()
                    )

                continue

            if isinstance(
                value,
                dict,
            ):

                name = (
                    value.get(
                        "name"
                    )
                    or value.get(
                        "organization_name"
                    )
                    or value.get(
                        "organization-name"
                    )
                    or value.get(
                        "label"
                    )
                    or value.get(
                        "value"
                    )
                )

                if name:

                    result.append(
                        str(name)
                    )

        if not result:
            return None

        # Remove duplicate values,
        # but preserve original order.
        result = list(
            dict.fromkeys(
                result
            )
        )

        return ", ".join(
            result
        )

    # ========================================================
    # FORMAT EXTERNAL IDS
    # ========================================================

    @staticmethod
    def _format_external_identifiers(
        identifiers,
    ):

        if not identifiers:
            return None

        result = []

        if isinstance(
            identifiers,
            dict,
        ):

            for (
                key,
                value,
            ) in identifiers.items():

                if not value:
                    continue

                if isinstance(
                    value,
                    (
                        dict,
                        list,
                    ),
                ):
                    continue

                result.append(
                    "<b>"
                    + html.escape(
                        str(key)
                    )
                    + ":</b> "
                    + html.escape(
                        str(value)
                    )
                )

        elif isinstance(
            identifiers,
            list,
        ):

            for identifier in identifiers:

                if isinstance(
                    identifier,
                    str,
                ):

                    result.append(
                        html.escape(
                            identifier
                        )
                    )

                    continue

                if not isinstance(
                    identifier,
                    dict,
                ):
                    continue

                identifier_type = (
                    identifier.get(
                        "type"
                    )
                    or identifier.get(
                        "external_id_type"
                    )
                    or identifier.get(
                        "external-id-type"
                    )
                    or identifier.get(
                        "name"
                    )
                    or "ID"
                )

                identifier_value = (
                    identifier.get(
                        "value"
                    )
                    or identifier.get(
                        "external_id_value"
                    )
                    or identifier.get(
                        "external-id-value"
                    )
                    or identifier.get(
                        "id"
                    )
                )

                if not identifier_value:
                    continue

                result.append(
                    "<b>"
                    + html.escape(
                        str(
                            identifier_type
                        )
                    )
                    + ":</b> "
                    + html.escape(
                        str(
                            identifier_value
                        )
                    )
                )

        if not result:
            return None

        return "<br>".join(
            result
        )