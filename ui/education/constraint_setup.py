"""
Constraint Setup Screen - constraint_setup.py
Step 4/5 of the Education Wizard: Add rooms and configure constraints.

Features:
- Add physical spaces (classrooms, labs, lecture halls)
- Set room type (Classroom or Lab)
- Set room capacity
- Configure teacher maximum hours per week
- Set teacher unavailable time slots

Rooms:
- Classrooms: For theory classes (capacity 40-100)
- Labs: For practical classes (capacity 20-50)
- Lecture Theatres: For large lectures (capacity 100+)

Teacher Constraints:
- Maximum hours per week (e.g., 24 hours)
- Unavailable slots: Days/times when teacher can't teach
  (e.g., Mr. Brown unavailable Monday 9:00-10:00)

These constraints ensure the generated schedule respects resource limitations
and teacher preferences.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QFrame
)
from db.queries import get_all_rooms, insert_room, delete_all_rooms

class ConstraintSetupScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Step 5: Add Rooms")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        layout.addWidget(QLabel("Define the rooms where classes and labs will be held."))

        # Table Container
        tbl_frame = QFrame()
        tbl_frame.setObjectName("Card")
        tbl_layout = QVBoxLayout(tbl_frame)

        self.tbl_rooms = QTableWidget(0, 3)
        self.tbl_rooms.setHorizontalHeaderLabels(["Room Name/No.", "Type", "Capacity"])
        self.tbl_rooms.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_rooms.setMinimumHeight(400)
        tbl_layout.addWidget(self.tbl_rooms)

        btn_add = QPushButton("+ Add Room")
        btn_add.setFixedWidth(150)
        btn_add.clicked.connect(self.add_room_row)
        tbl_layout.addWidget(btn_add)
        
        layout.addWidget(tbl_frame)
        layout.addStretch()
        self.load_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def add_room_row(self):
        row = self.tbl_rooms.rowCount()
        self.tbl_rooms.insertRow(row)
        self.tbl_rooms.setItem(row, 0, QTableWidgetItem(f"CR {101+row}"))
        
        cmb_type = QComboBox()
        cmb_type.addItems(["Classroom", "Lab", "Lecture Hall", "Special Venue"])
        self.tbl_rooms.setCellWidget(row, 1, cmb_type)
        
        spn = QSpinBox()
        spn.setRange(1, 1000)
        spn.setValue(60)
        self.tbl_rooms.setCellWidget(row, 2, spn)

    def save_data(self):
        delete_all_rooms()
        for r in range(self.tbl_rooms.rowCount()):
            name = self.tbl_rooms.item(r, 0).text()
            rtype = self.tbl_rooms.cellWidget(r, 1).currentText()
            cap = self.tbl_rooms.cellWidget(r, 2).value()
            insert_room({"name": name, "type": rtype, "capacity": cap})

    def load_data(self):
        rooms = get_all_rooms()
        self.tbl_rooms.setRowCount(0)
        for r_data in rooms:
            self.add_room_row()
            r = self.tbl_rooms.rowCount() - 1
            self.tbl_rooms.item(r, 0).setText(r_data['name'])
            self.tbl_rooms.cellWidget(r, 1).setCurrentText(r_data['type'])
            self.tbl_rooms.cellWidget(r, 2).setValue(r_data['capacity'])
