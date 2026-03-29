from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt
import db.queries as queries
from engine.excel_exporter import export_full_timetable
import os

class TimetableViewerScreen(QWidget):
    def __init__(self, wizard_cb):
        super().__init__()
        self.wizard_cb = wizard_cb
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Step 7: View & Export Timetable")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.setup_section_view()
        self.setup_teacher_view()
        self.setup_room_view()

        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh View")
        btn_refresh.clicked.connect(self.refresh_all)
        btn_layout.addWidget(btn_refresh)
        
        btn_export = QPushButton("📤 Export All to Excel")
        btn_export.setObjectName("PrimaryButton")
        btn_export.setFixedSize(200, 45)
        btn_export.clicked.connect(self.export_to_excel)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        
        layout.addLayout(btn_layout)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_all()

    def setup_section_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        top = QHBoxLayout()
        top.addWidget(QLabel("Select Section:"))
        self.cmb_section = QComboBox()
        self.cmb_section.currentIndexChanged.connect(self.load_section_tt)
        top.addWidget(self.cmb_section)
        top.addStretch()
        l.addLayout(top)

        self.tbl_sec = self._create_table()
        l.addWidget(self.tbl_sec)
        self.tabs.addTab(w, "Section-wise")

    def setup_teacher_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        top = QHBoxLayout()
        top.addWidget(QLabel("Select Teacher:"))
        self.cmb_teacher = QComboBox()
        self.cmb_teacher.currentIndexChanged.connect(self.load_teacher_tt)
        top.addWidget(self.cmb_teacher)
        top.addStretch()
        l.addLayout(top)

        self.tbl_tea = self._create_table()
        l.addWidget(self.tbl_tea)
        self.tabs.addTab(w, "Teacher-wise")

    def setup_room_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        top = QHBoxLayout()
        top.addWidget(QLabel("Select Room:"))
        self.cmb_room = QComboBox()
        self.cmb_room.currentIndexChanged.connect(self.load_room_tt)
        top.addWidget(self.cmb_room)
        top.addStretch()
        l.addLayout(top)

        self.tbl_room = self._create_table()
        l.addWidget(self.tbl_room)
        self.tabs.addTab(w, "Room-wise")

    def _create_table(self):
        tbl = QTableWidget()
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionMode(QTableWidget.NoSelection)
        tbl.setWordWrap(True)
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
        table.clearContents()
        
        # 1. Mark Breaks
        inst_row = queries.get_institution()
        if not inst_row: return
        breaks = [dict(b) for b in queries.get_breaks()]
        from datetime import datetime
        
        for d_idx, day in enumerate(self.days):
            for s_idx, t_range in enumerate(self.slots_times):
                s_start = datetime.strptime(t_range.split('-')[0], "%H:%M")
                s_end = datetime.strptime(t_range.split('-')[1], "%H:%M")
                is_break = False
                for b in breaks:
                    b_start = datetime.strptime(b['start_time'], "%H:%M")
                    b_end = datetime.strptime(b['end_time'], "%H:%M")
                    if not (s_end <= b_start or s_start >= b_end):
                        is_break = True
                        break
                if is_break:
                    item = QTableWidgetItem("BREAK")
                    item.setBackground(QBrush(QColor("#f39c12")))
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(s_idx, d_idx, item)

        # 2. Fill Entries
        for e in entries:
            try:
                day_name = e['day'].strip()
                if day_name not in self.days: continue
                d_idx = self.days.index(day_name)
                s_idx = e['slot_index']
                
                sub_name = e.get('subject_name') or "Unknown"
                line2 = e.get(line2_key) or "N/A"
                line3 = e.get(line3_key) or "N/A"
                
                text = f"{sub_name}\n({line2})\n[{line3}]"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                
                if e.get('is_lab'): 
                    item.setBackground(QBrush(QColor("#2ecc71")))
                    item.setForeground(QBrush(QColor("#ffffff")))
                else:
                    item.setBackground(QBrush(QColor("#4f6ef7")))
                    item.setForeground(QBrush(QColor("#ffffff")))
                
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
