from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QDialog
from PySide6.QtCore import Qt

class ModeCard(QFrame):
    def __init__(self, icon, title, desc, on_click):
        super().__init__()
        self.setObjectName("Card")
        self.setFixedSize(300, 350)
        self.setCursor(Qt.PointingHandCursor)
        self.on_click = on_click
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 64px;")
        lbl_icon.setAlignment(Qt.AlignCenter)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("TitleLabel")
        lbl_title.setStyleSheet("font-size: 24px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet("color: #8b8fa8;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(lbl_icon)
        layout.addSpacing(20)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.on_click()

class ModeSelectorScreen(QWidget):
    def __init__(self, switch_cb):
        super().__init__()
        self.switch_cb = switch_cb
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(lambda: switch_cb(0)) # Index 0 is dashboard
        header.addWidget(btn_back)
        header.addStretch()
        layout.addLayout(header)
        
        title = QLabel("Select Scheduling Mode")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(40)
        
        # Cards
        cards_layout = QHBoxLayout()
        cards_layout.setAlignment(Qt.AlignCenter)
        
        card_personal = ModeCard("🧑", "Personal", "Daily routines, habits, study plans, personal goals", lambda: switch_cb(2))
        card_business = ModeCard("💼", "Business", "Team rosters, shift scheduling, meeting blocks", lambda: switch_cb(3))
        card_education = ModeCard("🎓", "Education", "University & school timetable generation", self.start_education_mode)
        
        cards_layout.addWidget(card_personal)
        cards_layout.addSpacing(30)
        cards_layout.addWidget(card_business)
        cards_layout.addSpacing(30)
        cards_layout.addWidget(card_education)
        
        layout.addLayout(cards_layout)
        layout.addStretch()

    def start_education_mode(self):
        from ui.education.course_setup_dialog import CourseSetupDialog
        dialog = CourseSetupDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.switch_cb(4) # Switch to education wizard
