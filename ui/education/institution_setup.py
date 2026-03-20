import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QTimeEdit, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTime

class InstitutionSetupScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)

        title = QLabel("Step 2: Institution Setup")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Institution Name")
        layout.addWidget(self.txt_name)

        # Days
        days_layout = QHBoxLayout()
        self.chk_days = []
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            chk = QCheckBox(d)
            chk.setChecked(True)
            self.chk_days.append(chk)
            days_layout.addWidget(chk)
        layout.addLayout(days_layout)

        # Time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Start Time:"))
        self.tm_start = QTimeEdit()
        self.tm_start.setTime(QTime(9, 0))
        time_layout.addWidget(self.tm_start)
        
        time_layout.addWidget(QLabel("End Time:"))
        self.tm_end = QTimeEdit()
        self.tm_end.setTime(QTime(17, 0))
        time_layout.addWidget(self.tm_end)
        layout.addLayout(time_layout)

        # Duration
        dur_layout = QHBoxLayout()
        dur_layout.addWidget(QLabel("Slot Duration (mins):"))
        self.spn_dur = QSpinBox()
        self.spn_dur.setRange(30, 120)
        self.spn_dur.setValue(60)
        dur_layout.addWidget(self.spn_dur)
        
        self.lbl_total = QLabel("Total slots per day: 8")
        dur_layout.addWidget(self.lbl_total)
        layout.addLayout(dur_layout)
        
        self.tm_start.timeChanged.connect(self.recalc_slots)
        self.tm_end.timeChanged.connect(self.recalc_slots)
        self.spn_dur.valueChanged.connect(self.recalc_slots)

        # Breaks
        layout.addWidget(QLabel("Breaks Configuration"))
        self.tbl_breaks = QTableWidget(0, 3)
        self.tbl_breaks.setHorizontalHeaderLabels(["Break Name", "Start Time", "Duration (mins)"])
        self.tbl_breaks.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tbl_breaks)

        btn_add = QPushButton("Add Break")
        btn_add.clicked.connect(lambda: self.tbl_breaks.insertRow(self.tbl_breaks.rowCount()))
        layout.addWidget(btn_add)

    def recalc_slots(self):
        start = self.tm_start.time()
        end = self.tm_end.time()
        total_mins = start.secsTo(end) // 60
        slots = total_mins // self.spn_dur.value()
        self.lbl_total.setText(f"Total slots per day: {slots}")

    def save_data(self):
        # Implementation to save data via db.queries.execute_query
        pass
