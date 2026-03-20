DARK_THEME = """
    QMainWindow, QDialog {
        background-color: #0f1117;
        color: #ffffff;
    }

    QWidget {
        color: #ffffff;
    }

    QLabel {
        color: #ffffff;
    }
    
    QLabel#TitleLabel {
        font-size: 32px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }

    QLabel#SubtitleLabel {
        font-size: 16px;
        color: #8b8fa8;
        margin-bottom: 30px;
    }

    QPushButton {
        background-color: #2a2d3e;
        color: white;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
        border: 1px solid #3b4054;
    }

    QPushButton:hover {
        background-color: #3b4054;
    }

    QPushButton#PrimaryButton {
        background-color: #4f6ef7;
        border: none;
    }

    QPushButton#PrimaryButton:hover {
        background-color: #3f58c6;
    }

    QPushButton#DangerButton {
        background-color: #e74c3c;
        border: none;
    }

    QPushButton#DangerButton:hover {
        background-color: #c0392b;
    }

    QComboBox, QLineEdit, QSpinBox, QTimeEdit {
        padding: 8px;
        border: 1px solid #2a2d3e;
        border-radius: 4px;
        background-color: #1a1d27;
        color: white;
        font-size: 14px;
    }
    
    QComboBox:drop-down {
        border-left: 1px solid #2a2d3e;
    }

    QTableWidget {
        border: 1px solid #2a2d3e;
        background-color: #1a1d27;
        gridline-color: #2a2d3e;
        color: white;
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
        background-color: #1a1d27;
        border: 1px solid #2a2d3e;
        border-radius: 8px;
        padding: 20px;
    }

    QFrame#Card:hover {
        border: 1px solid #4f6ef7;
    }

    QTabWidget::pane {
        border: 1px solid #2a2d3e;
        background-color: #1a1d27;
        border-radius: 4px;
    }

    QTabBar::tab {
        background: #1a1d27;
        color: #8b8fa8;
        padding: 10px 20px;
        border: 1px solid #2a2d3e;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }

    QTabBar::tab:selected {
        background: #4f6ef7;
        color: white;
    }

    QProgressBar {
        border: 1px solid #2a2d3e;
        border-radius: 4px;
        text-align: center;
        background-color: #1a1d27;
        color: white;
    }

    QProgressBar::chunk {
        background-color: #4f6ef7;
        border-radius: 3px;
    }

    QComboBox QAbstractItemView {
        background-color: #1a1d27;
        color: #ffffff;
        selection-background-color: #4f6ef7;
        selection-color: #ffffff;
        border: 1px solid #2a2d3e;
    }

    QComboBox {
        color: #ffffff;
        background-color: #1a1d27;
    }

    QListWidget {
        color: #ffffff;
        background-color: #1a1d27;
        border: 1px solid #2a2d3e;
        outline: none;
    }

    QListWidget::item {
        color: #ffffff;
        padding: 5px;
    }

    QListWidget::item:selected {
        background-color: #4f6ef7;
        color: #ffffff;
    }

    QGroupBox {
        background-color: #1a1d27;
        color: #ffffff;
        border: 1px solid #2a2d3e;
        border-radius: 6px;
        margin-top: 15px;
        padding-top: 15px;
        font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: #ffffff;
        left: 10px;
    }

    QScrollArea {
        border: none;
        background-color: transparent;
    }

    QScrollBar:vertical {
        border: none;
        background: #0f1117;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }

    QScrollBar::handle:vertical {
        background: #2a2d3e;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
"""

LIGHT_THEME = """
    /* Placeholder for future light theme, keeping default fallback */
"""
