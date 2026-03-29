import os
import sys
import sqlite3
import json

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "saved_tt", "timetable_forge.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def execute_query(query, params=(), fetch_all=True):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(query, params)
    if query.strip().upper().startswith("SELECT"):
        if fetch_all:
            res = [dict(row) for row in c.fetchall()]
        else:
            row = c.fetchone()
            res = dict(row) if row else None
    else:
        conn.commit()
        res = c.lastrowid
    conn.close()
    return res

# --- 1. Institution Setup ---
def get_institution(institution_id=1):
    return execute_query("SELECT * FROM institutions WHERE id = ?", (institution_id,), fetch_all=False)

def update_institution(data, institution_id=1):
    execute_query('''
        INSERT OR REPLACE INTO institutions (id, name, department, semester, working_days, start_time, end_time, slot_duration_mins)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (institution_id, data.get("name"), data.get("department"), data.get("semester"), data.get("working_days"), data.get("start_time"), data.get("end_time"), data.get("slot_duration_mins")))

def get_breaks(institution_id=1):
    return execute_query("SELECT * FROM breaks WHERE institution_id = ?", (institution_id,))

def insert_break(data, institution_id=1):
    execute_query("INSERT INTO breaks (institution_id, name, start_time, end_time) VALUES (?, ?, ?, ?)", 
                  (institution_id, data.get("name"), data.get("start_time"), data.get("end_time")))

def delete_all_breaks(institution_id=1):
    execute_query("DELETE FROM breaks WHERE institution_id = ?", (institution_id,))

# --- 2. Sections ---
def get_all_sections(institution_id=1):
    return execute_query("SELECT * FROM sections WHERE institution_id = ?", (institution_id,))

def insert_section(data, institution_id=1):
    execute_query("INSERT INTO sections (institution_id, name, student_count) VALUES (?, ?, ?)", 
                  (institution_id, data.get("name"), data.get("student_count")))

def delete_all_sections(institution_id=1):
    execute_query("DELETE FROM sections WHERE institution_id = ?", (institution_id,))

# --- 3. Teachers ---
def get_all_teachers(institution_id=1):
    return execute_query("SELECT * FROM teachers WHERE institution_id = ?", (institution_id,))

def insert_teacher(data, institution_id=1):
    return execute_query("INSERT INTO teachers (institution_id, name, max_hours_per_week) VALUES (?, ?, ?)", 
                         (institution_id, data.get("name"), data.get("max_hours_per_week")))

def insert_teacher_unavailability(teacher_id, day, slot_index):
    execute_query("INSERT INTO teacher_unavailability (teacher_id, day, slot_index) VALUES (?, ?, ?)", 
                  (teacher_id, day, slot_index))

def get_teacher_unavailability(teacher_id):
    return execute_query("SELECT * FROM teacher_unavailability WHERE teacher_id = ?", (teacher_id,))

def delete_all_teachers(institution_id=1):
    execute_query("DELETE FROM teachers WHERE institution_id = ?", (institution_id,))
    execute_query("DELETE FROM teacher_unavailability WHERE teacher_id NOT IN (SELECT id FROM teachers)")

def update_teacher(teacher_id, data):
    execute_query('''
        UPDATE teachers SET name = ?, max_hours_per_week = ?
        WHERE id = ?
    ''', (data.get("name"), data.get("max_hours_per_week"), int(teacher_id)))

def delete_teacher(teacher_id):
    execute_query("DELETE FROM teachers WHERE id = ?", (int(teacher_id),))
    execute_query("DELETE FROM teacher_unavailability WHERE teacher_id = ?", (int(teacher_id),))

# --- 4. Subjects ---
def get_all_subjects(institution_id=1):
    return execute_query("SELECT * FROM subjects WHERE institution_id = ?", (institution_id,))

def insert_subject(data, institution_id=1):
    return execute_query('''
        INSERT INTO subjects (institution_id, code, name, type, hours_per_week, teacher_id, lab_duration, split_groups, room_type_req)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (institution_id, data.get("code"), data.get("name"), data.get("type"), data.get("hours_per_week"), data.get("teacher_id"), 
          data.get("lab_duration"), data.get("split_groups"), data.get("room_type_req")))

