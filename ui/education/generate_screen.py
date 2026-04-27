"""
Generate Screen - generate_screen.py
Step 6 of the Education Wizard: Run the scheduling algorithm with smooth loading UI.

Features:
- Animated loading screen (spinner + progress bar)
- Real-time progress updates showing current operation
- Detailed logging of scheduling process
- Smooth animations and transitions
- Handle solver success/failure gracefully

How it works:
1. User clicks "Start Generation" button
2. Beautiful loading overlay appears with spinner animation
3. Solver runs on background thread
4. Progress updates stream to log in real-time (every scheduled subject)
5. Progress bar fills smoothly
6. On completion, results are shown with summary statistics

The solver uses backtracking algorithm with scoring heuristics to find an optimal schedule
that satisfies all hard constraints and optimizes soft preferences.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, 
    QTextEdit, QFrame, QGraphicsOpacityEffect, QStackedWidget
)
from PySide6.QtCore import QThread, Signal, Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QColor
import db.queries as queries
from engine.constraint_solver import ConstraintSolver

class LoadingSpinner(QLabel):
    """Animated loading spinner that rotates."""
    def __init__(self):
        super().__init__()
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_frame = 0
        self.setFont(QFont("Arial", 32))
        self.setAlignment(Qt.AlignCenter)
        self.setText(self.spinner_chars[0])
        
        # Timer to animate spinner
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        
    def start(self):
        """Start the spinning animation."""
        self.timer.start(100)
        
    def stop(self):
        """Stop the spinning animation."""
        self.timer.stop()
        
    def animate(self):
        """Update spinner frame."""
        self.current_frame = (self.current_frame + 1) % len(self.spinner_chars)
        self.setText(self.spinner_chars[self.current_frame])

class GenerationThread(QThread):
    """Background thread that runs the timetable generation solver."""
    progress = Signal(int, str)  # (percentage, message)
    finished = Signal(bool, str, object)  # (success, message, result)

    def run(self):
        try:
            # ===== STEP 1: Data Loading =====
            self.progress.emit(5, "📦 Loading institution configuration...")
            inst_row = queries.get_institution()
            if not inst_row:
                self.finished.emit(False, "No institution setup found.", None)
                return
            inst = dict(inst_row)
            
            self.progress.emit(10, "📚 Loading breaks schedule...")
            breaks = [dict(b) for b in queries.get_breaks()]
            
            self.progress.emit(12, "👥 Loading student sections...")
            sections = [dict(s) for s in queries.get_all_sections()]
            
            self.progress.emit(14, "👨‍🏫 Loading teachers...")
            teachers = [dict(t) for t in queries.get_all_teachers()]
            
            self.progress.emit(16, "📝 Loading subjects...")
            subjects = [dict(s) for s in queries.get_all_subjects()]
            
            self.progress.emit(18, "🏛️ Loading rooms...")
            rooms = [dict(r) for r in queries.get_all_rooms()]
            
            self.progress.emit(20, "🚫 Loading teacher unavailability...")
            unav = []
            for t in teachers:
                unav.extend([dict(u) for u in queries.get_teacher_unavailability(t['id'])])
            
            elective_opts = []
            
            # Validation
            if not sections or not subjects or not rooms:
                self.finished.emit(False, "❌ Missing data: sections, subjects, or rooms.", None)
                return

            self.progress.emit(25, f"✅ Data loaded successfully!\n   • Sections: {len(sections)}\n   • Teachers: {len(teachers)}\n   • Subjects: {len(subjects)}\n   • Rooms: {len(rooms)}")

            # ===== STEP 2: Solver Initialization =====
            self.progress.emit(30, "⚙️ Initializing scheduling engine...")
            solver = ConstraintSolver(inst, breaks, sections, teachers, unav, subjects, elective_opts, rooms)
            
            self.progress.emit(35, "🔄 Building assignment list and sorting by difficulty...")
            
            # ===== STEP 3: Base Schedule Generation (CSP) =====
            self.progress.emit(40, "🎯 Starting base timetable generation (CSP Algorithm)...")
            import time
            start_time = time.time()
            res = solver.run_iteration()
            
            # Count scheduled subjects
            scheduled_count = 0
            if res.get('grid'):
                for sec_id, days in res['grid'].items():
                    for day, slots in days.items():
                        for slot_idx, entry in slots.items():
                            if entry and isinstance(entry, dict):
                                scheduled_count += 1
            
            self.progress.emit(50, f"✨ Base schedule complete! Scheduled {scheduled_count} slots")

            # ===== STEP 4: Optimization (Simulated Annealing) =====
            if res['success']:
                self.progress.emit(55, "🔥 Starting optimization phase (Simulated Annealing)...")
                self.progress.emit(60, "📊 Calculating initial schedule quality score...")
                initial_score = solver.calculate_total_score(res['assignment'])
                
                self.progress.emit(65, f"Initial quality score: {initial_score:.0f}")
                self.progress.emit(70, "🎨 Refining schedule for better distribution...")
                
                optimized_assignment = solver.optimize(res['assignment'], total_time_limit=2.0)
                res['assignment'] = optimized_assignment
                res['grid'] = solver.section_grid
                
                self.progress.emit(80, "🏆 Recalculating optimized quality score...")
                final_score = solver.calculate_total_score(optimized_assignment)
                res['initial_score'] = initial_score
                res['final_score'] = final_score
                
                # Calculate improvement
                improvement_pct = 0
                if initial_score > 0:
                    improvement_pct = ((final_score - initial_score) / initial_score) * 100
                
                self.progress.emit(85, f"✅ Optimization complete! Improvement: {improvement_pct:+.1f}%")
            else:
                res['initial_score'] = 0
                res['final_score'] = 0
                self.progress.emit(55, "⚠️ Could not generate base schedule, skipping optimization...")
                
            res['time_taken'] = time.time() - start_time
            result = res
            
            # ===== STEP 5: Database Persistence =====
            self.progress.emit(88, "💾 Persisting results to database...")
            queries.clear_timetable_entries()
            
            persisted_count = 0
            if result.get('grid'):
                for sec_id, days in result['grid'].items():
                    for day, slots in days.items():
                        for slot_idx, entry in slots.items():
                            if entry and isinstance(entry, dict):
                                t_id = int(entry.get('teacher_id') or 0)
                                s_id = int(entry.get('subject_id') or 0)
                                r_id = int(entry.get('room_id') or 0)
                                
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
                                persisted_count += 1
            
            self.progress.emit(95, f"Persisted {persisted_count} schedule entries")
            
            # ===== STEP 6: Final Status =====
            if not result['success']:
                self.progress.emit(98, f"⚠️ Warning: {len(result.get('failed', []))} subjects could not be scheduled")
            
            self.progress.emit(100, "✅ Generation complete! Ready to view results.")
            self.finished.emit(True, "Generation complete.", result)
            
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            print(f"ERROR: {err_msg}")
            self.progress.emit(100, f"❌ Error occurred!")
            self.finished.emit(False, f"Error: {str(e)}\n\n{err_msg}", None)

class GenerateScreen(QWidget):
    """Main screen for generating timetables with smooth loading animation."""
    
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        self.generation_thread = None
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("Step 6: Generate Timetable")
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)

        subtitle = QLabel("Click 'Start Generation' to begin. The algorithm will create an optimized, conflict-free schedule.")
        subtitle.setObjectName("SubtitleLabel")
        main_layout.addWidget(subtitle)

        # Stacked widget for switching between start screen and loading/results
        self.stacked_widget = QStackedWidget()
        
        # ===== SCREEN 0: Start Screen =====
        start_screen = self._create_start_screen()
        self.stacked_widget.addWidget(start_screen)
        
        # ===== SCREEN 1: Loading Screen =====
        loading_screen = self._create_loading_screen()
        self.stacked_widget.addWidget(loading_screen)
        
        # ===== SCREEN 2: Results Screen =====
        results_screen = self._create_results_screen()
        self.stacked_widget.addWidget(results_screen)
        
        main_layout.addWidget(self.stacked_widget)
        main_layout.addStretch()

    def _create_start_screen(self):
        """Create the initial screen shown before generation starts."""
        screen = QFrame()
        screen.setObjectName("Card")
        layout = QVBoxLayout(screen)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        info_label = QLabel(
            "Before generating, ensure you have configured:\n"
            "✓ Institution details (working days, time slots)\n"
            "✓ Student sections\n"
            "✓ Teachers and their availability\n"
            "✓ Subjects and assignments\n"
            "✓ Rooms (classrooms and labs)\n\n"
            "The solver will create an optimal schedule using advanced algorithms."
        )
        info_label.setStyleSheet("""
            QLabel {
                color: #01579b;
                font-size: 14px;
                line-height: 1.6;
                background-color: #e3f2fd;
                padding: 15px;
                border: 2px solid #4f9fbb;
                border-radius: 5px;
            }
        """)
        layout.addWidget(info_label)
        
        self.btn_start = QPushButton("🚀 Start Generation Now")
        self.btn_start.setObjectName("PrimaryButton")
        self.btn_start.setFixedHeight(50)
        self.btn_start.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4f9fbb;
                color: #ffffff;
                border: 2px solid #2d7a99;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2d7a99;
            }
        """)
        self.btn_start.clicked.connect(self.start_generation)
        layout.addWidget(self.btn_start)
        
        layout.addStretch()
        return screen

    def _create_loading_screen(self):
        """Create the smooth loading screen with spinner and progress."""
        screen = QFrame()
        layout = QVBoxLayout(screen)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.addStretch()
        
        # Spinner
        self.spinner = LoadingSpinner()
        self.spinner.setStyleSheet("color: #4f9fbb;")
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Status text
        self.loading_status = QLabel("Initializing...")
        self.loading_status.setAlignment(Qt.AlignCenter)
        self.loading_status.setFont(QFont("Arial", 13))
        self.loading_status.setStyleSheet("color: #01579b; font-weight: bold;")
        layout.addWidget(self.loading_status)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e8f4f8;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #4f9fbb;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Percentage
        self.progress_percent = QLabel("0%")
        self.progress_percent.setAlignment(Qt.AlignCenter)
        self.progress_percent.setFont(QFont("Arial", 11))
        self.progress_percent.setStyleSheet("color: #01579b; font-weight: bold;")
        layout.addWidget(self.progress_percent)
        
        # Log output
        self.log_txt = QTextEdit()
        self.log_txt.setReadOnly(True)
        self.log_txt.setMinimumHeight(200)
        self.log_txt.setMaximumHeight(250)
        self.log_txt.setStyleSheet("""
            QTextEdit {
                background-color: #0f1117;
                color: #8b8fa8;
                border: 1px solid #2a2d3e;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_txt)
        
        layout.addStretch()
        return screen

    def _create_results_screen(self):
        """Create the results screen shown after generation completes."""
        screen = QFrame()
        screen.setObjectName("Card")
        layout = QVBoxLayout(screen)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.results_label = QLabel()
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("font-size: 14px; line-height: 1.8;")
        layout.addWidget(self.results_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_view = QPushButton("📊 View Timetable")
        self.btn_view.setFixedHeight(45)
        self.btn_view.setStyleSheet("""
            QPushButton {
                background-color: #4f9fbb;
                color: #ffffff;
                border: 2px solid #2d7a99;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d7a99;
            }
        """)
        self.btn_view.clicked.connect(self._on_view_results)
        button_layout.addWidget(self.btn_view)
        
        self.btn_regenerate = QPushButton("🔄 Generate Again")
        self.btn_regenerate.setFixedHeight(45)
        self.btn_regenerate.setStyleSheet("""
            QPushButton {
                background-color: #c8e6c9;
                color: #1b5e20;
                border: 2px solid #558b2f;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a5d6a7;
            }
        """)
        self.btn_regenerate.clicked.connect(self.start_generation)
        button_layout.addWidget(self.btn_regenerate)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return screen

    def start_generation(self):
        """Start the generation process and show loading screen."""
        # Show loading screen
        self.stacked_widget.setCurrentIndex(1)
        self.spinner.start()
        self.log_txt.clear()
        self.progress_bar.setValue(0)
        
        # Create and start generation thread
        self.generation_thread = GenerationThread()
        self.generation_thread.progress.connect(self.update_progress)
        self.generation_thread.finished.connect(self.generation_finished)
        self.generation_thread.start()

    def update_progress(self, percentage, message):
        """Update progress bar and log with new message."""
        self.progress_bar.setValue(percentage)
        self.progress_percent.setText(f"{percentage}%")
        self.log_txt.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.log_txt.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def generation_finished(self, success, message, result):
        """Handle generation completion."""
        self.spinner.stop()
        
        if success and result:
            if result['success']:
                # Successful generation with optimal schedule
                time_taken = result.get('time_taken', 0)
                initial_score = result.get('initial_score', 0)
                final_score = result.get('final_score', 0)
                improvement = 0
                if initial_score > 0:
                    improvement = ((final_score - initial_score) / initial_score) * 100

                results_text = (
                    f"<b>✅ Timetable Generated Successfully!</b><br><br>"
                    f"<b>Generation Summary:</b><br>"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                    f"⏱️  <b>Time Taken:</b> {time_taken:.2f} seconds<br>"
                    f"📊 <b>Initial Score:</b> {initial_score:.0f}<br>"
                    f"🏆 <b>Final Score:</b> {final_score:.0f}<br>"
                    f"📈 <b>Optimization:</b> <span style='color: #2ecc71;'>{improvement:+.1f}%</span><br>"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br><br>"
                    f"Your timetable is ready to view and export!"
                )
                
                self.log_txt.append(
                    "\n" + "="*50 + "\n"
                    f"✨ GENERATION COMPLETE ✨\n"
                    f"{'='*50}\n"
                    f"Time: {time_taken:.2f}s | Score: {final_score:.0f} | Improvement: {improvement:+.1f}%"
                )
                
                self.results_label.setText(results_text)
            else:
                # Generation failed to create complete schedule
                fail_details = []
                for f in result.get('failed', []):
                    group_str = f" ({f['group']})" if f.get('group') else ""
                    fail_details.append(f"• {f['subject']['code']}{group_str}")
                
                fail_text = "\n".join(fail_details[:5])  # Show first 5
                if len(result.get('failed', [])) > 5:
                    fail_text += f"\n... and {len(result['failed']) - 5} more"
                
                results_text = (
                    f"<b>⚠️  Incomplete Schedule Generated</b><br><br>"
                    f"<b>Details:</b><br>"
                    f"• Total conflicts: {len(result.get('failed', []))}<br>"
                    f"• Failed assignments:<br>"
                    f"<pre>{fail_text}</pre><br>"
                    f"Try adjusting constraints or adding more resources."
                )
                self.results_label.setText(results_text)
                
                self.log_txt.append(
                    "\n" + "="*50 + "\n"
                    f"⚠️ GENERATION COMPLETE WITH {len(result.get('failed', []))} CONFLICTS ⚠️\n"
                    f"{'='*50}"
                )
        else:
            # Error occurred
            results_text = (
                f"<b>❌ Generation Failed</b><br><br>"
                f"<b>Error:</b><br>"
                f"{message}"
            )
            self.results_label.setText(results_text)
            
            self.log_txt.append(
                "\n" + "="*50 + "\n"
                f"❌ ERROR ❌\n"
                f"{'='*50}\n"
                f"{message}"
            )
        
        # Show results screen after 2 second delay (lets user see completion)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.stacked_widget.setCurrentIndex(2))

    def _on_view_results(self):
        """Navigate to timetable viewer."""
        self.wizard_cb(6)
