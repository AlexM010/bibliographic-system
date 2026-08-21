from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton

class CandidateDialog(QDialog):

    # Build a dialog that displays candidates and lets the user select one.
    def __init__(self, title, candidates, formatter, parent=None):
        super().__init__(parent)
        self.candidates = candidates
        self.selected_candidate = None
        self.setWindowTitle(title)
        self.resize(620, 460)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(12)
        heading = QLabel(title)
        heading.setObjectName('pageTitle')
        heading.setWordWrap(True)
        layout.addWidget(heading)
        info = QLabel('Select the result that matches the publication.')
        info.setObjectName('muted')
        layout.addWidget(info)
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(6)
        self.list_widget.setAlternatingRowColors(False)
        for candidate in candidates:
            item = QListWidgetItem(formatter(candidate))
            item.setSizeHint(QSize(100, 64))
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget, 1)
        buttons = QHBoxLayout()
        buttons.addStretch()
        skip_button = QPushButton('Skip')
        self.select_button = QPushButton('Select')
        self.select_button.setObjectName('primaryButton')
        self.select_button.setEnabled(False)
        buttons.addWidget(skip_button)
        buttons.addWidget(self.select_button)
        layout.addLayout(buttons)
        skip_button.clicked.connect(self.reject)
        self.select_button.clicked.connect(self.accept_selection)
        self.list_widget.currentRowChanged.connect(self.on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)

    # Enable selection only after the user chooses a candidate.
    def on_selection_changed(self, row):
        self.select_button.setEnabled(row >= 0)

    # Store the selected candidate and close the dialog.
    def accept_selection(self, *_):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        if row >= len(self.candidates):
            return
        self.selected_candidate = self.candidates[row]
        self.accept()

    @classmethod
    # Open the dialog and return the selected candidate, if any.
    def choose(cls, parent, title, candidates, formatter):
        if not candidates:
            return None
        dialog = cls(title=title, candidates=candidates, formatter=formatter, parent=parent)
        result = dialog.exec()
        if result != QDialog.Accepted:
            return None
        return dialog.selected_candidate
