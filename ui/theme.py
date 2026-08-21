APP_STYLE = """

/* Global */

QWidget {
    font-family: "Segoe UI", "Inter", Arial;
    font-size: 14px;

    color: #e6e8ee;
    background-color: #0f1117;
}

QMainWindow {
    background-color: #0f1117;
}

QDialog {
    background-color: #0f1117;
}

QWidget#pageContent {
    background-color: #0f1117;
}


/* Sidebar */

QWidget#sidebar {
    background-color: #151821;
    border-right: 1px solid #272b38;
}


/* Labels */

QLabel {
    background-color: transparent;
    color: #e6e8ee;
}

QLabel#appTitle {
    font-size: 21px;
    font-weight: 700;
    color: #ffffff;
    padding: 4px 2px;
}

QLabel#pageTitle {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    background-color: transparent;
}

QLabel#sectionTitle {
    font-size: 17px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#muted {
    color: #9ca3b4;
    font-size: 12px;
}


/* Publication Card */

QFrame#publicationCard {
    background-color: #151821;

    border: 1px solid #292e3b;

    border-radius: 10px;
}

QFrame#publicationCard:hover {
    border-color: #3d4354;
}

QLabel#publicationCardTitle {
    font-size: 15px;

    font-weight: 600;

    color: #ffffff;
}


/* Buttons */

QPushButton {
    min-height: 38px;

    padding-left: 16px;
    padding-right: 16px;

    border-radius: 8px;

    border: 1px solid #303545;

    background-color: #1b1f29;

    color: #e7eaf0;

    font-weight: 500;
}

QPushButton:hover {
    background-color: #242936;

    border-color: #454c60;
}

QPushButton:pressed {
    background-color: #161a22;
}

QPushButton:disabled {
    background-color: #151820;

    border-color: #242835;

    color: #616777;
}


/* Primary Button */

QPushButton#primaryButton {
    background-color: #635bff;

    border: 1px solid #635bff;

    color: #ffffff;

    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #746dff;

    border-color: #746dff;
}

QPushButton#primaryButton:pressed {
    background-color: #5149db;
}


/* Delete / Danger */

QPushButton#dangerButton {
    background-color: transparent;

    color: #ff7474;

    border: 1px solid #543034;
}

QPushButton#dangerButton:hover {
    background-color: #321e22;

    border-color: #8b4148;

    color: #ff9090;
}

QPushButton#dangerButton:pressed {
    background-color: #28181b;
}


/* Sidebar Navigation */

QPushButton#navButton {
    min-height: 44px;

    text-align: left;

    padding-left: 16px;

    border: none;

    background-color: transparent;

    color: #c7cad3;

    font-weight: 500;
}

QPushButton#navButton:hover {
    background-color: #1d2230;

    color: #ffffff;
}

QPushButton#navButton:checked {
    background-color: #292d40;

    color: #ffffff;

    font-weight: 600;
}


/* Inputs */

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox {
    background-color: #171a22;

    color: #f0f1f5;

    border: 1px solid #343949;

    border-radius: 8px;

    padding: 9px;
}

QLineEdit:hover,
QTextEdit:hover,
QPlainTextEdit:hover,
QComboBox:hover {
    border-color: #464c60;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus {
    border: 1px solid #6c63ff;
}


/* Group Boxes */

QGroupBox {
    background-color: #151821;

    border: 1px solid #292e3b;

    border-radius: 12px;

    margin-top: 15px;

    padding-top: 18px;

    font-weight: 600;

    color: #f3f4f7;
}

QGroupBox::title {
    subcontrol-origin: margin;

    subcontrol-position: top left;

    left: 14px;

    padding: 3px 8px;

    border-radius: 5px;

    background-color: #151821;

    color: #ffffff;

    font-weight: 600;
}


/* Checkboxes */

QCheckBox {
    min-height: 38px;

    padding: 8px 12px;

    spacing: 10px;

    background-color: #181b24;

    border: 1px solid #2d3241;

    border-radius: 9px;

    color: #cfd2dc;
}

QCheckBox:hover {
    background-color: #202431;

    border-color: #43495c;
}

QCheckBox:checked {
    background-color: #28264a;

    border: 1px solid #6c63ff;

    color: #ffffff;

    font-weight: 600;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}


/* Lists */

QListWidget {
    background-color: #12151c;

    border: 1px solid #292e3b;

    border-radius: 10px;

    padding: 6px;

    outline: none;
}

QListWidget::item {
    background-color: transparent;

    border-radius: 7px;

    padding: 6px;

    color: #e6e8ee;
}

QListWidget::item:hover {
    background-color: #1c202b;
}

QListWidget::item:selected {
    background-color: #302c5a;

    color: #ffffff;

    border: 1px solid #6c63ff;
}


/* Scroll Area */

QScrollArea {
    background-color: #0f1117;

    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: #0f1117;
}


/* Scrollbar */

QScrollBar:vertical {
    background-color: #11141b;

    width: 10px;

    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: #383d4d;

    min-height: 30px;

    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #51576a;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}


/* Login */

QLabel#loginTitle {
    color: #ffffff;

    font-size: 25px;

    font-weight: 700;

    background-color: transparent;
}

QLabel#loginSubtitle {
    color: #8f95a5;

    font-size: 13px;

    background-color: transparent;
}

QLabel#loginStatus {
    color: #8f95a5;

    font-size: 12px;

    background-color: transparent;
}

QPushButton#googleLoginButton {
    min-height: 46px;

    background-color: #ffffff;

    color: #17191f;

    border: none;

    border-radius: 9px;

    padding-left: 20px;
    padding-right: 20px;

    font-size: 14px;

    font-weight: 600;
}

QPushButton#googleLoginButton:hover {
    background-color: #ededf1;
}

QPushButton#googleLoginButton:pressed {
    background-color: #dedee3;
}

QPushButton#googleLoginButton:disabled {
    background-color: #272b35;

    color: #777d8c;
}
QPushButton#logoutButton {
    background-color: transparent;
    border: 1px solid #343949;
    color: #9ca3b4;
}

QPushButton#logoutButton:hover {
    background-color: #321e22;
    border-color: #8b4148;
    color: #ff7474;
}

/* Copyright */

QLabel#copyrightLabel {
    background-color: transparent;

    color: #686e7d;

    font-size: 10px;

    font-weight: 400;
}


/* Tooltip */

QToolTip {
    background-color: #222631;

    color: #ffffff;

    border: 1px solid #3b4152;

    padding: 6px;
}

"""