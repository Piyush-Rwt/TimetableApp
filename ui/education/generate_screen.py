from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit, QMessageBox, QFrame
)
from PySide6.QtCore import QThread, Signal, Qt
import db.queries as queries
from engine.constraint_solver import ConstraintSolver

class GenerationThread(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str, object)

    def run(self):
        try:
            self.progress.emit(10, "Fetching data from database...")
            inst_row = queries.get_institution()
            if not inst_row:
                self.finished.emit(False, "No institution setup found.", None)
                return
            inst = dict(inst_row)
            breaks = [dict(b) for b in queries.get_breaks()]
            sections = [dict(s) for s in queries.get_all_sections()]
            teachers = [dict(t) for t in queries.get_all_teachers()]
            subjects = [dict(s) for s in queries.get_all_subjects()]
            rooms = [dict(r) for r in queries.get_all_rooms()]
            
            unav = []
            for t in teachers:
                unav.extend([dict(u) for u in queries.get_teacher_unavailability(t['id'])])
            
            elective_opts = [] 
            
            if not sections or not subjects or not rooms:
                self.finished.emit(False, "Missing data: sections, subjects, or rooms.", None)
                return

            self.progress.emit(30, "Initializing solver engine...")
            solver = ConstraintSolver(inst, breaks, sections, teachers, unav, subjects, elective_opts, rooms)
            
            self.progress.emit(40, "Generating base timetable (CSP)...")
            # We bypass solve() to get manual progress reporting
            import time
            start_time = time.time()
            res = solver.run_iteration()
            
            if res['success']:
                self.progress.emit(70, "Optimizing timetable quality (Simulated Annealing)...")
                initial_score = solver.calculate_total_score(res['assignment'])
                optimized_assignment = solver.optimize(res['assignment'], total_time_limit=2.0)
                res['assignment'] = optimized_assignment
                res['grid'] = solver.section_grid
                final_score = solver.calculate_total_score(optimized_assignment)
                res['initial_score'] = initial_score
                res['final_score'] = final_score
            else:
                res['initial_score'] = 0
                res['final_score'] = 0
                
            res['time_taken'] = time.time() - start_time
            result = res
            
            if not result['success']:
                self.progress.emit(70, f"Warning: {len(result['failed'])} subjects could not be scheduled.")
            
            self.progress.emit(80, "Persisting results to database...")
            queries.clear_timetable_entries()
            
            for sec_id, days in result['grid'].items():
                for day, slots in days.items():
                    for slot_idx, entry in slots.items():
                        if entry and isinstance(entry, dict):
                            t_id = int(entry.get('teacher_id') or 0)
                            s_id = int(entry.get('subject_id') or 0)
                            r_id = int(entry.get('room_id') or 0)
                            
                            # Debug print as requested by user
                            print(f"Inserting: section={sec_id}, subject={s_id}, teacher={t_id}, room={r_id}, day={day}, slot={slot_idx}")
                            
                            queries.insert_timetable_entry({
                                'section_id': int(sec_id),
                                'subject_id': s_id,
                                'teacher_id': t_id,
                                'room_id': r_id,
                                'day': day,
                                'slot_index': int(slot_idx),
                                'is_lab': entry.get('is_lab', 0),
                                'elective_option_id': None
                            })
            
            self.progress.emit(100, "Done.")
            self.finished.emit(True, "Generation complete.", result)
            
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            self.finished.emit(False, f"Error: {str(e)}\n\nFull details:\n{err_msg}", None)

class GenerateScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Step 6: Generate Timetable")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Status Card
        status_frame = QFrame()
        status_frame.setObjectName("Card")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(15)

        self.status_lbl = QLabel("Ready to generate.")
        self.status_lbl.setStyleSheet("font-size: 16px; color: #8b8fa8;")
        status_layout.addWidget(self.status_lbl)

        self.btn_gen = QPushButton("🚀 Start Generation")
        self.btn_gen.setObjectName("PrimaryButton")
        self.btn_gen.setFixedSize(250, 50)
        self.btn_gen.clicked.connect(self.start_generation)
        status_layout.addWidget(self.btn_gen, alignment=Qt.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(25)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_frame)

        # Log Card
        log_frame = QFrame()
        log_frame.setObjectName("Card")
        log_layout = QVBoxLayout(log_frame)
        log_layout.addWidget(QLabel("Generation Log:"))
        self.log_txt = QTextEdit()
        self.log_txt.setReadOnly(True)
        self.log_txt.setMinimumHeight(300)
        log_layout.addWidget(self.log_txt)
        layout.addWidget(log_frame)

        self.btn_view = QPushButton("View Results →")
        self.btn_view.setObjectName("PrimaryButton")
        self.btn_view.setFixedSize(200, 50)
        self.btn_view.setVisible(False)
        self.btn_view.clicked.connect(lambda: self.wizard_cb(6))
        layout.addWidget(self.btn_view, alignment=Qt.AlignRight)

        layout.addStretch()

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
        self.log_txt.append(msg)

    def generation_finished(self, success, msg, result):
        self.btn_gen.setEnabled(True)
        self.btn_gen.setText("🔄 Regenerate")
        self.log_txt.append(msg)
        if success:
            if result['success']:
                time_taken = result.get('time_taken', 0)
                initial_score = result.get('initial_score', 0)
                final_score = result.get('final_score', 0)
                improvement = 0
                if initial_score > 0:
                    improvement = ((final_score - initial_score) / initial_score) * 100

                summary = (
                    f"\n"
                    f"✨ Generation Summary:\n"
                    f"----------------------------\n"
                    f"⏱️ Time Taken: {time_taken:.1f}s\n"
                    f"📊 Initial Score: {initial_score}\n"
                    f"🏆 Final Score: {final_score}\n"
                    f"📈 Improvement: +{improvement:.1f}%\n"
                    f"----------------------------\n"
                )
                self.log_txt.append(summary)
                QMessageBox.information(self, "Success", "Timetable generated and optimized successfully!")
            
            if not result['success']:
                fail_details = []
                for f in result['failed']:
                    group_str = f" ({f['group']})" if f.get('group') else ""
                    fail_details.append(f"• {f['subject']['code']}{group_str} - {f['hours_lost']}hrs lost (Section {f['section_name']})")
                
                self.log_txt.append("\n⚠️ FAILED ASSIGNMENTS:\n" + "\n".join(fail_details))
                QMessageBox.warning(self, "Incomplete Schedule", 
                    f"Timetable generated with {len(result['failed'])} conflicts. See log for details.")
            
            self.btn_view.setVisible(True)
        else:
            QMessageBox.critical(self, "Error", msg)

    def save_data(self):
        pass
