import sqlite3
import json

DB_PATH = "saved_tt/timetable_forge.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

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
        "institutions", "breaks", "teachers", "courses", "sections", "subjects", 
        "subject_group_map", "teacher_subject_map", "rooms", "constraint_config",
        "timetable_entries", "generation_runs", "wizard_draft"
    ]
    for table in tables:
        c.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()

# Provide helper methods for retrieving/storing individual models.
def execute_query(query, params=(), fetch_all=True):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(query, params)
    if query.strip().upper().startswith("SELECT"):
        res = c.fetchall() if fetch_all else c.fetchone()
    else:
        conn.commit()
        res = c.lastrowid
    conn.close()
    return res

def get_all_teachers():
    return execute_query("SELECT * FROM teachers")

def insert_teacher(data):
    execute_query('''
        INSERT INTO teachers (institution_id, name, department, subjects, max_teach_hrs, max_stay_hrs, available_from, available_till, unavailable_days, constraints_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (1, data.get("name"), data.get("department"), data.get("subjects"), data.get("max_teach_hrs"), data.get("max_stay_hrs"), data.get("available_from"), data.get("available_till"), data.get("unavailable_days"), data.get("constraints_json", "{}")))

def delete_all_teachers():
    execute_query("DELETE FROM teachers")
