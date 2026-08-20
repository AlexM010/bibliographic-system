import sys

from PySide6.QtWidgets import (
    QApplication,
)

from ui.login_window import (
    LoginWindow,
)

from ui.main_window import (
    MainWindow,
)

from ui.theme import (
    APP_STYLE,
)


def main():

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "Bibliographic Collections"
    )

    app.setStyle(
        "Fusion"
    )

    app.setStyleSheet(
        APP_STYLE
    )

    # Keep references to windows so that
    # Python's garbage collector does not
    # destroy them.
    windows = {}

    # ==============================================
    # SHOW LOGIN
    # ==============================================

    def show_login():

        # Avoid creating a second login window.
        existing_login = windows.get(
            "login"
        )

        if existing_login:

            existing_login.show()
            existing_login.raise_()
            existing_login.activateWindow()

            return

        login_window = LoginWindow()

        windows["login"] = (
            login_window
        )

        login_window.login_successful.connect(
            open_main_window
        )

        login_window.show()

    # ==============================================
    # OPEN MAIN WINDOW
    # ==============================================

    def open_main_window(
        user,
    ):

        login_window = windows.get(
            "login"
        )

        main_window = MainWindow(
            user=user
        )

        windows["main"] = (
            main_window
        )

        main_window.logout_requested.connect(
            logout
        )

        # IMPORTANT:
        # show MainWindow BEFORE closing login.
        main_window.show()

        if login_window:

            login_window.close()

            windows.pop(
                "login",
                None,
            )

    # ==============================================
    # LOGOUT
    # ==============================================

    def logout():

        main_window = windows.get(
            "main"
        )

        # IMPORTANT:
        # Open login FIRST.
        #
        # If MainWindow is closed before another
        # window exists, Qt may interpret that as
        # the application's last window closing
        # and terminate the application.
        show_login()

        if main_window:

            main_window.close()

            windows.pop(
                "main",
                None,
            )

    # ==============================================
    # START
    # ==============================================

    show_login()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()