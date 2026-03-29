from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QCheckBox, QGridLayout, QFrame
)
from db.queries import get_all_teachers, insert_teacher, delete_all_teachers, get_institution, insert_teacher_unavailability, get_teacher_unavailability
from PySide6.QtCore import Qt
import json

class UnavailabilityDialog(QDialog):
    def __init__(self, teacher_name, days, num_slots, existing_unav):
        super().__init__()
        self.setWindowTitle(f"Unavailability: {teacher_name}")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)
        
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)
        
        self.chks = {} # (day, slot) -> QCheckBox
        
        # Headers
        for d_idx, day in enumerate(days):
            self.grid_layout.addWidget(QLabel(day), 0, d_idx + 1)
        
        for s_idx in range(num_slots):
            self.grid_layout.addWidget(QLabel(f"Slot {s_idx+1}"), s_idx + 1, 0)
            for d_idx, day in enumerate(days):
                chk = QCheckBox()
                is_unav = any(u['day'] == day and u['slot_index'] == s_idx for u in existing_unav)
                chk.setChecked(is_unav)
                self.grid_layout.addWidget(chk, s_idx + 1, d_idx + 1)
                self.chks[(day, s_idx)] = chk
                
        btn_ok = QPushButton("Apply")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

    def get_unavailability(self):
        res = []
        for (day, s_idx), chk in self.chks.items():
            if chk.isChecked():
                res.append((day, s_idx))
        return res

class TeacherUploadScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Step 3: Add Teachers & Availability")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Table Container
        tbl_frame = QFrame()
        tbl_frame.setObjectName("Card")
        tbl_layout = QVBoxLayout(tbl_frame)

        self.tbl_teachers = QTableWidget(0, 3)
        self.tbl_teachers.setHorizontalHeaderLabels(["Teacher Name", "Max Hrs/Week", "Unavailability"])
        self.tbl_teachers.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_teachers.setMinimumHeight(400)
        tbl_layout.addWidget(self.tbl_teachers)

        btn_add = QPushButton("+ Add Teacher")
        btn_add.setFixedWidth(150)
        btn_add.clicked.connect(self.add_teacher_row)
        tbl_layout.addWidget(btn_add)
        
        layout.addWidget(tbl_frame)
        layout.addStretch()
        self.teacher_unav_data = {} # row_idx -> list of (day, slot)
        
        self.load_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def add_teacher_row(self):
        row = self.tbl_teachers.rowCount()
        self.tbl_teachers.insertRow(row)
        self.tbl_teachers.setItem(row, 0, QTableWidgetItem(f"Teacher {row+1}"))
        
        spn = QSpinBox()
        spn.setRange(1, 100)
        spn.setValue(20)
        self.tbl_teachers.setCellWidget(row, 1, spn)
        
        btn_unav = QPushButton("Set Slots")
        btn_unav.clicked.connect(lambda: self.open_unav_dialog(row))
        self.tbl_teachers.setCellWidget(row, 2, btn_unav)

    def open_unav_dialog(self, row):
        name = self.tbl_teachers.item(row, 0).text()
        inst_row = get_institution()
        if not inst_row: return
        inst = dict(inst_row)
        
        days = [d.strip() for d in inst['working_days'].split(',')]
        from datetime import datetime
        start = datetime.strptime(inst['start_time'], "%H:%M")
        end = datetime.strptime(inst['end_time'], "%H:%M")
        num_slots = int((end - start).total_seconds() / (60 * inst['slot_duration_mins']))
        
        existing = self.teacher_unav_data.get(row, [])
        
        dlg = UnavailabilityDialog(name, days, num_slots, existing)
        if dlg.exec():
            self.teacher_unav_data[row] = dlg.get_unavailability()

    def save_data(self):
        delete_all_teachers()
        for r in range(self.tbl_teachers.rowCount()):
            name = self.tbl_teachers.item(r, 0).text()
            max_hrs = self.tbl_teachers.cellWidget(r, 1).value()
            t_id = insert_teacher({"name": name, "max_hours_per_week": max_hrs})
            
            unav_list = self.teacher_unav_data.get(r, [])
            for day, s_idx in unav_list:
                if isinstance(day, tuple): # Robustness check
                    insert_teacher_unavailability(t_id, day[0], day[1])
                else:
                    insert_teacher_unavailability(t_id, day, s_idx)

    def load_data(self):
        teachers = get_all_teachers()
        self.tbl_teachers.setRowCount(0)
        self.teacher_unav_data = {}
        for idx, t in enumerate(teachers):
            self.add_teacher_row()
            r = self.tbl_teachers.rowCount() - 1
            self.tbl_teachers.item(r, 0).setText(t['name'])
            self.tbl_teachers.cellWidget(r, 1).setValue(t['max_hours_per_week'])
            
            unavs = get_teacher_unavailability(t['id'])
            self.teacher_unav_data[r] = [{'day': u['day'], 'slot_index': u['slot_index']} for u in unavs]
