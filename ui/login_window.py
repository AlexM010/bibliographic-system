from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    Qt,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)

from auth.firebase_auth import (
    FirebaseAuthService,
    FirebaseAuthError,
)


# ============================================================
# LOGIN WORKER
# ============================================================

class LoginWorker(QObject):

    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def run(self):

        try:

            user = (
                FirebaseAuthService()
                .login()
            )

            self.success.emit(
                user
            )

        except FirebaseAuthError as error:

            self.error.emit(
                str(error)
            )

        except Exception as error:

            self.error.emit(
                str(error)
            )

        finally:

            # IMPORTANT:
            # tells QThread that the worker
            # has completely finished.
            self.finished.emit()


# ============================================================
# LOGIN WINDOW
# ============================================================

class LoginWindow(QWidget):

    login_successful = Signal(object)

    def __init__(
        self,
    ):
        super().__init__()

        self.thread = None
        self.worker = None

        self.pending_user = None
        self.pending_error = None

        self.login_in_progress = False

        self.setWindowTitle(
            "Bibliographic Collections"
        )

        self.resize(
            520,
            440,
        )

        self.setMinimumSize(
            460,
            400,
        )

        self._build_ui()

    # ========================================================
    # UI
    # ========================================================

    def _build_ui(
        self,
    ):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            70,
            45,
            70,
            30,
        )

        layout.setSpacing(
            14
        )

        # ====================================================
        # CENTER
        # ====================================================

        layout.addStretch(
            2
        )

        title = QLabel(
            "Bibliographic Collections"
        )

        title.setObjectName(
            "loginTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Manage and enrich your academic publications."
        )

        subtitle.setObjectName(
            "loginSubtitle"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle.setWordWrap(
            True
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            22
        )

        # ====================================================
        # GOOGLE LOGIN BUTTON
        # ====================================================

        self.login_button = QPushButton(
            "Continue with Google"
        )

        self.login_button.setObjectName(
            "googleLoginButton"
        )

        self.login_button.setCursor(
            Qt.PointingHandCursor
        )

        self.login_button.clicked.connect(
            self.start_login
        )

        layout.addWidget(
            self.login_button
        )

        # ====================================================
        # STATUS
        # ====================================================

        self.status_label = QLabel(
            ""
        )

        self.status_label.setObjectName(
            "loginStatus"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        self.status_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.status_label
        )

        layout.addStretch(
            2
        )

        # ====================================================
        # THESIS INFORMATION
        # ====================================================

        copyright_label = QLabel(
            "Bachelor’s Thesis\n"
            "Student: Alexandros Markodimitrakis · csd4337\n"
            "Supervisor: Xenophon Zabulis\n"
            "Computer Science Department, University of Crete\n"
            "© 2026"
        )

        copyright_label.setObjectName(
            "copyrightLabel"
        )

        copyright_label.setAlignment(
            Qt.AlignCenter
        )

        copyright_label.setWordWrap(
            True
        )

        layout.addWidget(
            copyright_label
        )

    # ========================================================
    # START LOGIN
    # ========================================================

    def start_login(
        self,
    ):

        # Prevent double login
        if self.login_in_progress:
            return

        self.login_in_progress = True

        self.pending_user = None
        self.pending_error = None

        self.login_button.setEnabled(
            False
        )

        self.login_button.setText(
            "Signing in..."
        )

        self.status_label.setText(
            "Complete sign in in your browser."
        )

        # ====================================================
        # THREAD
        # ====================================================

        self.thread = QThread(
            self
        )

        self.worker = LoginWorker()

        self.worker.moveToThread(
            self.thread
        )

        # Start worker
        self.thread.started.connect(
            self.worker.run
        )

        # Worker result
        self.worker.success.connect(
            self._worker_success
        )

        self.worker.error.connect(
            self._worker_error
        )

        # IMPORTANT:
        # worker finishes first,
        # THEN thread quits.
        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        # We do not open MainWindow
        # until QThread is completely stopped.
        self.thread.finished.connect(
            self._thread_finished
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.start()

    # ========================================================
    # WORKER SUCCESS
    # ========================================================

    def _worker_success(
        self,
        user,
    ):

        # Do NOT emit login_successful here.
        #
        # At this point the QThread may still
        # technically be running.
        self.pending_user = user

    # ========================================================
    # WORKER ERROR
    # ========================================================

    def _worker_error(
        self,
        error,
    ):

        self.pending_error = error

    # ========================================================
    # THREAD COMPLETELY FINISHED
    # ========================================================

    def _thread_finished(
        self,
    ):

        user = self.pending_user
        error = self.pending_error

        self.worker = None
        self.thread = None

        self.login_in_progress = False

        # ====================================================
        # SUCCESS
        # ====================================================

        if user is not None:

            self.status_label.setText(
                "Signed in successfully."
            )

            self.login_button.setText(
                "Signed in"
            )

            # NOW it is safe for main_gui.py
            # to close LoginWindow.
            self.login_successful.emit(
                user
            )

            return

        # ====================================================
        # ERROR
        # ====================================================

        self.login_button.setEnabled(
            True
        )

        self.login_button.setText(
            "Continue with Google"
        )

        if error:

            self.status_label.setText(
                f"Login failed:\n{error}"
            )

        else:

            self.status_label.setText(
                "Login was not completed."
            )

    # ========================================================
    # WINDOW CLOSE
    # ========================================================

    def closeEvent(
        self,
        event,
    ):

        # Do not allow the LoginWindow to be destroyed
        # while the Google authentication worker is
        # still running.
        if (
            self.thread is not None
            and self.thread.isRunning()
        ):

            event.ignore()

            self.status_label.setText(
                "Please complete the Google sign in first."
            )

            return

        event.accept()