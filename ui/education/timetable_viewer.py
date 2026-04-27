"""
Timetable Viewer Screen - timetable_viewer.py
Step 7 of the Education Wizard: View and export generated timetables.

Features:
- Display timetable in grid format (days × time slots)
- View by section: See all classes for a specific student section
- View by teacher: See all classes for a specific teacher
- View by room: See all classes in a specific room
- Color-coded classes by subject type (Theory=Blue, Lab=Green, Elective=Yellow)
- Export to Excel: Generate professional Excel file with formatted schedules
- Print timetable: Generate PDF/print-ready version

Display:
- Grid layout with days as columns and time slots as rows
- Each cell shows: Subject Code, Teacher Name, Room Number
- Color-coded for easy visual identification
- Hover tooltips showing full details

Export Options:
- Excel workbook with multiple sheets
- One sheet per section, teacher, or room view
- Formatted with colors, borders, and auto-fit columns
- Ready to print or distribute to students/staff
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QMessageBox, QFileDialog, QStackedWidget
)
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt, QTimer, QThread, Signal
import db.queries as queries
from engine.excel_exporter import export_full_timetable
import os

class TableRenderThread(QThread):
    """Background thread to render table data without freezing UI."""
    finished = Signal(list)  # Signal with entries list
    
    def __init__(self, query_func, table_key):
        super().__init__()
        self.query_func = query_func
        self.table_key = table_key
    
    def run(self):
        """Load table entries in background."""
        entries = [dict(e) for e in self.query_func()]
        self.finished.emit(entries)

class TimetableViewerScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        self.is_loading = False
        self.current_tab = 0
        self.render_threads = {}  # Track render threads
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title = QLabel("Step 7: View & Export Timetable")
        title.setObjectName("TitleLabel")
        main_layout.addWidget(title)

        # Loading overlay (positioned over tabs)
        self.loading_overlay = QLabel("⏳ Loading timetable data...")
        self.loading_overlay.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #4f9fbb;
                font-weight: bold;
                background-color: #ffffff;
                border: 2px solid #4f9fbb;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        self.loading_overlay.setAlignment(Qt.AlignCenter)
        self.loading_overlay.setFixedHeight(60)
        self.loading_overlay.hide()
        main_layout.addWidget(self.loading_overlay)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #b0d4e3; }
            QTabBar::tab { 
                background-color: #e0f2f7;
                color: #01579b;
                padding: 8px 20px;
                border: 1px solid #b0d4e3;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected { 
                background-color: #4f9fbb;
                color: #ffffff;
            }
        """)
        # Connect tab change to load data
        self.tabs.currentChanged.connect(self._on_tab_changed)
        main_layout.addWidget(self.tabs)

        self.setup_section_view()
        self.setup_teacher_view()
        self.setup_room_view()

        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh View")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #b3e5fc;
                color: #01579b;
                border: 2px solid #4f9fbb;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81d4fa;
            }
        """)
        btn_refresh.clicked.connect(self._do_refresh_current)
        btn_layout.addWidget(btn_refresh)
        
        btn_export = QPushButton("📤 Export All to Excel")
        btn_export.setObjectName("PrimaryButton")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #4f9fbb;
                color: #ffffff;
                border: 2px solid #2d7a99;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d7a99;
            }
        """)
        btn_export.setFixedSize(200, 45)
        btn_export.clicked.connect(self.export_to_excel)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        
        main_layout.addLayout(btn_layout)
        
        # Timer for loading state
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self._finish_loading)
        
        self.show_loading()
    
    def show_loading(self):
        """Show loading indicator and refresh data."""
        self.is_loading = True
        self.loading_overlay.show()
        self.tabs.setEnabled(False)
        self.loading_timer.start(1500)  # Wait 1.5 seconds before loading
    
    def _finish_loading(self):
        """Hide loading indicator and load current tab."""
        self.loading_timer.stop()
        self.is_loading = False
        self.loading_overlay.hide()
        self.tabs.setEnabled(True)
        self.refresh_all()
    
    def _on_tab_changed(self, tab_index):
        """Handle tab change - show loading and load data."""
        self.current_tab = tab_index
        # Don't reload during initial setup
        if not hasattr(self, 'slots_times'):
            return
        # Show brief loading indicator
        self.loading_overlay.show()
        self.tabs.setEnabled(False)
        QTimer.singleShot(300, self._load_current_tab)
    
    def _load_current_tab(self):
        """Load data for current tab."""
        if self.current_tab == 0:
            self.load_section_tt()
        elif self.current_tab == 1:
            self.load_teacher_tt()
        elif self.current_tab == 2:
            self.load_room_tt()
        self.loading_overlay.hide()
        self.tabs.setEnabled(True)
    
    def _do_refresh_current(self):
        """Refresh current tab."""
        self._load_current_tab()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_all()

    def setup_section_view(self):
        w = QWidget()
        w.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        l = QVBoxLayout(w)
        l.setContentsMargins(10, 10, 10, 10)
        l.setSpacing(10)
        top = QHBoxLayout()
        
        lbl = QLabel("Select Section:")
        lbl.setStyleSheet("color: #01579b; font-weight: bold;")
        top.addWidget(lbl)
        
        self.cmb_section = QComboBox()
        self.cmb_section.setStyleSheet("""
            QComboBox {
                background-color: #b3e5fc;
                color: #01579b;
                border: 2px solid #4f9fbb;
                padding: 6px;
                border-radius: 4px;
            }
        """)
        self.cmb_section.currentIndexChanged.connect(self.load_section_tt)
        top.addWidget(self.cmb_section)
        top.addStretch()
        l.addLayout(top)

        self.tbl_sec = self._create_table()
        l.addWidget(self.tbl_sec)
        self.tabs.addTab(w, "Section-wise")

    def setup_teacher_view(self):
        w = QWidget()
        w.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        l = QVBoxLayout(w)
        l.setContentsMargins(10, 10, 10, 10)
        l.setSpacing(10)
        top = QHBoxLayout()
        
        lbl = QLabel("Select Teacher:")
        lbl.setStyleSheet("color: #01579b; font-weight: bold;")
        top.addWidget(lbl)
        
        self.cmb_teacher = QComboBox()
        self.cmb_teacher.setStyleSheet("""
            QComboBox {
                background-color: #b3e5fc;
                color: #01579b;
                border: 2px solid #4f9fbb;
                padding: 6px;
                border-radius: 4px;
            }
        """)
        self.cmb_teacher.currentIndexChanged.connect(self.load_teacher_tt)
        top.addWidget(self.cmb_teacher)
        top.addStretch()
        l.addLayout(top)

        self.tbl_tea = self._create_table()
        l.addWidget(self.tbl_tea)
        self.tabs.addTab(w, "Teacher-wise")

    def setup_room_view(self):
        w = QWidget()
        w.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        l = QVBoxLayout(w)
        l.setContentsMargins(10, 10, 10, 10)
        l.setSpacing(10)
        top = QHBoxLayout()
        
        lbl = QLabel("Select Room:")
        lbl.setStyleSheet("color: #01579b; font-weight: bold;")
        top.addWidget(lbl)
        
        self.cmb_room = QComboBox()
        self.cmb_room.setStyleSheet("""
            QComboBox {
                background-color: #b3e5fc;
                color: #01579b;
                border: 2px solid #4f9fbb;
                padding: 6px;
                border-radius: 4px;
            }
        """)
        self.cmb_room.currentIndexChanged.connect(self.load_room_tt)
        top.addWidget(self.cmb_room)
        top.addStretch()
        l.addLayout(top)

        self.tbl_room = self._create_table()
        l.addWidget(self.tbl_room)
        self.tabs.addTab(w, "Room-wise")

    def _create_table(self):
        """
        Create a styled QTableWidget with professional light colors and borders.
        Uses light blue backgrounds (#e8f4f8) with distinct borders for differentiation.
        """
        tbl = QTableWidget()
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionMode(QTableWidget.NoSelection)
        tbl.setWordWrap(True)
        tbl.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #b0d4e3;
                border: 1px solid #7ec8e3;
            }
            QTableWidget::item {
                padding: 5px;
                border: 1px solid #b0d4e3;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #4f9fbb;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #2d7a99;
                font-weight: bold;
            }
        """)
        return tbl

    def refresh_all(self):
        inst_row = queries.get_institution()
        if not inst_row: return
        inst = dict(inst_row)
        
        self.days = [d.strip() for d in inst['working_days'].split(',')]
        from datetime import datetime, timedelta
        start = datetime.strptime(inst['start_time'], "%H:%M")
        end = datetime.strptime(inst['end_time'], "%H:%M")
        self.num_slots = int((end - start).total_seconds() / (60 * inst['slot_duration_mins']))
        
        self.slots_times = []
        for i in range(self.num_slots):
            t_start = start + timedelta(minutes=i * inst['slot_duration_mins'])
            t_end = t_start + timedelta(minutes=inst['slot_duration_mins'])
            self.slots_times.append(f"{t_start.strftime('%H:%M')}-{t_end.strftime('%H:%M')}")

        for tbl in [self.tbl_sec, self.tbl_tea, self.tbl_room]:
            tbl.setRowCount(self.num_slots)
            tbl.setColumnCount(len(self.days))
            tbl.setHorizontalHeaderLabels(self.days)
            tbl.setVerticalHeaderLabels(self.slots_times)
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tbl.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Populate combos (Block signals to prevent intermediate triggers)
        self.cmb_section.blockSignals(True)
        self.cmb_section.clear()
        for s in queries.get_all_sections():
            self.cmb_section.addItem(s['name'], s['id'])
        self.cmb_section.blockSignals(False)
        self.cmb_section.setCurrentIndex(0)  # Trigger signal
            
        # Load ALL teachers, not just those with entries
        self.cmb_teacher.blockSignals(True)
        self.cmb_teacher.clear()
        all_teachers = queries.get_all_teachers()
        for t in all_teachers:
            self.cmb_teacher.addItem(t['name'], t['id'])
        self.cmb_teacher.blockSignals(False)
        self.cmb_teacher.setCurrentIndex(0)  # Trigger signal
            
        # Load ALL rooms, not just those with entries
        self.cmb_room.blockSignals(True)
        self.cmb_room.clear()
        all_rooms = queries.get_all_rooms()
        for r in all_rooms:
            self.cmb_room.addItem(r['name'], r['id'])
        self.cmb_room.blockSignals(False)
        self.cmb_room.setCurrentIndex(0)  # Trigger signal

        # Initial load is now triggered by setCurrentIndex(0)

    def load_section_tt(self):
        sid_raw = self.cmb_section.currentData()
        if sid_raw is None or self.cmb_section.currentIndex() < 0:
            self.tbl_sec.clearContents()
            return
        sid = int(sid_raw)
        entries = [dict(e) for e in queries.get_timetable_entries(section_id=sid)]
        print(f"DEBUG: Section View - Dropdown index={self.cmb_section.currentIndex()}, Section ID={sid}, Found {len(entries)} entries")
        self._fill_table(self.tbl_sec, entries, "teacher_name", "room_name")

    def load_teacher_tt(self):
        tid_raw = self.cmb_teacher.currentData()
        if tid_raw is None or self.cmb_teacher.currentIndex() < 0:
            self.tbl_tea.clearContents()  # Clear table if no valid selection
            return
        tid = int(tid_raw)
        entries = [dict(e) for e in queries.get_timetable_entries(teacher_id=tid)]
        print(f"DEBUG: Teacher View - Dropdown index={self.cmb_teacher.currentIndex()}, Teacher ID={tid}, Found {len(entries)} entries")
        self._fill_table(self.tbl_tea, entries, "section_name", "room_name")

    def load_room_tt(self):
        rid_raw = self.cmb_room.currentData()
        if rid_raw is None or self.cmb_room.currentIndex() < 0:
            self.tbl_room.clearContents()
            return
        rid = int(rid_raw)
        entries = [dict(e) for e in queries.get_timetable_entries(room_id=rid)]
        print(f"DEBUG: Room View - Dropdown index={self.cmb_room.currentIndex()}, Room ID={rid}, Found {len(entries)} entries")
        self._fill_table(self.tbl_room, entries, "subject_name", "section_name")

    def _fill_table(self, table, entries, line2_key, line3_key):
        """
        Fill table with entries efficiently. Optimized for fast rendering.
        Only creates items for non-empty cells to improve performance.
        """
        table.clearContents()
        
        # 1. Pre-calculate break slots for this day/slot combination
        inst_row = queries.get_institution()
        if not inst_row: return
        breaks = [dict(b) for b in queries.get_breaks()]
        from datetime import datetime
        
        # Build a set of break slots for O(1) lookup
        break_slots = set()
        for d_idx, day in enumerate(self.days):
            for s_idx, t_range in enumerate(self.slots_times):
                s_start = datetime.strptime(t_range.split('-')[0], "%H:%M")
                s_end = datetime.strptime(t_range.split('-')[1], "%H:%M")
                for b in breaks:
                    b_start = datetime.strptime(b['start_time'], "%H:%M")
                    b_end = datetime.strptime(b['end_time'], "%H:%M")
                    if not (s_end <= b_start or s_start >= b_end):
                        break_slots.add((d_idx, s_idx))
                        break

        # 2. Fill breaks only (don't create items for empty cells)
        for d_idx, s_idx in break_slots:
            item = QTableWidgetItem("BREAK")
            item.setBackground(QBrush(QColor("#ffd89b")))  # Light orange for breaks
            item.setForeground(QBrush(QColor("#8B5A00")))  # Dark orange text
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(QFont("Arial", 10, QFont.Bold))
            table.setItem(s_idx, d_idx, item)

        # 3. Fill Entries (only create items for actual classes)
        for e in entries:
            try:
                day_name = e['day'].strip()
                if day_name not in self.days: continue
                d_idx = self.days.index(day_name)
                s_idx = e['slot_index']
                
                # Skip if already a break
                if (d_idx, s_idx) in break_slots:
                    continue
                
                sub_name = e.get('subject_name') or "Unknown"
                line2 = e.get(line2_key) or "N/A"
                line3 = e.get(line3_key) or "N/A"
                
                text = f"{sub_name}\n({line2})\n[{line3}]"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QFont("Arial", 9))
                
                if e.get('is_lab'): 
                    # Light green for lab classes
                    item.setBackground(QBrush(QColor("#c8e6c9")))
                    item.setForeground(QBrush(QColor("#1b5e20")))
                else:
                    # Light blue for theory classes
                    item.setBackground(QBrush(QColor("#b3e5fc")))
                    item.setForeground(QBrush(QColor("#01579b")))
                
                table.setItem(s_idx, d_idx, item)
            except Exception as err:
                print(f"DEBUG: Viewer Cell Error: {err}")

    def export_to_excel(self):
        try:
            inst_row = queries.get_institution()
            if not inst_row: return
            sections = [dict(s) for s in queries.get_all_sections()]
            subjects = [dict(s) for s in queries.get_all_subjects()]
            teachers = [dict(t) for t in queries.get_all_teachers()]
            rooms = [dict(r) for r in queries.get_all_rooms()]
            entries = [dict(e) for e in queries.get_timetable_entries()]
            
            grid = {s['id']: {d: {i: None for i in range(self.num_slots)} for d in self.days} for s in sections}
            for e in entries:
                grid[e['section_id']][e['day']][e['slot_index']] = {
                    'subject_id': e['subject_id'],
                    'teacher_id': e['teacher_id'],
                    'room_id': e['room_id'],
                    'is_lab': e['is_lab']
                }
            
            breaks = [dict(b) for b in queries.get_breaks()]
            from datetime import datetime
            for d in self.days:
                for s_idx in range(self.num_slots):
                    s_start = datetime.strptime(self.slots_times[s_idx].split('-')[0], "%H:%M")
                    s_end = datetime.strptime(self.slots_times[s_idx].split('-')[1], "%H:%M")
                    for b in breaks:
                        b_start = datetime.strptime(b['start_time'], "%H:%M")
                        b_end = datetime.strptime(b['end_time'], "%H:%M")
                        if not (s_end <= b_start or s_start >= b_end):
                             for sid in grid: grid[sid][d][s_idx] = "BREAK"

            res_obj = {
                'days': self.days,
                'slots_times': [t.split('-') for t in self.slots_times],
                'grid': grid
            }
            
            path, _ = QFileDialog.getSaveFileName(self, "Export Timetable", "", "Excel Files (*.xlsx)")
            if path:
                export_full_timetable(res_obj, sections, subjects, teachers, rooms, path)
                QMessageBox.information(self, "Export Successful", f"Timetable exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error: {str(e)}")

    def save_data(self):
        pass
