import sys
from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.theme import APP_STYLE

# Start the Qt application and manage login, logout and the main window.
def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Bibliographic Collections')
    app.setStyle('Fusion')
    app.setStyleSheet(APP_STYLE)
    windows = {}

    # Create the login window if one is not already open.
    def show_login():
        existing_login = windows.get('login')
        if existing_login:
            existing_login.show()
            existing_login.raise_()
            existing_login.activateWindow()
            return
        login_window = LoginWindow()
        windows['login'] = login_window
        login_window.login_successful.connect(open_main_window)
        login_window.show()

    # Open the main application window after a successful login.
    def open_main_window(user):
        login_window = windows.get('login')
        main_window = MainWindow(user=user)
        windows['main'] = main_window
        main_window.logout_requested.connect(logout)
        main_window.show()
        if login_window:
            login_window.close()
            windows.pop('login', None)

    # Close the main window and return to the login screen.
    def logout():
        main_window = windows.get('main')
        show_login()
        if main_window:
            main_window.close()
            windows.pop('main', None)
    show_login()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
