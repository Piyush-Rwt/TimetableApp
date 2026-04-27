"""
ScheduleForge - Main Entry Point
This is the starting point of the application. It:
1. Checks for application updates
2. Initializes the PySide6 GUI framework
3. Loads and displays the main application window

The application is a timetable/schedule generation system with three modes:
- Education Mode: For schools and universities (creates class schedules)
- Personal Mode: For individuals (personal event scheduling)
- Business Mode: For organizations (staff shift planning)
"""

import sys
import os
import requests
import webbrowser
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VERSION_URL = "https://raw.githubusercontent.com/Piyush-Rwt/TimetableApp/main/version.json"
CURRENT_VERSION = "1.0"

def check_for_updates(parent=None):
    """
    Check GitHub for new application versions and notify user if update available.
    This runs asynchronously to not block the UI.
    
    Args:
        parent: Parent widget for displaying message dialogs
    """
    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            remote_version = data.get("version")
            download_url = data.get("download_url")
            
            if remote_version and remote_version != CURRENT_VERSION:
                reply = QMessageBox.question(
                    parent, 
                    "Update Available", 
                    f"A new version ({remote_version}) is available. Do you want to download it?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    webbrowser.open(download_url)
    except Exception:
        pass # Silent skip on internet or parsing errors

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    # Check for updates after showing the main window
    check_for_updates(window)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
