# ScheduleForge - Production Edition

A production-grade, multi-purpose desktop scheduling application built with Python, PySide6, and SQLite. ScheduleForge utilizes advanced Constraint Satisfaction Problem (CSP) backtracking algorithms to intelligently generate complex timetables for Personal, Business, and Educational environments.

## 🚀 Key Features

### 1. Multi-Mode Scheduling
- **🧑 Personal Mode**: Manage daily routines, habits, and study plans with priority-based slot distribution and customizable active hours.
- **💼 Business Mode**: Generate shift rosters, allocate staff while respecting maximum working hours, and manage unavailability.
- **🎓 Education Mode**: A comprehensive 7-step wizard for generating full university and school timetables.

### 2. Education Wizard Flow
The application provides a seamless, step-by-step experience for complex academic scheduling:
1. **Initial Course Setup**: Define institution name, courses, years, and section distribution (Standard or Group Mode).
2. **Teacher Upload**: Bulk import teacher availability, maximum hours, and constraints via Excel templates.
3. **Institution Setup**: Configure working days, daily time boundaries, slot durations, and break periods.
4. **Group Setup**: Manage advanced section grouping (Core, Specialization, Electives).
5. **Subject & Room Setup**: Define subjects (Theory/Labs), map them to groups, and import room capacities via Excel.
6. **Constraint Setup**: Fine-tune hard and soft constraints (e.g., max consecutive hours, preferred lab placements).
7. **Generation & Viewer**: Run the backtracking engine in a non-blocking background thread. View results via Section, Teacher, and Master tabs, and export to Excel.

### 3. Advanced CSP Backtracking Engine
- **Hard Constraints**: Prevents double-booking of teachers/rooms/sections, respects break times, and honors specific availability windows.
- **Soft Constraints (Slot Scoring)**: Intelligently minimizes teacher gaps, balances workload across the week, and optimizes lab placements.

### 4. Data Persistence & Export
- **SQLite Database**: All data (configurations, uploaded constraints, generated grids, and wizard drafts) is automatically persisted in `saved_tt/timetable_forge.db`.
- **Excel Export**: Richly formatted `.xlsx` exports powered by `openpyxl` (color-coded, merged cells for labs and breaks).

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd TimetableApp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The primary dependencies are `PySide6` and `openpyxl`)*

3. **Run the application**:
   ```bash
   python main.py
   ```

## 🗺️ Project Structure

```text
/
├── main.py                     # Application entry point
├── db/
│   ├── schema.py               # SQLite schema definitions
│   └── queries.py              # Database helper functions
├── engine/
│   ├── constraint_solver.py    # Backtracking scheduling logic
│   ├── slot_scorer.py          # Soft constraint evaluation
│   └── excel_exporter.py       # openpyxl formatting & export
├── ui/
│   ├── main_window.py          # Core window and stack manager
│   ├── dashboard.py            # Landing screen
│   ├── mode_selector.py        # Mode selection cards
│   ├── personal_mode.py        # Personal scheduling flow
│   ├── business_mode.py        # Business roster flow
│   ├── styles.py               # Centralized QSS dark theme
│   └── education/              # Education wizard screens
│       ├── course_setup_dialog.py
│       ├── teacher_upload.py
│       ├── institution_setup.py
│       ├── section_group_setup.py
│       ├── subject_setup.py
│       ├── constraint_setup.py
│       ├── generate_screen.py
│       └── timetable_viewer.py
└── saved_tt/                   # Local storage for DB and Excel exports
```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
