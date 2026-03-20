from exam_db import get_exams, get_conflicts, save_schedule, init_db, seed_data

def is_safe(exam, slot, graph, result):
    # Check if any neighbor of the exam is already assigned the same slot
    for neighbor in graph[exam]:
        if neighbor in result and result[neighbor] == slot:
            return False
    return True

def backtracking_coloring(exams, graph, num_slots, result=None):
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
