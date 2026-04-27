from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QTextBrowser, QMessageBox, QFrame
from PySide6.QtCore import Qt
import db.queries as queries
from random_data_generator import generate_random_data

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
        """
        Auto-fill database with random realistic test data.
        Generates:
        - 50 random teachers with varying max hours (12-28 hours/week)
        - 20-25 random rooms (classrooms and labs with random capacities)
        - 6-10 random sections with 50-80 students each
        - 8-13 random subjects assigned to random teachers
        - Random teacher unavailability slots
        """
        queries.clear_all_data()
        
        # Generate all random data
        data = generate_random_data()
        
        # 1. Insert Institution configuration
        queries.update_institution(data["institution"])
        
        # 2. Insert Breaks
        for brk in data["breaks"]:
            queries.insert_break(brk)
        
        # 3. Insert Sections
        for section_name, student_count in data["sections"]:
            queries.insert_section({"name": section_name, "student_count": student_count})
        
        # 4. Insert Teachers and their unavailability
        teacher_map = {}  # Maps teacher names to their IDs
        for teacher_name, max_hours in data["teachers"]:
            tid = queries.insert_teacher({
                "name": teacher_name,
                "max_hours_per_week": max_hours
            })
            teacher_map[teacher_name] = tid
            
            # Add random unavailability slots if they exist
            if teacher_name in data["teacher_unavailability"]:
                for day, slot in data["teacher_unavailability"][teacher_name]:
                    queries.insert_teacher_unavailability(tid, day, slot)
        
        # 5. Insert Rooms
        for room_name, room_type, capacity in data["rooms"]:
            queries.insert_room({
                "name": room_name,
                "type": room_type,
                "capacity": capacity
            })
        
        # 6. Insert Subjects with teacher assignments
        for subject in data["subjects"]:
            teacher_id = teacher_map.get(subject["teacher_name"])
            if teacher_id:  # Only insert if teacher exists
                queries.insert_subject({
                    "code": subject["code"],
                    "name": subject["name"],
                    "type": subject["type"],
                    "hours_per_week": subject["hours_per_week"],
                    "teacher_id": teacher_id,
                    "room_type_req": subject["room_type_req"],
                    "lab_duration": subject["lab_duration"],
                    "split_groups": subject["split_groups"]
                })
        
        # Show summary and navigate
        summary = f"""Random Test Data Generated:
        
• Teachers: {len(data['teachers'])}
• Rooms: {len(data['rooms'])}
• Sections: {len(data['sections'])}
• Subjects: {len(data['subjects'])}
• Working Days: {data['institution']['working_days']}
• Slot Duration: {data['institution']['slot_duration_mins']} minutes

Ready to generate schedule!"""
        
        QMessageBox.information(self, "Success", summary)
        if self.switch_cb:
            self.switch_cb(4)  # Navigate to Education Wizard
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
                background: #add8e6; 
                color: #003d82; 
                border: 1px solid #87ceeb; 
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                color: #ffffff;
                border: 1px solid #4db8ff;
                background: #87ceeb;
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