def insert_elective_option(subject_id, option_name, teacher_id):
    execute_query("INSERT INTO elective_options (subject_id, option_name, teacher_id) VALUES (?, ?, ?)", 
                  (subject_id, option_name, teacher_id))

def get_elective_options(subject_id):
    return execute_query("SELECT * FROM elective_options WHERE subject_id = ?", (subject_id,))

def delete_all_subjects(institution_id=1):
    execute_query("DELETE FROM subjects WHERE institution_id = ?", (institution_id,))
    execute_query("DELETE FROM elective_options WHERE subject_id NOT IN (SELECT id FROM subjects)")

# --- 5. Rooms ---
def get_all_rooms(institution_id=1):
    return execute_query("SELECT * FROM rooms WHERE institution_id = ?", (institution_id,))

def insert_room(data, institution_id=1):
    execute_query("INSERT INTO rooms (institution_id, name, type, capacity) VALUES (?, ?, ?, ?)", 
                  (institution_id, data.get("name"), data.get("type"), data.get("capacity")))

def delete_all_rooms(institution_id=1):
    execute_query("DELETE FROM rooms WHERE institution_id = ?", (institution_id,))

# --- 6. Timetable Entries ---
def clear_timetable_entries():
    execute_query("DELETE FROM timetable_entries")

def insert_timetable_entry(data):
    execute_query('''
        INSERT INTO timetable_entries (section_id, subject_id, teacher_id, room_id, day, slot_index, is_lab, elective_option_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['section_id'], data['subject_id'], data['teacher_id'], data['room_id'], data['day'], data['slot_index'], data.get('is_lab', 0), data.get('elective_option_id')))

def get_timetable_entries(section_id=None, teacher_id=None, room_id=None):
    query = '''
        SELECT t.*, s.name as subject_name, s.code as subject_code, 
               tea.name as teacher_name, r.name as room_name, sec.name as section_name
        FROM timetable_entries t
        LEFT JOIN subjects s ON t.subject_id = s.id
        LEFT JOIN teachers tea ON t.teacher_id = tea.id
        LEFT JOIN rooms r ON t.room_id = r.id
        LEFT JOIN sections sec ON t.section_id = sec.id
        WHERE 1=1
    '''
    params = []
    if section_id is not None:
        query += " AND t.section_id = ?"
        params.append(int(section_id))
    if teacher_id is not None:
        query += " AND t.teacher_id = ?"
        params.append(int(teacher_id))
    if room_id is not None:
        query += " AND t.room_id = ?"
        params.append(int(room_id))
        
    return execute_query(query, tuple(params))

def get_teachers_with_entries():
    return execute_query('''
        SELECT DISTINCT tea.id, tea.name 
        FROM timetable_entries t
        JOIN teachers tea ON t.teacher_id = tea.id
        ORDER BY tea.name
    ''')

def get_rooms_with_entries():
    return execute_query('''
        SELECT DISTINCT r.id, r.name
        FROM timetable_entries t  
        JOIN rooms r ON t.room_id = r.id
        ORDER BY r.name
    ''')

# --- 7. Wizard Drafts ---
def save_draft(step, data_json, institution_id=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM wizard_draft WHERE step = ? AND institution_id = ?", (step, institution_id))
    row = c.fetchone()
    if row:
        c.execute("UPDATE wizard_draft SET data_json = ? WHERE step = ? AND institution_id = ?", (data_json, step, institution_id))
    else:
        c.execute("INSERT INTO wizard_draft (institution_id, step, data_json) VALUES (?, ?, ?)", (institution_id, step, data_json))
    conn.commit()
    conn.close()

def get_draft(step, institution_id=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT data_json FROM wizard_draft WHERE step = ? AND institution_id = ?", (step, institution_id))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def clear_all_data():
    conn = get_connection()
    c = conn.cursor()
    tables = [
        "institutions", "breaks", "teachers", "teacher_unavailability", "sections", "subjects", 
        "elective_options", "rooms", "timetable_entries", "wizard_draft"
    ]
    for table in tables:
        c.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
