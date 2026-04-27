"""
Exam Database Manager - exam_db.py
Handles exam scheduling data persistence and conflict graph generation.
Used by the exam scheduler to store and retrieve exam information.

Functions:
- init_db(): Create exam database schema
- seed_data(): Populate with sample exam data for testing
- get_exams(): Retrieve all exams
- get_conflicts(): Get exam conflict graph (which exams can't be at same time)
- save_schedule(): Save final exam schedule to database

Exam Conflict Types:
- Students taking both exams (must be scheduled differently)
- Teachers invigilating both exams
- Room unavailability
"""

import sqlite3
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "saved_tt", "exams.db")

def init_db():
    save_dir = os.path.join(BASE_DIR, "saved_tt")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conflicts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam1 TEXT,
            exam2 TEXT,
            FOREIGN KEY (exam1) REFERENCES exams(name),
            FOREIGN KEY (exam2) REFERENCES exams(name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_name TEXT,
            slot INTEGER,
            FOREIGN KEY (exam_name) REFERENCES exams(name)
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sample exams
    exams = [("A",), ("B",), ("C",), ("D",), ("E",), ("F",)]
    cursor.executemany("INSERT OR IGNORE INTO exams (name) VALUES (?)", exams)
    
    # Sample conflicts
    conflicts = [
        ("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"), ("F", "A"),
        ("A", "C"), ("B", "D"), ("C", "E"), ("D", "F"), ("E", "A"), ("F", "B")
    ]
    # Check if conflict already exists to avoid duplicates
    for c in conflicts:
        cursor.execute("SELECT * FROM conflicts WHERE (exam1=? AND exam2=?) OR (exam1=? AND exam2=?)", (c[0], c[1], c[1], c[0]))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO conflicts (exam1, exam2) VALUES (?, ?)", c)
    
    conn.commit()
    conn.close()

def get_exams():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM exams")
    exams = [row[0] for row in cursor.fetchall()]
    conn.close()
    return exams

def get_conflicts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT exam1, exam2 FROM conflicts")
    conflicts = cursor.fetchall()
    conn.close()
    return conflicts

def save_schedule(schedule):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedule") # Clear previous
    for exam, slot in schedule.items():
        cursor.execute("INSERT INTO schedule (exam_name, slot) VALUES (?, ?)", (exam, slot))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database initialized and seeded.")
