from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from db.queries import get_all_sections, insert_section, delete_all_sections

class SectionGroupSetupScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Step 2: Add Sections")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        layout.addWidget(QLabel("Define the sections/classes for which the timetable is generated."))

        # Table Container
        tbl_frame = QFrame()
        tbl_frame.setObjectName("Card")
        tbl_layout = QVBoxLayout(tbl_frame)

        self.tbl_sections = QTableWidget(0, 2)
        self.tbl_sections.setHorizontalHeaderLabels(["Section Name", "Student Count"])
        self.tbl_sections.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_sections.setMinimumHeight(400)
        tbl_layout.addWidget(self.tbl_sections)

        btn_add = QPushButton("+ Add Section")
        btn_add.setFixedWidth(150)
        btn_add.clicked.connect(self.add_section_row)
        tbl_layout.addWidget(btn_add)
        
        layout.addWidget(tbl_frame)
        layout.addStretch()
        self.load_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def add_section_row(self):
        row = self.tbl_sections.rowCount()
        self.tbl_sections.insertRow(row)
        self.tbl_sections.setItem(row, 0, QTableWidgetItem(f"Section {chr(65+row)}"))
        
        spn = QSpinBox()
        spn.setRange(1, 1000)
        spn.setValue(60)
        self.tbl_sections.setCellWidget(row, 1, spn)

    def save_data(self):
        delete_all_sections()
        for r in range(self.tbl_sections.rowCount()):
            name = self.tbl_sections.item(r, 0).text()
            count = self.tbl_sections.cellWidget(r, 1).value()
            insert_section({"name": name, "student_count": count})

    def load_data(self):
        sections = get_all_sections()
        self.tbl_sections.setRowCount(0)
        for s in sections:
            self.add_section_row()
            r = self.tbl_sections.rowCount() - 1
            self.tbl_sections.item(r, 0).setText(s['name'])
            self.tbl_sections.cellWidget(r, 1).setValue(s['student_count'])
