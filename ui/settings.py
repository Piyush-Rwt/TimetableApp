"""
Settings Screen - settings.py
Application preferences and configuration interface.

Features:
- Application theme selection
- Export/import settings
- Database path configuration
- User preferences

Settings are persisted and loaded on application startup.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QLineEdit, QFileDialog
)
from PySide6.QtCore import Qt
import os

class SettingsScreen(QWidget):
    def __init__(self, switch_cb):
        super().__init__()
        self.switch_cb = switch_cb
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(lambda: switch_cb(0)) # Back to dashboard
        header.addWidget(btn_back)
        header.addStretch()
        layout.addLayout(header)

        title = QLabel("App Settings")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # 1. App Version
        version_group = QGroupBox("System Information")
        version_layout = QVBoxLayout()
        version_layout.addWidget(QLabel("App Version: 1.0.0"))
        btn_update = QPushButton("Check for Updates")
        btn_update.clicked.connect(self.check_updates)
        version_layout.addWidget(btn_update)
        version_group.setLayout(version_layout)
        layout.addWidget(version_group)

        # 3. Export Folder
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout()
        export_layout.addWidget(QLabel("Default Export Path:"))
        
        path_row = QHBoxLayout()
        self.export_path_edit = QLineEdit()
        self.export_path_edit.setText(os.path.join(os.path.expanduser("~"), "Documents", "ScheduleForge"))
        path_row.addWidget(self.export_path_edit)
        
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.browse_folder)
        path_row.addWidget(btn_browse)
        
        export_layout.addLayout(path_row)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        layout.addStretch()

    def check_updates(self):
        from main import check_for_updates
        check_for_updates(self)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if folder:
            self.export_path_edit.setText(folder)
