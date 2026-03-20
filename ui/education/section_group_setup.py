from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)

class SectionGroupSetupScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)

        title = QLabel("Step 3: Group Setup")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        layout.addWidget(QLabel("Manage Groups (Core / Specialization / Electives)"))
        self.tbl_groups = QTableWidget(0, 3)
        self.tbl_groups.setHorizontalHeaderLabels(["Group Name", "Section Names (comma-separated)", "Group Type"])
        self.tbl_groups.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tbl_groups)

        btn_add_group = QPushButton("Add Group")
        btn_add_group.clicked.connect(lambda: self.add_group_row())
        layout.addWidget(btn_add_group)

    def add_group_row(self):
        r = self.tbl_groups.rowCount()
        self.tbl_groups.insertRow(r)
        
        cmb = QComboBox()
        cmb.addItems(["Core", "Specialization", "Elective"])
        self.tbl_groups.setCellWidget(r, 2, cmb)

    def save_data(self):
        pass
