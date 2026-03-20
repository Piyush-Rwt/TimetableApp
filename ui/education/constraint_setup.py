import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QCheckBox, QPushButton, QScrollArea, QFrame, QGroupBox
)

class ConstraintSetupScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        self.setStyleSheet("background-color: #0f1117; color: #ffffff;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Step 5: Constraint Setup")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Section A: Student Constraints
        stu_group = QGroupBox("Section A: Student Constraints")
        stu_layout = QVBoxLayout()
        self.spn_stu_min_hrs = self.create_spinbox_row("Min hours a student attends per day", 4, stu_layout)
        self.spn_stu_max_hrs = self.create_spinbox_row("Max hours a student stays per day", 8, stu_layout)
        self.spn_stu_max_cons = self.create_spinbox_row("Max consecutive slots without a break", 3, stu_layout)
        stu_group.setLayout(stu_layout)
        content_layout.addWidget(stu_group)

        # Section B: Teacher Constraints
        tea_group = QGroupBox("Section B: Global Teacher Constraints")
        tea_layout = QVBoxLayout()
        self.spn_tea_max_teach = self.create_spinbox_row("Max teaching slots per day", 5, tea_layout)
        self.spn_tea_max_stay = self.create_spinbox_row("Max stay hours per day", 8, tea_layout)
        self.spn_tea_max_cons = self.create_spinbox_row("Max consecutive teaching slots", 3, tea_layout)
        self.spn_tea_gap = self.create_spinbox_row("Minimum gap between two sessions (minutes)", 0, tea_layout)
        tea_group.setLayout(tea_layout)
        content_layout.addWidget(tea_group)

        # Section C: Hard Constraints
        hard_group = QGroupBox("Section C: Hard Constraint Rules (Always Enforced)")
        hard_layout = QVBoxLayout()
        hard_rules = [
            "A teacher cannot teach two sections at the same time",
            "A section cannot have two subjects at the same time",
            "A room cannot have two classes at the same time",
            "No class during break/lunch slots",
            "Teacher availability window (from/till) must be respected",
            "Teacher unavailable days must be respected",
            "Lab sessions must be consecutive slots",
            "Respect per-teacher constraints from Excel upload"
        ]
        for rule in hard_rules:
            chk = QCheckBox(rule)
            chk.setChecked(True)
            chk.setEnabled(False) # Cannot turn off
            hard_layout.addWidget(chk)
        hard_group.setLayout(hard_layout)
        content_layout.addWidget(hard_group)

        # Section D: Soft Constraints
        soft_group = QGroupBox("Section D: Soft Constraint Preferences")
        soft_layout = QVBoxLayout()
        self.soft_chks = {}
        soft_rules = [
            "Avoid teacher having gaps between classes",
            "Distribute each subject evenly across week",
            "Prefer labs in second half of day",
            "Avoid first and last slot for high-priority teachers",
            "Balance workload across days"
        ]
        for rule in soft_rules:
            chk = QCheckBox(rule)
            chk.setChecked(True)
            self.soft_chks[rule] = chk
            soft_layout.addWidget(chk)
        soft_group.setLayout(soft_layout)
        content_layout.addWidget(soft_group)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def create_spinbox_row(self, label_text, default_val, parent_layout):
        row_widget = QWidget()
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 5, 0, 5)
        row.addWidget(QLabel(label_text))
        spn = QSpinBox()
        spn.setFixedWidth(100)
        spn.setValue(default_val)
        row.addWidget(spn)
        parent_layout.addWidget(row_widget)
        return spn

    def save_data(self):
        pass
