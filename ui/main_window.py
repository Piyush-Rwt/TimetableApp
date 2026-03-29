import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, 
    QPushButton, QLabel, QFrame, QScrollArea
)
from db.schema import init_db
from ui.styles import DARK_THEME
from ui.dashboard import DashboardScreen
from ui.mode_selector import ModeSelectorScreen
from ui.personal_mode import PersonalModeScreen
from ui.business_mode import BusinessModeScreen
from ui.settings import SettingsScreen

# Education Steps
from ui.education.teacher_upload import TeacherUploadScreen
from ui.education.institution_setup import InstitutionSetupScreen
from ui.education.section_group_setup import SectionGroupSetupScreen
from ui.education.subject_setup import SubjectSetupScreen
from ui.education.constraint_setup import ConstraintSetupScreen
from ui.education.generate_screen import GenerateScreen
from ui.education.timetable_viewer import TimetableViewerScreen

class EducationWizard(QWidget):
    def __init__(self, main_switch_cb):
        super().__init__()
        self.main_switch_cb = main_switch_cb
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("← Exit Education Mode")
        btn_back.clicked.connect(lambda: self.main_switch_cb(1))
        header.addWidget(btn_back)
        header.addStretch()
        layout.addLayout(header)

        # Step Indicator Bar
        self.step_indicator = QLabel("Step 1 of 7")
        self.step_indicator.setStyleSheet("color: #4f6ef7; font-weight: bold; font-size: 16px;")
        layout.addWidget(self.step_indicator)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.stack = QStackedWidget()
        self.scroll.setWidget(self.stack)
        layout.addWidget(self.scroll)

        # Initialize steps
        self.steps = [
            InstitutionSetupScreen(self.switch_step),
            SectionGroupSetupScreen(self.switch_step),
            TeacherUploadScreen(self.switch_step), # Now Step 3
            SubjectSetupScreen(self.switch_step), # Now Step 4
            ConstraintSetupScreen(self.switch_step),
            GenerateScreen(self.switch_step),
            TimetableViewerScreen(self.switch_step)
        ]
        for step in self.steps:
            self.stack.addWidget(step)

        # Navigation Bar
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.clicked.connect(self.prev_step)
        
        self.btn_next = QPushButton("Next")
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.clicked.connect(self.next_step)
        
        self.btn_save = QPushButton("Save Draft")
        self.btn_save.clicked.connect(self.save_draft)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_save)
        nav_layout.addWidget(self.btn_next)
        
        layout.addLayout(nav_layout)
        self.update_nav()

    def switch_step(self, idx):
        self.stack.setCurrentIndex(idx)
        self.update_nav()

    def prev_step(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
            self.update_nav()

    def next_step(self):
        idx = self.stack.currentIndex()
        if hasattr(self.steps[idx], 'save_data'):
            self.steps[idx].save_data()
            
        if idx < self.stack.count() - 1:
            self.stack.setCurrentIndex(idx + 1)
            self.update_nav()

    def save_draft(self):
        idx = self.stack.currentIndex()
        data = {}
        if hasattr(self.steps[idx], 'get_data'):
            data = self.steps[idx].get_data()
        
        import json
        from db.queries import save_draft
        save_draft(idx, json.dumps(data))
        
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Draft Saved", f"Step {idx + 1} progress saved successfully.")

    def load_draft(self):
        from db.queries import get_connection
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT step, data_json FROM wizard_draft ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        
        if row:
            step_idx, data_json = row
            data = json.loads(data_json)
            self.stack.setCurrentIndex(step_idx)
            if hasattr(self.steps[step_idx], 'set_data'):
                self.steps[step_idx].set_data(data)
            self.update_nav()
            return True
        return False

    def update_nav(self):
        idx = self.stack.currentIndex()
        self.step_indicator.setText(f"Step {idx + 1} of {self.stack.count()}")
        self.btn_prev.setEnabled(idx > 0)
        
        if idx == self.stack.count() - 1 or idx == 5: # View screen or Generate Screen
            self.btn_next.setVisible(False)
            self.btn_save.setVisible(False)
        else:
            self.btn_next.setVisible(True)
            self.btn_save.setVisible(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScheduleForge - Production Edition")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(DARK_THEME)

        init_db()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.stack.addWidget(DashboardScreen(self.switch_screen))       # 0
        self.stack.addWidget(ModeSelectorScreen(self.switch_screen))    # 1
        self.stack.addWidget(PersonalModeScreen(self.switch_screen))    # 2
        self.stack.addWidget(BusinessModeScreen(self.switch_screen))    # 3
        self.stack.addWidget(EducationWizard(self.switch_screen))       # 4
        self.stack.addWidget(SettingsScreen(self.switch_screen))        # 5

    def switch_screen(self, idx):
        self.stack.setCurrentIndex(idx)
