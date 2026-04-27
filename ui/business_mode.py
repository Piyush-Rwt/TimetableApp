"""
Business Mode Screen - business_mode.py
Scheduling interface for organizations to plan staff shifts and work assignments.

Features:
- Add employees/staff
- Define shift patterns
- Assign roles and responsibilities
- Handle employee availability
- Generate fair shift schedules

Use Cases:
- Restaurant/retail staff scheduling
- Hospital shift planning
- Factory worker scheduling
- 24/7 operation coverage
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt

class BusinessModeScreen(QWidget):
    def __init__(self, switch_cb):
        super().__init__()
        self.switch_cb = switch_cb
        self.layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(lambda: self.switch_cb(1))
        header.addWidget(btn_back)
        self.title_lbl = QLabel("Business Roster - Step 1")
        header.addWidget(self.title_lbl)
        header.addStretch()
        self.layout.addLayout(header)
        
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        self.setup_step1()
        self.setup_step2()
        
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.clicked.connect(self.prev_step)
        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self.next_step)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_next)
        self.layout.addLayout(nav_layout)
        self.update_nav()

    def setup_step1(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Team Members"))
        self.tbl_team = QTableWidget(0, 3)
        self.tbl_team.setHorizontalHeaderLabels(["Name", "Role", "Max Hours/Week"])
        self.tbl_team.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.tbl_team)
        btn_add = QPushButton("Add Member")
        btn_add.clicked.connect(lambda: self.tbl_team.insertRow(self.tbl_team.rowCount()))
        l.addWidget(btn_add)
        self.stack.addWidget(w)

    def setup_step2(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Shifts"))
        self.tbl_shifts = QTableWidget(3, 3)
        self.tbl_shifts.setHorizontalHeaderLabels(["Shift Name", "Start Time", "End Time"])
        self.tbl_shifts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_shifts.setItem(0, 0, QTableWidgetItem("Morning"))
        self.tbl_shifts.setItem(0, 1, QTableWidgetItem("08:00"))
        self.tbl_shifts.setItem(0, 2, QTableWidgetItem("14:00"))
        self.tbl_shifts.setItem(1, 0, QTableWidgetItem("Afternoon"))
        self.tbl_shifts.setItem(1, 1, QTableWidgetItem("14:00"))
        self.tbl_shifts.setItem(1, 2, QTableWidgetItem("20:00"))
        self.tbl_shifts.setItem(2, 0, QTableWidgetItem("Night"))
        self.tbl_shifts.setItem(2, 1, QTableWidgetItem("20:00"))
        self.tbl_shifts.setItem(2, 2, QTableWidgetItem("02:00"))
        l.addWidget(self.tbl_shifts)
        self.stack.addWidget(w)

    def prev_step(self):
        if self.stack.currentIndex() > 0:
            self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
            self.update_nav()

    def next_step(self):
        if self.stack.currentIndex() < self.stack.count() - 1:
            self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
            self.update_nav()

    def update_nav(self):
        idx = self.stack.currentIndex()
        self.title_lbl.setText(f"Business Roster - Step {idx + 1}")
        self.btn_prev.setEnabled(idx > 0)
        self.btn_next.setVisible(idx < self.stack.count() - 1)
