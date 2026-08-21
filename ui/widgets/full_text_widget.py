from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QRadioButton, QButtonGroup, QFileDialog

class FullTextWidget(QWidget):

    # Initialize the full-paper selector and load an existing value when provided.
    def __init__(self, full_text=None, parent=None):
        super().__init__(parent)
        self._build_ui()
        if full_text:
            self.set_value(full_text)

    # Build the controls for no paper, a local file or an online link.
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        type_layout = QHBoxLayout()
        self.none_radio = QRadioButton('None')
        self.local_radio = QRadioButton('Local PDF')
        self.url_radio = QRadioButton('Online link')
        self.type_group = QButtonGroup(self)
        self.type_group.setExclusive(True)
        self.type_group.addButton(self.none_radio)
        self.type_group.addButton(self.local_radio)
        self.type_group.addButton(self.url_radio)
        self.none_radio.setChecked(True)
        type_layout.addWidget(self.none_radio)
        type_layout.addWidget(self.local_radio)
        type_layout.addWidget(self.url_radio)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        self.local_container = QWidget()
        local_layout = QHBoxLayout(self.local_container)
        local_layout.setContentsMargins(0, 0, 0, 0)
        self.local_edit = QLineEdit()
        self.local_edit.setPlaceholderText('No local PDF selected')
        self.local_edit.setReadOnly(True)
        self.browse_button = QPushButton('Choose PDF')
        self.browse_button.setCursor(Qt.PointingHandCursor)
        self.browse_button.clicked.connect(self.choose_local_file)
        local_layout.addWidget(self.local_edit, 1)
        local_layout.addWidget(self.browse_button)
        layout.addWidget(self.local_container)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText('https://drive.google.com/... or another online location')
        layout.addWidget(self.url_edit)
        self.none_radio.toggled.connect(self._update_state)
        self.local_radio.toggled.connect(self._update_state)
        self.url_radio.toggled.connect(self._update_state)
        self._update_state()

    # Show only the input that matches the selected paper location type.
    def _update_state(self):
        self.local_container.setVisible(self.local_radio.isChecked())
        self.url_edit.setVisible(self.url_radio.isChecked())

    # Open a file dialog and store the selected PDF path.
    def choose_local_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Paper PDF', '', 'PDF Files (*.pdf);;All Files (*)')
        if not file_path:
            return
        self.local_edit.setText(file_path)
        self.local_radio.setChecked(True)

    # Return the selected full-paper location in storage format.
    def value(self):
        if self.local_radio.isChecked():
            location = self.local_edit.text().strip()
            if not location:
                return None
            return {'type': 'local', 'location': location}
        if self.url_radio.isChecked():
            location = self.url_edit.text().strip()
            if not location:
                return None
            return {'type': 'url', 'location': location}
        return None

    # Load a stored full-paper location into the widget.
    def set_value(self, full_text):
        self.local_edit.clear()
        self.url_edit.clear()
        if not isinstance(full_text, dict):
            self.none_radio.setChecked(True)
            self._update_state()
            return
        full_text_type = full_text.get('type') or ''
        location = full_text.get('location') or ''
        if full_text_type == 'local':
            self.local_edit.setText(str(location))
            self.local_radio.setChecked(True)
        elif full_text_type == 'url':
            self.url_edit.setText(str(location))
            self.url_radio.setChecked(True)
        else:
            self.none_radio.setChecked(True)
        self._update_state()

    # Reset the widget to no selected full paper.
    def clear(self):
        self.local_edit.clear()
        self.url_edit.clear()
        self.none_radio.setChecked(True)
        self._update_state()
