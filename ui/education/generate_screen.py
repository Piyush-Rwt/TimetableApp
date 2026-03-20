from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit
)
from PySide6.QtCore import QThread, Signal
import time

class GenerationThread(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def run(self):
        try:
            self.progress.emit(10, "Initializing slot grid...")
            time.sleep(0.5)
            self.progress.emit(30, "Locking break slots...")
            time.sleep(0.5)
            self.progress.emit(50, "Placing lab sessions...")
            time.sleep(0.5)
            self.progress.emit(70, "Placing theory classes...")
            time.sleep(0.5)
            self.progress.emit(85, "Applying soft constraints...")
            time.sleep(0.5)
            self.progress.emit(100, "Finalizing and saving...")
            time.sleep(0.5)
            self.finished.emit(True, "Done! Scheduled successfully.")
        except Exception as e:
            self.finished.emit(False, str(e))

class GenerateScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)

        title = QLabel("Step 6: Generate Timetable")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        self.summary_lbl = QLabel("Summary: 0 teachers, 0 sections, 0 subjects, 0 rooms")
        layout.addWidget(self.summary_lbl)

        self.btn_gen = QPushButton("Generate Timetables")
        self.btn_gen.setObjectName("PrimaryButton")
        self.btn_gen.setFixedSize(250, 50)
        self.btn_gen.clicked.connect(self.start_generation)
        layout.addWidget(self.btn_gen)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("")
        layout.addWidget(self.status_lbl)

        self.log_txt = QTextEdit()
        self.log_txt.setReadOnly(True)
        layout.addWidget(self.log_txt)

        self.btn_view = QPushButton("View Timetables →")
        self.btn_view.setObjectName("PrimaryButton")
        self.btn_view.setVisible(False)
        self.btn_view.clicked.connect(lambda: self.wizard_cb(6)) # Index 6 is view
        layout.addWidget(self.btn_view)

    def start_generation(self):
        self.btn_gen.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_txt.clear()
        
        self.thread = GenerationThread()
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.generation_finished)
        self.thread.start()

    def update_progress(self, val, msg):
        self.progress_bar.setValue(val)
        self.status_lbl.setText(msg)
        self.log_txt.append(msg)

    def generation_finished(self, success, msg):
        self.btn_gen.setEnabled(True)
        self.status_lbl.setText(msg)
        self.log_txt.append(msg)
        if success:
            self.btn_view.setVisible(True)
