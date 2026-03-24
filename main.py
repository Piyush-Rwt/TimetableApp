import sys
import requests
import webbrowser
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow

VERSION_URL = "https://raw.githubusercontent.com/Piyush-Rwt/TimetableApp/main/version.json"
CURRENT_VERSION = "1.0"

def check_for_updates(parent=None):
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
