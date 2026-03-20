import sqlite3
import os

def init_db(db_path="saved_tt/timetable_forge.db"):
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS institutions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            working_days TEXT,
            start_time TEXT,
            end_time TEXT,
            slot_duration_mins INTEGER
        );

        CREATE TABLE IF NOT EXISTS breaks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            name TEXT,
            start_time TEXT,
            duration_mins INTEGER
        );

        CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            name TEXT,
            department TEXT,
            subjects TEXT,
            max_teach_hrs INTEGER,
            max_stay_hrs INTEGER,
            available_from TEXT,
            available_till TEXT,
            unavailable_days TEXT,
            constraints_json TEXT
        );

        CREATE TABLE IF NOT EXISTS courses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            name TEXT,
            total_years INTEGER
        );

        CREATE TABLE IF NOT EXISTS sections(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            year INTEGER,
            name TEXT,
            group_name TEXT,
            group_type TEXT
        );

        CREATE TABLE IF NOT EXISTS subjects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            code TEXT,
            name TEXT,
            hours_per_week INTEGER,
            is_lab INTEGER,
            lab_slots INTEGER,
            requires_special_room INTEGER
        );

        CREATE TABLE IF NOT EXISTS subject_group_map(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            group_name TEXT
        );

        CREATE TABLE IF NOT EXISTS teacher_subject_map(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            subject_id INTEGER,
            section_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS rooms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            name TEXT,
            type TEXT,
            capacity INTEGER
        );

        CREATE TABLE IF NOT EXISTS constraint_config(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            config_json TEXT
        );

        CREATE TABLE IF NOT EXISTS timetable_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER,
            subject_id INTEGER,
            teacher_id INTEGER,
            room_id INTEGER,
            day TEXT,
            slot_index INTEGER,
            is_locked INTEGER,
            is_lab INTEGER
        );

        CREATE TABLE IF NOT EXISTS generation_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            created_at TEXT,
            status TEXT,
            warnings_json TEXT,
            failed_subjects_json TEXT
        );

        CREATE TABLE IF NOT EXISTS wizard_draft(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            step INTEGER,
            data_json TEXT
        );
    ''')
    
    conn.commit()
    conn.close()
