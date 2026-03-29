from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QFrame
)
import db.queries as queries

class SubjectSetupScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Step 4: Add Subjects")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Table Container
        tbl_frame = QFrame()
        tbl_frame.setObjectName("Card")
        tbl_layout = QVBoxLayout(tbl_frame)

        self.tbl_subjects = QTableWidget(0, 7)
        self.tbl_subjects.setHorizontalHeaderLabels([
            "Code", "Name", "Type", "Hrs/Week", "Teacher", "Room Type", "Lab Details"
        ])
        self.tbl_subjects.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_subjects.setMinimumHeight(400)
        tbl_layout.addWidget(self.tbl_subjects)

        btn_add = QPushButton("+ Add Subject")
        btn_add.setFixedWidth(150)
        btn_add.clicked.connect(self.add_subject_row)
        tbl_layout.addWidget(btn_add)
        
        layout.addWidget(tbl_frame)
        layout.addStretch()
        self.load_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def add_subject_row(self, teacher_list=None):
        row = self.tbl_subjects.rowCount()
        self.tbl_subjects.insertRow(row)
        
        self.tbl_subjects.setItem(row, 0, QTableWidgetItem("TCS 401"))
        self.tbl_subjects.setItem(row, 1, QTableWidgetItem("New Subject"))
        
        cmb_type = QComboBox()
        cmb_type.addItems(["Theory", "Lab", "Elective"])
        self.tbl_subjects.setCellWidget(row, 2, cmb_type)
        
        spn_hrs = QSpinBox()
        spn_hrs.setRange(1, 40)
        spn_hrs.setValue(3)
        self.tbl_subjects.setCellWidget(row, 3, spn_hrs)
        
        # Teacher Dropdown (Required)
        cmb_teacher = QComboBox()
        if teacher_list is None:
            teacher_list = queries.get_all_teachers()
        
        for t in teacher_list:
            cmb_teacher.addItem(t['name'], t['id'])
        self.tbl_subjects.setCellWidget(row, 4, cmb_teacher)
        
        cmb_room = QComboBox()
        cmb_room.addItems(["Classroom", "Lab", "Lecture Hall", "Special Venue"])
        self.tbl_subjects.setCellWidget(row, 5, cmb_room)
        
        self.tbl_subjects.setItem(row, 6, QTableWidgetItem("Dur: 1, Split: 0"))

    def save_data(self):
        queries.delete_all_subjects()
        for r in range(self.tbl_subjects.rowCount()):
            t_id = self.tbl_subjects.cellWidget(r, 4).currentData()
            if not t_id:  # Ensure teacher is always assigned
                t_id = self.tbl_subjects.cellWidget(r, 4).itemData(0) if self.tbl_subjects.cellWidget(r, 4).count() > 0 else 1
            data = {
                "code": self.tbl_subjects.item(r, 0).text(),
                "name": self.tbl_subjects.item(r, 1).text(),
                "type": self.tbl_subjects.cellWidget(r, 2).currentText(),
                "hours_per_week": self.tbl_subjects.cellWidget(r, 3).value(),
                "teacher_id": int(t_id),
                "room_type_req": self.tbl_subjects.cellWidget(r, 5).currentText(),
                "lab_duration": 1,
                "split_groups": 0
            }
            details = self.tbl_subjects.item(r, 6).text()
            if "Dur: 2" in details: data["lab_duration"] = 2
            if "Split: 1" in details: data["split_groups"] = 1
            
            queries.insert_subject(data)

    def load_data(self):
        teachers = queries.get_all_teachers()
        subjects = queries.get_all_subjects()
        self.tbl_subjects.setRowCount(0)
        for s in subjects:
            self.add_subject_row(teachers)
            r = self.tbl_subjects.rowCount() - 1
            self.tbl_subjects.item(r, 0).setText(s['code'])
            self.tbl_subjects.item(r, 1).setText(s['name'])
            self.tbl_subjects.cellWidget(r, 2).setCurrentText(s['type'])
            self.tbl_subjects.cellWidget(r, 3).setValue(s['hours_per_week'])
            
            cmb_t = self.tbl_subjects.cellWidget(r, 4)
            target_id = int(s['teacher_id']) if s['teacher_id'] else None
            if target_id:
                idx = cmb_t.findData(target_id)
                if idx >= 0: 
                    cmb_t.setCurrentIndex(idx)
                else:
                    cmb_t.setCurrentIndex(0)  # Default to first teacher if not found
            else:
                cmb_t.setCurrentIndex(0)  # Default to first teacher if not assigned
            
            self.tbl_subjects.cellWidget(r, 5).setCurrentText(s['room_type_req'])
            self.tbl_subjects.item(r, 6).setText(f"Dur: {s['lab_duration']}, Split: {s['split_groups']}")
