from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget
from ui.pages.publications_page import PublicationsPage
from ui.pages.new_publication_page import NewPublicationPage
from ui.widgets.user_profile import UserProfileWidget

class MainWindow(QMainWindow):
    logout_requested = Signal()

    # Initialize the main application window for the signed-in user.
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle('Bibliographic Collections')
        self.resize(1280, 800)
        self.setMinimumSize(1000, 650)
        self._build_ui()

    # Build the sidebar, profile area and page stack.
    def _build_ui(self):
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        sidebar = QWidget()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(245)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 18)
        sidebar_layout.setSpacing(8)
        app_title = QLabel('Bibliographic\nCollections')
        app_title.setObjectName('appTitle')
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacing(22)
        self.publications_button = self._nav_button('Publications')
        self.new_button = self._nav_button('New Publication')
        self.publications_button.setCursor(Qt.PointingHandCursor)
        self.new_button.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.publications_button)
        sidebar_layout.addWidget(self.new_button)
        sidebar_layout.addStretch()
        self.user_profile = UserProfileWidget(self.user)
        self.user_profile.logout_requested.connect(self.logout_requested.emit)
        sidebar_layout.addWidget(self.user_profile)
        self.pages = QStackedWidget()
        self.publications_page = PublicationsPage(self.user)
        self.new_page = NewPublicationPage(self.user)
        self.pages.addWidget(self.publications_page)
        self.pages.addWidget(self.new_page)
        self.publications_button.clicked.connect(self.show_publications)
        self.new_button.clicked.connect(self.show_new_publication)
        self.new_page.publication_saved.connect(self.publication_saved)
        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)
        self.show_publications()

    # Create one navigation button and connect its action.
    def _nav_button(self, text):
        button = QPushButton(text)
        button.setObjectName('navButton')
        button.setCheckable(True)
        return button

    # Mark only the active navigation button as selected.
    def _select_button(self, selected):
        self.publications_button.setChecked(selected is self.publications_button)
        self.new_button.setChecked(selected is self.new_button)

    # Show the publication library and refresh its contents.
    def show_publications(self):
        self.publications_page.load_publications()
        self.pages.setCurrentWidget(self.publications_page)
        self._select_button(self.publications_button)

    # Show the form used to add a publication.
    def show_new_publication(self):
        self.pages.setCurrentWidget(self.new_page)
        self._select_button(self.new_button)

    # Return to the library after a publication is saved.
    def publication_saved(self):
        self.publications_page.load_publications()
        self.pages.setCurrentWidget(self.publications_page)
        self._select_button(self.publications_button)
