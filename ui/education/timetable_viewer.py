from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QListWidget
)

class TimetableViewerScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)

        title = QLabel("Timetable Viewer")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.setup_section_view()
        self.setup_teacher_view()
        self.setup_master_view()
        self.setup_warnings_view()

        export_layout = QHBoxLayout()
        btn_exp_sec = QPushButton("Export All Section Timetables")
        btn_exp_tea = QPushButton("Export All Teacher Timetables")
        btn_exp_mas = QPushButton("Export Master Sheet")
        export_layout.addWidget(btn_exp_sec)
        export_layout.addWidget(btn_exp_tea)
        export_layout.addWidget(btn_exp_mas)
        layout.addLayout(export_layout)

    def setup_section_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        top = QHBoxLayout()
        top.addWidget(QLabel("Course:"))
        top.addWidget(QComboBox())
        top.addWidget(QLabel("Year:"))
        top.addWidget(QComboBox())
        top.addWidget(QLabel("Group:"))
        top.addWidget(QComboBox())
        top.addWidget(QLabel("Section:"))
        top.addWidget(QComboBox())
        top.addStretch()
        l.addLayout(top)

        tbl = QTableWidget(8, 6)
        tbl.setHorizontalHeaderLabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(tbl)
        
        self.tabs.addTab(w, "Section View")

    def setup_teacher_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        top = QHBoxLayout()
        top.addWidget(QLabel("Teacher:"))
        top.addWidget(QComboBox())
        top.addStretch()
        l.addLayout(top)

        tbl = QTableWidget(8, 6)
        tbl.setHorizontalHeaderLabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(tbl)
        
        self.tabs.addTab(w, "Teacher View")

    def setup_master_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        tbl = QTableWidget(5, 48) # dummy
        l.addWidget(tbl)
        self.tabs.addTab(w, "Master View")

    def setup_warnings_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lst = QListWidget()
        
        from PySide6.QtWidgets import QListWidgetItem
        from PySide6.QtGui import QColor
        item = QListWidgetItem("Generation ran successfully with no hard constraint violations.")
        item.setForeground(QColor("#ffffff"))
        lst.addItem(item)
        
        l.addWidget(lst)
        self.tabs.addTab(w, "Conflicts & Warnings")
