from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class DashboardScreen(QWidget):
    def __init__(self, switch_cb):
        super().__init__()
        self.switch_cb = switch_cb
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Welcome to ScheduleForge")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)

        subtext = QLabel("Smart timetable scheduling for everyone")
        subtext.setObjectName("SubtitleLabel")
        subtext.setAlignment(Qt.AlignCenter)

        btn_start = QPushButton("Make a Timetable →")
        btn_start.setObjectName("PrimaryButton")
        btn_start.setFixedSize(250, 50)
        btn_start.clicked.connect(lambda: self.switch_cb(1)) # Index 1 is mode selector

        footer = QLabel("v2.0.0 | March 2026")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #8b8fa8; margin-top: 50px;")

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtext)
        layout.addSpacing(20)
        layout.addWidget(btn_start, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(footer)
