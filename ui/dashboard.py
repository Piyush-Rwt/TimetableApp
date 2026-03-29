from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QTextBrowser, QMessageBox, QFrame
from PySide6.QtCore import Qt
import db.queries as queries

class AdminDialog(QDialog):
    def __init__(self, parent=None, switch_cb=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Tools")
        self.setFixedWidth(350)
        self.switch_cb = switch_cb
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel("Developer Quick Actions")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(label)
        
        btn_fill = QPushButton("🚀 Auto Fill Test Data")
        btn_fill.setObjectName("PrimaryButton")
        btn_fill.setFixedHeight(45)
        btn_fill.clicked.connect(self.auto_fill)
        layout.addWidget(btn_fill)
        
        btn_clear = QPushButton("🗑️ Clear All Data")
        btn_clear.setObjectName("DangerButton")
        btn_clear.setFixedHeight(45)
        btn_clear.clicked.connect(self.clear_data)
        layout.addWidget(btn_clear)
        
        layout.addSpacing(10)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

    def clear_data(self):
        queries.clear_all_data()
        QMessageBox.information(self, "Success", "All database tables cleared!")
        self.accept()

    def auto_fill(self):
        queries.clear_all_data()
        
        # 1. Institution
        inst_data = {
            "name": "Test University",
            "department": "Computer Science",
            "semester": "IV",
            "working_days": "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday",
            "start_time": "08:00",
            "end_time": "18:00",  # Extended from 17:00 to 18:00 (+2 more slots)
            "slot_duration_mins": 55
        }
        queries.update_institution(inst_data)
        queries.insert_break({"name": "Short Break", "start_time": "09:50", "end_time": "10:10"})
        queries.insert_break({"name": "Lunch Break", "start_time": "13:50", "end_time": "14:10"})
        
        # 2. Sections
        for s in ["A1", "A2", "B1", "B2"]:
            queries.insert_section({"name": s, "student_count": 60})
            
        # 3. Teachers - Increased max hours
        teachers = [
            ("Mr. Smith", 24), ("Mr. Jones", 22), ("Ms. Alice", 24),
            ("Mr. Brown", 16), ("Ms. White", 16)
        ]
        t_map = {}
        for name, max_h in teachers:
            tid = queries.insert_teacher({"name": name, "max_hours_per_week": max_h})
            t_map[name] = tid
            
        # Unavailability: Mr. Brown Mon
        for s_idx in range(9):
            queries.insert_teacher_unavailability(t_map["Mr. Brown"], "Monday", s_idx)
            
        # 4. Rooms - Added 2 more
        rooms = [
            ("CR 101", "Classroom", 60), ("CR 102", "Classroom", 60), ("CR 103", "Classroom", 60),
            ("CR 104", "Classroom", 60), ("LAB 1", "Lab", 35), ("LAB 2", "Lab", 35), ("LAB 3", "Lab", 35)
        ]
        for name, rtype, cap in rooms:
            queries.insert_room({"name": name, "type": rtype, "capacity": cap})
            
        # 5. Subjects - Reduced theory hours (3→2), NO lab splits, better distribution
        subjects = [
            ("TCS 401", "Theory 1", "Theory", 2, t_map["Mr. Smith"], "Classroom", 1, 0),
            ("TCS 402", "Theory 2", "Theory", 2, t_map["Mr. Jones"], "Classroom", 1, 0),
            ("TCS 403", "Theory 3", "Theory", 2, t_map["Ms. Alice"], "Classroom", 1, 0),
            ("PCS 401", "Lab 1", "Lab", 2, t_map["Mr. Smith"], "Lab", 2, 0),  # No split
            ("PCS 402", "Lab 2", "Lab", 2, t_map["Ms. Alice"], "Lab", 2, 0),  # No split
            ("ELECTIVE", "Elective 1", "Elective", 2, t_map["Mr. Brown"], "Classroom", 1, 0),
            ("GEC 101", "General Course", "Theory", 2, t_map["Ms. White"], "Classroom", 1, 0)
        ]
        for code, name, stype, hrs, tid, rtype, dur, split in subjects:
            queries.insert_subject({
                "code": code, "name": name, "type": stype, "hours_per_week": hrs,
                "teacher_id": tid, "room_type_req": rtype,
                "lab_duration": dur, "split_groups": split
            })
            
        QMessageBox.information(self, "Success", "Test data loaded! Go to Education Mode to generate.")
        if self.switch_cb:
            self.switch_cb(4) # Navigate to Education Wizard
        self.accept()

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help & Instructions")
        self.setMinimumSize(700, 600)
        layout = QVBoxLayout(self)
        
        help_text = QTextBrowser()
        help_text.setStyleSheet("background-color: #1a1d27; border: 1px solid #2a2d3e; color: #ffffff; padding: 10px;")
        help_text.setHtml("""
            <h2 style='color: #4f6ef7;'>ScheduleForge Help Guide</h2>
            <hr>
            <h3 style='color: #2ecc71;'>1. Education Mode</h3>
            <p>A 7-step wizard for schools and universities:</p>
            <ul>
                <li><b>Step 1:</b> Set university name, working days, and slot timings.</li>
                <li><b>Step 2:</b> Add student sections (e.g., A1, B2).</li>
                <li><b>Step 3:</b> Add subjects, assign teachers, and set theory/lab types.</li>
                <li><b>Step 4:</b> Manage teacher maximum hours and unavailable slots.</li>
                <li><b>Step 5:</b> Add rooms and specify if they are labs or classrooms.</li>
                <li><b>Step 6:</b> Click generate to run the constraint engine.</li>
                <li><b>Step 7:</b> View and export results to Excel.</li>
            </ul>
            <h3 style='color: #2ecc71;'>2. Personal & Business Modes</h3>
            <p>Simpler versions designed for individuals and staff shift planning.</p>
            <hr>
            <p><b>Tip:</b> Use the 'Save Draft' button in the wizard to resume later!</p>
        """)
        layout.addWidget(help_text)
        
        btn_close = QPushButton("Got it!")
        btn_close.setObjectName("PrimaryButton")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

class DashboardScreen(QWidget):
    def __init__(self, switch_cb):
        super().__init__()
        self.switch_cb = switch_cb
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Top Bar (Help & Settings)
        top_bar = QHBoxLayout()
        btn_help = QPushButton("❓ Help")
        btn_help.setFixedWidth(100)
        btn_help.clicked.connect(self.show_help)
        
        btn_settings = QPushButton("⚙️ Settings")
        btn_settings.setFixedWidth(120)
        btn_settings.clicked.connect(lambda: self.switch_cb(5))
        
        top_bar.addWidget(btn_help)
        top_bar.addStretch()
        top_bar.addWidget(btn_settings)
        layout.addLayout(top_bar)

        # Center Content
        layout.addStretch(1)
        
        title = QLabel("Welcome to ScheduleForge")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtext = QLabel("Smart university and college timetable generation")
        subtext.setObjectName("SubtitleLabel")
        subtext.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtext)

        layout.addSpacing(30)

        # Action Buttons
        btn_start = QPushButton("Make a Timetable →")
        btn_start.setObjectName("PrimaryButton")
        btn_start.setFixedSize(280, 60)
        btn_start.clicked.connect(lambda: self.switch_cb(1))
        layout.addWidget(btn_start, alignment=Qt.AlignCenter)

        layout.addSpacing(15)

        self.btn_continue = QPushButton("Continue Education Draft")
        self.btn_continue.setObjectName("SecondaryButton")
        self.btn_continue.setFixedSize(280, 50)
        self.btn_continue.setVisible(False)
        self.btn_continue.clicked.connect(self.continue_draft)
        layout.addWidget(self.btn_continue, alignment=Qt.AlignCenter)

        self.check_draft()

        layout.addStretch(2)

        # Footer Area
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 20, 0, 0) # Top padding for footer
        
        version_lbl = QLabel("v2.1.0 | 2026 Edition")
        version_lbl.setStyleSheet("color: #5c5f77;")
        footer_layout.addWidget(version_lbl)
        
        footer_layout.addStretch()
        
        # Subtle Admin Button - Improved Visibility
        btn_admin = QPushButton("Admin")
        btn_admin.setFixedSize(80, 30)
        btn_admin.setStyleSheet("""
            QPushButton {
                background: #1a1d27; 
                color: #3b4054; 
                border: 1px solid #2a2d3e; 
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                color: #4f6ef7;
                border: 1px solid #4f6ef7;
                background: #2a2d3e;
            }
        """)
        btn_admin.clicked.connect(self.show_admin)
        footer_layout.addWidget(btn_admin)
        
        layout.addLayout(footer_layout)

    def check_draft(self):
        try:
            from db.queries import get_connection
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT 1 FROM wizard_draft LIMIT 1")
            if c.fetchone():
                self.btn_continue.setVisible(True)
            conn.close()
        except: pass

    def continue_draft(self):
        main_win = self.window()
        if hasattr(main_win, 'stack'):
            edu_wizard = main_win.stack.widget(4)
            if hasattr(edu_wizard, 'load_draft'):
                if edu_wizard.load_draft():
                    self.switch_cb(4)

    def show_help(self):
        dialog = HelpDialog(self)
        dialog.exec()

    def show_admin(self):
        dialog = AdminDialog(self, self.switch_cb)
        dialog.exec()
