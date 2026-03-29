from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QTimeEdit, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt, QTime
from db.queries import update_institution, delete_all_breaks, insert_break, get_institution, get_breaks

class InstitutionSetupScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("Step 1: Institution & Time Setup")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Form Container
        form_frame = QFrame()
        form_frame.setObjectName("Card")
        form_frame.setStyleSheet("QFrame#Card { border-left: 5px solid #4f6ef7; padding-left: 15px; }")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(10)

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Institution Name (e.g., Graphic Era Hill University)")
        form_layout.addWidget(QLabel("Institution Name:"))
        form_layout.addWidget(self.txt_name)
        
        self.txt_dept = QLineEdit()
        self.txt_dept.setPlaceholderText("Department (e.g., Computer Science)")
        form_layout.addWidget(QLabel("Department:"))
        form_layout.addWidget(self.txt_dept)
        
        self.txt_sem = QLineEdit()
        self.txt_sem.setPlaceholderText("Semester (e.g., IV)")
        form_layout.addWidget(QLabel("Semester:"))
        form_layout.addWidget(self.txt_sem)
        layout.addWidget(form_frame)

        # Days Container
        days_frame = QFrame()
        days_frame.setObjectName("Card")
        days_frame.setStyleSheet("QFrame#Card { border-left: 5px solid #2ecc71; padding-left: 15px; }")
        days_vbox = QVBoxLayout(days_frame)
        days_vbox.addWidget(QLabel("Working Days:"))
        days_layout = QHBoxLayout()
        self.chk_days = {}
        for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            chk = QCheckBox(d)
            if d != "Sunday": chk.setChecked(True)
            self.chk_days[d] = chk
            days_layout.addWidget(chk)
        days_vbox.addLayout(days_layout)
        layout.addWidget(days_frame)

        # Time Slots Container
        time_frame = QFrame()
        time_frame.setObjectName("Card")
        time_frame.setStyleSheet("QFrame#Card { border-left: 5px solid #9b59b6; padding-left: 15px; }")
        time_vbox = QVBoxLayout(time_frame)
        time_vbox.addWidget(QLabel("Daily Schedule Configuration:"))
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Start Time:"))
        self.tm_start = QTimeEdit()
        self.tm_start.setTime(QTime(8, 0))
        time_layout.addWidget(self.tm_start)
        
        time_layout.addWidget(QLabel("End Time:"))
        self.tm_end = QTimeEdit()
        self.tm_end.setTime(QTime(17, 0))
        time_layout.addWidget(self.tm_end)
        
        time_layout.addWidget(QLabel("Slot Duration (mins):"))
        self.spn_dur = QSpinBox()
        self.spn_dur.setRange(30, 120)
        self.spn_dur.setValue(55)
        time_layout.addWidget(self.spn_dur)
        time_vbox.addLayout(time_layout)
        layout.addWidget(time_frame)

        # Breaks Container
        breaks_frame = QFrame()
        breaks_frame.setObjectName("Card")
        breaks_frame.setStyleSheet("QFrame#Card { border-left: 5px solid #f1c40f; padding-left: 15px; }")
        breaks_layout = QVBoxLayout(breaks_frame)
        breaks_layout.addWidget(QLabel("Breaks (e.g., Lunch, Tea)"))
        self.tbl_breaks = QTableWidget(0, 3)
        self.tbl_breaks.setHorizontalHeaderLabels(["Name", "Start Time", "End Time"])
        self.tbl_breaks.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_breaks.setMinimumHeight(120)
        breaks_layout.addWidget(self.tbl_breaks)

        btn_add_break = QPushButton("+ Add Break")
        btn_add_break.setFixedWidth(150)
        btn_add_break.clicked.connect(self.add_break_row)
        breaks_layout.addWidget(btn_add_break)
        layout.addWidget(breaks_frame)
        
        self.load_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def add_break_row(self):
        row = self.tbl_breaks.rowCount()
        self.tbl_breaks.insertRow(row)
        self.tbl_breaks.setItem(row, 0, QTableWidgetItem("Break"))
        
        tm_start = QTimeEdit()
        tm_start.setTime(QTime(12, 0))
        self.tbl_breaks.setCellWidget(row, 1, tm_start)
        
        tm_end = QTimeEdit()
        tm_end.setTime(QTime(13, 0))
        self.tbl_breaks.setCellWidget(row, 2, tm_end)

    def save_data(self):
        working_days = ",".join([d for d, chk in self.chk_days.items() if chk.isChecked()])
        data = {
            "name": self.txt_name.text(),
            "department": self.txt_dept.text(),
            "semester": self.txt_sem.text(),
            "working_days": working_days,
            "start_time": self.tm_start.time().toString("HH:mm"),
            "end_time": self.tm_end.time().toString("HH:mm"),
            "slot_duration_mins": self.spn_dur.value()
        }
        update_institution(data)
        
        delete_all_breaks()
        for r in range(self.tbl_breaks.rowCount()):
            name = self.tbl_breaks.item(r, 0).text()
            start = self.tbl_breaks.cellWidget(r, 1).time().toString("HH:mm")
            end = self.tbl_breaks.cellWidget(r, 2).time().toString("HH:mm")
            insert_break({"name": name, "start_time": start, "end_time": end})

    def load_data(self):
        inst_row = get_institution()
        if inst_row:
            inst = dict(inst_row)
            self.txt_name.setText(inst['name'])
            self.txt_dept.setText(inst.get('department', ''))
            self.txt_sem.setText(inst.get('semester', ''))
            self.tm_start.setTime(QTime.fromString(inst['start_time'], "HH:mm"))
            self.tm_end.setTime(QTime.fromString(inst['end_time'], "HH:mm"))
            self.spn_dur.setValue(inst['slot_duration_mins'])
            
            days = inst['working_days'].split(',')
            for d, chk in self.chk_days.items():
                chk.setChecked(d in days)
                
        breaks = get_breaks()
        self.tbl_breaks.setRowCount(0)
        for b in breaks:
            self.add_break_row()
            r = self.tbl_breaks.rowCount() - 1
            self.tbl_breaks.item(r, 0).setText(b['name'])
            self.tbl_breaks.cellWidget(r, 1).setTime(QTime.fromString(b['start_time'], "HH:mm"))
            self.tbl_breaks.cellWidget(r, 2).setTime(QTime.fromString(b['end_time'], "HH:mm"))
