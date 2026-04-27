"""
Database Schema - schema.py
Defines the SQLite database structure for storing timetable scheduling data.

Tables:
1. institutions: School/university configuration (working days, time slots)
2. breaks: Break periods (lunch, short break, etc.)
3. sections: Student divisions/classes
4. teachers: Staff members teaching classes
5. teacher_unavailability: Slots when teachers are unavailable
6. subjects: Courses/classes to be scheduled
7. rooms: Physical spaces (classrooms, labs)
8. timetable_slots: Final generated schedule assignments

Database Location: saved_tt/timetable_forge.db

Functions:
- init_db(): Create/initialize database with all tables
- clear_all_data(): Reset database (delete all records but keep schema)
"""

import sqlite3
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_DB_PATH = os.path.join(BASE_DIR, "saved_tt", "timetable_forge.db")

def init_db(db_path=DEFAULT_DB_PATH):
    """
    Initialize SQLite database with schema.
    Creates all required tables if they don't already exist.
    
    Args:
        db_path: Path where database file will be created (default: saved_tt/timetable_forge.db)
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
        -- 1. Institution Setup
        CREATE TABLE IF NOT EXISTS institutions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department TEXT,
            semester TEXT,
            working_days TEXT, -- "Monday,Tuesday,..."
            start_time TEXT,    -- "08:00"
            end_time TEXT,      -- "17:00"
            slot_duration_mins INTEGER
        );

        CREATE TABLE IF NOT EXISTS breaks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            name TEXT,
            start_time TEXT,
            end_time TEXT
        );

        -- 2. Sections Setup
        CREATE TABLE IF NOT EXISTS sections(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            name TEXT,
            student_count INTEGER
        );

        -- 3. Teachers Setup
        CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            name TEXT,
            max_hours_per_week INTEGER
        );

        CREATE TABLE IF NOT EXISTS teacher_unavailability(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            day TEXT,
            slot_index INTEGER
        );

        -- 4. Subjects Setup
        CREATE TABLE IF NOT EXISTS subjects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            code TEXT,
            name TEXT,
            type TEXT, -- "Theory", "Lab", "Elective"
            hours_per_week INTEGER,
            teacher_id INTEGER, -- Assigned faculty
            lab_duration INTEGER, -- 1 or 2 slots
            split_groups INTEGER, -- 0 or 1
            room_type_req TEXT    -- "Classroom", "Lab", etc.
        );

        CREATE TABLE IF NOT EXISTS elective_options(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            option_name TEXT,
            teacher_id INTEGER
        );

        -- 5. Rooms Setup
        CREATE TABLE IF NOT EXISTS rooms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution_id INTEGER,
            name TEXT,
            type TEXT, -- "Classroom", "Lab", "Lecture Hall", "Special Venue"
            capacity INTEGER
        );

        -- 6. Generation & Output
        CREATE TABLE IF NOT EXISTS timetable_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER,
            subject_id INTEGER,
            teacher_id INTEGER,
            room_id INTEGER,
            day TEXT,
            slot_index INTEGER,
            is_lab INTEGER,
            elective_option_id INTEGER -- NULL for non-electives
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
