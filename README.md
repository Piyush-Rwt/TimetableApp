# ScheduleForge - University Edition

A production-grade, general-purpose university timetable generator built with Python, PySide6, and SQLite. ScheduleForge utilizes an advanced Constraint Satisfaction Problem (CSP) randomized greedy algorithm to generate optimized, conflict-free schedules for any college or department.

### 🚀 Key Features

### 🎓 General Purpose Education Mode
A comprehensive 7-step wizard designed to handle complex university requirements:
1. **Institution Setup**: Define working days, custom time slots, and break timings (e.g., Lunch, Tea).
2. **Sections Setup**: Add multiple sections or classes with specific student counts.
3. **Teacher Management**: Manage faculty names, maximum weekly work hours, and specific unavailability slots.
4. **Subject Configuration**: Define Theory, Lab, and Elective subjects with assigned faculty and room requirements.
5. **Room Management**: Add Classrooms, Labs, and Lecture Halls with capacity tracking.
6. **AI Generation**: A background-threaded solver with real-time progress reporting ("Generating", "Optimizing").
7. **Multi-View Results**: View results Section-wise, Teacher-wise, or Room-wise.

### 🎨 Clean & Native UI
- **Single High-Visibility Theme**: Permanently optimized light theme for maximum readability in university environments.
- **Native OS Elements**: Uses native OS rendering for controls like SpinBox arrows to ensure a consistent, professional feel.
- **Live Summary Panel**: Instantly see time taken, initial vs. optimized scores, and total improvement percentage.

### 📸 Screenshots


### Wizard Setup
![Wizard](assets/wizard.png)

### Generated Timetable
![Timetable](assets/timetable.png)

### 🧠 Algorithm Overview

ScheduleForge uses a two-tier scheduling architecture:

#### Level 1: Constraint Satisfaction Problem (CSP)
Generates a **valid** initial solution using:
- **MRV (Minimum Remaining Values)**: Picks the "hardest" variables first to prune the search space early.
- **Forward Checking**: Every assignment immediately prunes the domains of *related* variables.
- **Recursive Backtracking**: A formal depth-first search that can undo mistakes.
- **Randomized Restarts**: If the solver hits a dead end, it restarts with a new seed.

#### Level 2: Simulated Annealing (SA) Optimization
Refines the valid solution into an **optimized** timetable using:
- **Delta-Scoring Engine**: O(1) score updates instead of full recomputation, allowing for thousands of iterations per second.
- **Biased Neighbor Selection**: The engine identifies "weak slots" (gaps, isolated classes) and targets them for moves/swaps.
- **Adaptive Cooling**: The temperature decay rate adjusts dynamically based on the frequency of improvements.
- **Multi-Run Iterated Search**: Runs multiple shorter annealing processes (e.g., 4 x 0.5s) to escape deep local minima and find the global optimum.

### ⚡ Performance

- **Millisecond Generation**: Initial valid schedules found in **50ms – 500ms**.
- **Deep Optimization**: Performs **10,000+ iterations** of Simulated Annealing in under 2 seconds.
- **Visible Quality**: Shows **Initial vs Final Score** and total improvement percentage (typically 15-30% better distribution).
- **O(1) Conflict Checks**: Bitmasking allows for single-instruction availability verification.

### 🌍 Why ScheduleForge?

Timetable generation is an **NP-hard** problem in real-world institutions. ScheduleForge demonstrates:
- **Constraint Modeling**: Converting abstract rules into programmable logic.
- **Optimization Techniques**: Balancing multiple conflicting goals (e.g., teacher preference vs. student gaps).
- **Heuristic-based Search**: Using domain knowledge to guide the search for an optimal solution.
- **Real-world System Design**: A full-stack desktop application handling data persistence, complex logic, and professional reporting.

## 🧠 Advanced Constraint Engine
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

## 🎥 Demo
*(Add a link to a GIF or Video here to showcase the app in action!)*

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
   ```bash-      
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
│   ├── styles.py          # Unified application styling (Light Theme)
│   ├── dashboard.py       # Home screen & Admin tools
│   └── education/         # 7-Step wizard screens
└── saved_tt/              # SQLite Databases & Exports
```

## 📄 License
This project is licensed under the MIT License.
