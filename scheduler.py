"""
Exam Scheduler - scheduler.py
This module handles exam timetable generation using a graph coloring algorithm.
It solves the constraint satisfaction problem of assigning exam time slots such that:
- No two conflicting exams are scheduled in the same slot
- No teacher has overlapping exams
- All exams are assigned a valid slot

Algorithm: Backtracking Graph Coloring
The algorithm treats exams as nodes in a graph where edges connect conflicting exams.
It then assigns colors (time slots) to nodes ensuring no adjacent nodes share a color.
"""

from exam_db import get_exams, get_conflicts, save_schedule, init_db, seed_data

def is_safe(exam, slot, graph, result):
    """
    Check if assigning the given exam to the given slot is safe.
    An assignment is safe if no conflicting exam is already assigned to that slot.
    
    Args:
        exam: Exam identifier
        slot: Time slot number to try
        graph: Dict mapping exam to list of conflicting exams
        result: Dict mapping exams to their assigned slots
    
    Returns:
        True if safe to assign, False otherwise
    """
    # Check if any neighbor of the exam is already assigned the same slot
    for neighbor in graph[exam]:
        if neighbor in result and result[neighbor] == slot:
            return False
    return True

def backtracking_coloring(exams, graph, num_slots, result=None):
    """
    Solve exam scheduling using backtracking graph coloring algorithm.
    
    Args:
        exams: List of exam IDs
        graph: Dict mapping exam ID to list of conflicting exam IDs
        num_slots: Maximum number of available time slots
        result: Dict to store exam->slot assignments (used for recursion)
    
    Returns:
        Dict mapping each exam to its assigned slot, or None if no valid schedule exists
    
    Algorithm:
    1. Base case: If all exams are assigned, return the result
    2. Pick an unassigned exam
    3. Try each time slot (1 to num_slots)
    4. If slot is safe (no conflicts), assign it and recurse
    5. If recursion succeeds, return the result
    6. Otherwise, backtrack and try the next slot
    """
    if result is None:
        result = {}

    # Base case: All exams are assigned a slot
    if len(result) == len(exams):
        return result

    # Pick the next unassigned exam
    current_exam = exams[len(result)]

    # Try assigning each slot from 1 to num_slots
    for slot in range(1, num_slots + 1):
        if is_safe(current_exam, slot, graph, result):
            result[current_exam] = slot
            
            # Recur for the remaining exams
            if backtracking_coloring(exams, graph, num_slots, result):
                return result
            
            # Backtrack if the assignment doesn't lead to a solution
            del result[current_exam]

    return None

def find_optimal_schedule(exams, conflicts):
    # Initialize the graph
    graph = {exam: [] for exam in exams}
    for u, v in conflicts:
        graph[u].append(v)
        graph[v].append(u)

    # Try finding a solution starting from 1 slot upwards
    for num_slots in range(1, len(exams) + 1):
        schedule = backtracking_coloring(exams, graph, num_slots)
        if schedule:
            return schedule, num_slots

if __name__ == "__main__":
    # Ensure DB is ready
    init_db()
    seed_data()
    
    # Step 3: Fetching Data from DB
    exams = get_exams()
    conflicts = get_conflicts()

    print("--- Exam Scheduler (Step 3: Database Integration) ---")
    print(f"Read {len(exams)} exams and {len(conflicts)} conflicts from Database.")
    
    # Process
    schedule, total_slots = find_optimal_schedule(exams, conflicts)

    # Output to Console
    print(f"\nOptimal Schedule Found with {total_slots} Slots:")
    for exam, slot in sorted(schedule.items()):
        print(f"{exam} → Slot {slot}")
        
    # Store results in DB
    save_schedule(schedule)
    print("\nResults saved back to 'schedule' table in Database.")
