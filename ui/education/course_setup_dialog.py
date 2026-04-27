"""
Course Setup Dialog - course_setup_dialog.py
Dialog for adding or editing individual courses/subjects in the Education Wizard.

Purpose:
- Provides a focused form for adding a single subject
- Used by SubjectSetupScreen for add/edit operations
- Validates input before saving to database

Fields:
- Subject Code (e.g., CS201)
- Subject Name (e.g., Data Structures)
- Subject Type (Theory, Lab, Elective)
- Teacher assignment
- Weekly hours (2, 3, 4, etc.)
- Room type requirement (Classroom, Lab)
- Lab duration (for lab classes)
- Split groups (for divided classes)

Modal dialog that blocks the parent window until closed.
Used as part of the larger subject management workflow.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from db.queries import execute_query

class CourseSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Initial Course Setup")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Institution Name:"))
        self.txt_inst_name = QLineEdit()
        self.txt_inst_name.setPlaceholderText("e.g. Stanford University")
        layout.addWidget(self.txt_inst_name)
        
        layout.addSpacing(10)
        layout.addWidget(QLabel("Course Configuration:"))
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Course Name", "Total Years", "Sections", "Mode"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add Course")
        btn_add.clicked.connect(self.add_row)
        btn_rem = QPushButton("Remove Selected")
        btn_rem.clicked.connect(self.remove_row)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_rem)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        layout.addSpacing(20)
        
        footer = QHBoxLayout()
        self.btn_ok = QPushButton("OK - Start Wizard")
        self.btn_ok.setObjectName("PrimaryButton")
        self.btn_ok.clicked.connect(self.accept_and_save)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        footer.addStretch()
        footer.addWidget(self.btn_cancel)
        footer.addWidget(self.btn_ok)
        layout.addLayout(footer)

    def add_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)
        
        # Years
        spn_years = QSpinBox()
        spn_years.setRange(1, 6)
        spn_years.setValue(4)
        self.table.setCellWidget(r, 1, spn_years)
        
        # Sections
        spn_secs = QSpinBox()
        spn_secs.setRange(1, 20)
        spn_secs.setValue(1)
        self.table.setCellWidget(r, 2, spn_secs)
        
        # Mode
        cmb = QComboBox()
        cmb.addItems(["Standard", "Group Mode"])
        self.table.setCellWidget(r, 3, cmb)

    def remove_row(self):
        curr = self.table.currentRow()
        if curr >= 0:
            self.table.removeRow(curr)

    def accept_and_save(self):
        inst_name = self.txt_inst_name.text().strip()
        if not inst_name:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Required", "Institution Name is required.")
            return

        # Save Institution
        inst_id = execute_query("INSERT INTO institutions (name) VALUES (?)", (inst_name,))
        
        # Save Courses and Sections
        for r in range(self.table.rowCount()):
            course_name = self.table.item(r, 0).text() if self.table.item(r, 0) else f"Course {r+1}"
            years = self.table.cellWidget(r, 1).value()
            secs = self.table.cellWidget(r, 2).value()
            mode = self.table.cellWidget(r, 3).currentText()
            
            c_id = execute_query("INSERT INTO courses (institution_id, name, total_years) VALUES (?, ?, ?)", 
                                (inst_id, course_name, years))
            
            # Auto-generate sections
            for y in range(1, years + 1):
                for s_num in range(secs):
                    s_name = chr(65 + s_num) if mode == "Standard" else f"G{s_num+1}"
                    execute_query("INSERT INTO sections (course_id, year, name, group_type) VALUES (?, ?, ?, ?)",
                                 (c_id, y, s_name, mode))
        
        self.accept()
