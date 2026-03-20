from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QLineEdit, QSpinBox, QTimeEdit, QTableWidget, QTableWidgetItem, QComboBox, QHeaderView
from PySide6.QtCore import Qt, QTime

class PersonalModeScreen(QWidget):
    def __init__(self, switch_cb):
        super().__init__()
        self.switch_cb = switch_cb
        
        self.layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(self.go_back)
        header.addWidget(btn_back)
        self.title_lbl = QLabel("Personal Schedule - Step 1")
        header.addWidget(self.title_lbl)
        header.addStretch()
        self.layout.addLayout(header)
        
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        self.setup_step1()
        self.setup_step2()
        self.setup_step3()
        self.setup_step4()
        self.setup_step5()
        
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

    def go_back(self):
        self.switch_cb(1) # Return to mode selector

    def setup_step1(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("What do you want to schedule?"))
        self.txt_activities = QLineEdit()
        self.txt_activities.setPlaceholderText("e.g. Study, Gym, Reading, Cooking, Meditation")
        l.addWidget(self.txt_activities)
        l.addStretch()
        self.stack.addWidget(w)

    def setup_step2(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("How many days per week?"))
        self.spn_days = QSpinBox()
        self.spn_days.setRange(1, 7)
        self.spn_days.setValue(5)
        l.addWidget(self.spn_days)
        
        l.addWidget(QLabel("Active from:"))
        self.time_from = QTimeEdit()
        self.time_from.setDisplayFormat("HH:mm")
        self.time_from.setTime(QTime(8, 0)) # Fixed line
        l.addWidget(self.time_from)
        
        l.addWidget(QLabel("Active till:"))
        self.time_to = QTimeEdit()
        self.time_to.setDisplayFormat("HH:mm")
        self.time_to.setTime(QTime(22, 0)) # Fixed line
        l.addWidget(self.time_to)
        
        l.addStretch()
        self.stack.addWidget(w)

    def setup_step3(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Fixed Commitments (Blocked slots)"))
        self.tbl_fixed = QTableWidget(0, 4)
        self.tbl_fixed.setHorizontalHeaderLabels(["Activity", "Day", "From", "To"])
        self.tbl_fixed.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.tbl_fixed)
        
        btn_add = QPushButton("Add Row")
        btn_add.clicked.connect(lambda: self.tbl_fixed.insertRow(self.tbl_fixed.rowCount()))
        l.addWidget(btn_add)
        self.stack.addWidget(w)

    def setup_step4(self):
        w = QWidget()
        self.l4 = QVBoxLayout(w)
        self.l4.addWidget(QLabel("Duration & Priority"))
        self.tbl_dur = QTableWidget(0, 3)
        self.tbl_dur.setHorizontalHeaderLabels(["Activity", "Duration (mins)", "Priority"])
        self.tbl_dur.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.l4.addWidget(self.tbl_dur)
        self.stack.addWidget(w)

    def setup_step5(self):
        w = QWidget()
        l = QVBoxLayout(w)
        btn_gen = QPushButton("Generate My Schedule")
        btn_gen.setObjectName("PrimaryButton")
        l.addWidget(btn_gen)
        
        self.tbl_result = QTableWidget()
        l.addWidget(self.tbl_result)
        self.stack.addWidget(w)

    def prev_step(self):
        if self.stack.currentIndex() > 0:
            self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
            self.update_nav()

    def next_step(self):
        idx = self.stack.currentIndex()
        if idx == 0:
            acts = [x.strip() for x in self.txt_activities.text().split(",") if x.strip()]
            self.tbl_dur.setRowCount(0)
            for a in acts:
                r = self.tbl_dur.rowCount()
                self.tbl_dur.insertRow(r)
                self.tbl_dur.setItem(r, 0, QTableWidgetItem(a))
                spn = QSpinBox()
                spn.setRange(15, 180)
                self.tbl_dur.setCellWidget(r, 1, spn)
                cmb = QComboBox()
                cmb.addItems(["High", "Medium", "Low"])
                self.tbl_dur.setCellWidget(r, 2, cmb)
                
        if idx < self.stack.count() - 1:
            self.stack.setCurrentIndex(idx + 1)
            self.update_nav()

    def update_nav(self):
        idx = self.stack.currentIndex()
        self.title_lbl.setText(f"Personal Schedule - Step {idx + 1}")
        self.btn_prev.setEnabled(idx > 0)
        self.btn_next.setVisible(idx < self.stack.count() - 1)
