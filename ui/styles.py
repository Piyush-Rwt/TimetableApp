"""
Style Definitions - styles.py
This file contains QSS (Qt StyleSheet) theme definitions for the application.
QSS is similar to CSS but used by PySide6/PyQt for styling GUI elements.

Themes:
- LIGHT_THEME: Light mode stylesheet

Key Components Styled:
- Buttons: Primary (blue), Danger (red), default (dark gray)
- Input Fields: Text boxes, dropdowns, spin boxes with light backgrounds
- Tables: Data tables with blue headers
- Cards: Container frames with hover effects
- Tabs: Tab navigation with active state highlighting
- Lists: Scrollable lists with selection styling
"""

"""
Style Definitions - styles.py
This file contains QSS (Qt StyleSheet) theme definitions for the application.
QSS is similar to CSS but used by PySide6/PyQt for styling GUI elements.

Themes:
- LIGHT_THEME: Light mode stylesheet

Key Components Styled:
- Buttons: Primary (blue), Danger (red), default (dark gray)
- Input Fields: Text boxes, dropdowns, spin boxes with light backgrounds
- Tables: Data tables with blue headers
- Cards: Container frames with hover effects
- Tabs: Tab navigation with active state highlighting
- Lists: Scrollable lists with selection styling
"""

LIGHT_THEME = """
    QMainWindow, QDialog, QWidget {
        background-color: #f5f6fa;
        color: #2f3640;
    }

    QLabel {
        color: #2f3640;
    }
    
    QLabel#TitleLabel {
        font-size: 32px;
        font-weight: bold;
        color: #2f3640;
        margin-bottom: 10px;
    }

    QLabel#SubtitleLabel {
        font-size: 16px;
        color: #7f8c8d;
        margin-bottom: 30px;
    }

    QPushButton {
        background-color: #dcdde1;
        color: #2f3640;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
        border: 1px solid #bdc3c7;
    }

    QPushButton:hover {
        background-color: #bdc3c7;
    }

    QPushButton#PrimaryButton {
        background-color: #4f6ef7;
        color: white;
        border: none;
    }

    QPushButton#PrimaryButton:hover {
        background-color: #3f58c6;
    }

    QComboBox, QLineEdit, QSpinBox, QTimeEdit {
        padding: 8px;
        border: 1px solid #dcdde1;
        border-radius: 4px;
        background-color: #ffffff;
        color: #2f3640;
        font-size: 14px;
    }

    QSpinBox::up-button, QSpinBox::down-button,
    QTimeEdit::up-button, QTimeEdit::down-button {
        width: 20px;
        height: 15px;
        border: 1px solid #dcdde1;
        background-color: #e8f4f8;
    }

    QSpinBox::up-button:hover, QSpinBox::down-button:hover,
    QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
        background-color: #4f9fbb;
    }
    }

    QTableWidget {
        border: 1px solid #dcdde1;
        background-color: #ffffff;
        gridline-color: #f1f2f6;
        color: #2f3640;
        font-size: 13px;
    }

    QHeaderView::section {
        background-color: #4f6ef7;
        color: white;
        font-weight: bold;
        padding: 6px;
        border: 1px solid #3f58c6;
    }
    
    QFrame#Card {
        background-color: #ffffff;
        border: 1px solid #dcdde1;
        border-radius: 8px;
        padding: 20px;
    }

    QFrame#Card:hover {
        border: 1px solid #4f6ef7;
    }

    QTabWidget::pane {
        border: 1px solid #dcdde1;
        background-color: #ffffff;
        border-radius: 4px;
    }

    QTabBar::tab {
        background: #f1f2f6;
        color: #7f8c8d;
        padding: 10px 20px;
        border: 1px solid #dcdde1;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }

    QTabBar::tab:selected {
        background: #4f6ef7;
        color: white;
    }

    QProgressBar {
        border: 1px solid #dcdde1;
        border-radius: 4px;
        text-align: center;
        background-color: #f1f2f6;
        color: #2f3640;
    }

    QProgressBar::chunk {
        background-color: #4f6ef7;
        border-radius: 3px;
    }

    QListWidget {
        color: #2f3640;
        background-color: #ffffff;
        border: 1px solid #dcdde1;
        outline: none;
    }

    QListWidget::item {
        padding: 5px;
    }

    QListWidget::item:selected {
        background-color: #4f6ef7;
        color: #ffffff;
    }

    QGroupBox {
        background-color: #ffffff;
        color: #2f3640;
        border: 1px solid #dcdde1;
        border-radius: 6px;
        margin-top: 15px;
        padding-top: 15px;
        font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: #2f3640;
        left: 10px;
    }

    QScrollArea {
        border: none;
        background-color: transparent;
    }

    QScrollBar:vertical {
        border: none;
        background: #f5f6fa;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }

    QScrollBar::handle:vertical {
        background: #dcdde1;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
"""
