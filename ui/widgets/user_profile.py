from PySide6.QtCore import Qt, QSize, QUrl, Signal
from PySide6.QtGui import QPainter, QPainterPath, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton

class AvatarWidget(QWidget):

    # Initialize the circular avatar widget.
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name or 'U'
        self.pixmap = None
        self.setFixedSize(44, 44)

    # Return the preferred avatar size.
    def sizeHint(self):
        return QSize(44, 44)

    # Store a profile image and repaint the avatar.
    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.update()

    # Draw the profile image inside a circular clip.
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addEllipse(rect)
        painter.setClipPath(path)
        if self.pixmap:
            scaled = self.pixmap.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect, scaled)
        else:
            painter.fillRect(rect, Qt.darkGray)
            painter.setPen(Qt.white)
            font = painter.font()
            font.setBold(True)
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignCenter, self.name[0].upper())

class UserProfileWidget(QWidget):
    logout_requested = Signal()

    # Build the signed-in user profile and logout controls.
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        name = getattr(user, 'display_name', None) or getattr(user, 'email', None) or 'User'
        email = getattr(user, 'email', None) or ''
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(4, 8, 4, 8)
        root_layout.setSpacing(10)
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(10)
        self.avatar = AvatarWidget(name)
        profile_layout.addWidget(self.avatar)
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        name_label = QLabel(name)
        name_label.setStyleSheet('\n            QLabel {\n                font-weight: 600;\n                color: white;\n                background: transparent;\n            }\n            ')
        email_label = QLabel(email)
        email_label.setObjectName('muted')
        email_label.setWordWrap(True)
        text_layout.addWidget(name_label)
        text_layout.addWidget(email_label)
        profile_layout.addLayout(text_layout, 1)
        root_layout.addLayout(profile_layout)
        self.logout_button = QPushButton('Logout')
        self.logout_button.setObjectName('logoutButton')
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.clicked.connect(self.logout_requested.emit)
        root_layout.addWidget(self.logout_button)
        self.network = QNetworkAccessManager(self)
        photo_url = getattr(user, 'photo_url', None)
        if photo_url:
            self._load_photo(photo_url)

    # Download the Google profile photo asynchronously.
    def _load_photo(self, url):
        request = QNetworkRequest(QUrl(url))
        reply = self.network.get(request)
        reply.finished.connect(lambda: self._photo_loaded(reply))

    # Apply the downloaded profile image when the request succeeds.
    def _photo_loaded(self, reply):
        if reply.error():
            reply.deleteLater()
            return
        data = reply.readAll()
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            self.avatar.set_pixmap(pixmap)
        reply.deleteLater()
