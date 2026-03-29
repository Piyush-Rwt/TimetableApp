# ScheduleForge - University Edition

A production-grade, general-purpose university timetable generator built with Python, PySide6, and SQLite. ScheduleForge utilizes an advanced Constraint Satisfaction Problem (CSP) randomized greedy algorithm to generate optimized, conflict-free schedules for any college or department.

## 🚀 Key Features

### 🎓 General Purpose Education Mode
A comprehensive 7-step wizard designed to handle complex university requirements:
1. **Institution Setup**: Define working days, custom time slots, and break timings (e.g., Lunch, Tea).
2. **Sections Setup**: Add multiple sections or classes with specific student counts.
3. **Teacher Management**: Manage faculty names, maximum weekly work hours, and specific unavailability slots.
4. **Subject Configuration**: Define Theory, Lab, and Elective subjects with assigned faculty and room requirements.
5. **Room Management**: Add Classrooms, Labs, and Lecture Halls with capacity tracking.
6. **AI Generation**: A background-threaded solver that runs multiple iterations to find the densest possible schedule.
7. **Multi-View Results**: View results Section-wise, Teacher-wise, or Room-wise.

### 🧠 Advanced Constraint Engine
*   **Hard Constraints**:
    *   Zero double-booking for Teachers, Rooms, and Sections.
    *   Automatic Lab splitting (G1/G2) for large sections.
    *   Strict adherence to teacher unavailability and max hour limits.
    *   Consecutive slot allocation for Lab sessions.
    *   Strict room type and capacity verification.
*   **Soft Constraints (Packing Logic)**:
    *   **Compactness**: Prioritizes filling morning slots to minimize gaps.
    *   **Clustering**: Groups subjects together to reduce idle time for students.
    *   **Distribution**: Prevents same-subject clumping on a single day.

### 📊 Professional Export
*   Export the entire generated timetable to a multi-sheet **Excel (.xlsx)** file.
*   Includes beautifully formatted grids for every Section, Teacher, and Room.

### 🛠️ Developer Tools (Admin Mode)
*   A hidden **Admin** button in the bottom-right of the dashboard allows developers to:
    *   **Auto Fill Test Data**: Instantly populate the DB with a realistic university dataset (5 teachers, 4 sections, 7 subjects, 5 rooms).
    *   **Clear All Data**: Wipe the database clean for fresh testing.

## 💻 Tech Stack
*   **GUI**: PySide6 (Qt for Python)
*   **Database**: SQLite
*   **Engine**: Custom CSP Greedy Solver with randomized backtracking
*   **Export**: OpenPyXL

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ScheduleForge.git
   cd ScheduleForge
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## 📂 Project Structure
```text
├── main.py                # Application entry point
├── db/
│   ├── schema.py          # Database table definitions
│   └── queries.py         # SQL CRUD operations
├── engine/
│   ├── constraint_solver.py # Core AI scheduling logic
│   ├── slot_scorer.py     # Soft constraint logic
│   └── excel_exporter.py  # Excel generation logic
├── ui/
│   ├── styles.py          # Global Dark/Light themes
│   ├── dashboard.py       # Home screen & Admin tools
│   └── education/         # 7-Step wizard screens
└── saved_tt/              # SQLite Databases & Exports
```

## 📄 License
This project is licensed under the MIT License.
