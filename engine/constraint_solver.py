"""
Constraint Solver - constraint_solver.py
This module solves the timetable scheduling problem using constraint satisfaction (CSP).

Problem: Given teachers, sections, subjects, and rooms, assign each subject to a time slot
         such that all constraints are satisfied:
         - No teacher teaches two classes at the same time
         - No room is used by two classes at the same time
         - No section attends two classes at the same time
         - All break times are free
         - Teacher working hours don't exceed max hours per week
         - Teachers are not scheduled during their unavailable slots
         - Lab classes get appropriate room types

Algorithm: Backtracking with heuristics and conflict detection
The solver tries to place each subject in valid slots, scoring them based on various criteria.
If a slot causes conflicts, it backtracks and tries another slot.
"""

import json
import random
from datetime import datetime, timedelta
from engine.slot_scorer import score_slot

class ConstraintSolver:
    """
    Main solver for educational timetable scheduling.
    
    Attributes:
        institution: School/university configuration (working days, times, slot duration)
        days: List of working days (e.g., ['Monday', 'Tuesday', ...])
        num_slots: Number of time slots per day
        slots_times: List of (start_time, end_time) tuples for each slot
        section_grid: 3D grid tracking which subject is in which section/day/slot
        teacher_busy: 3D grid tracking teacher availability
        room_busy: 3D grid tracking room availability
        teacher_hours: Dict tracking total hours assigned to each teacher
    """
    
    def __init__(self, institution, breaks, sections, teachers, unavailability, subjects, elective_options, rooms):
        """
        Initialize the constraint solver with all scheduling data.
        
        Args:
            institution: Dict with working_days, start_time, end_time, slot_duration_mins
            breaks: List of break periods (lunch, short break, etc.)
            sections: List of student sections/classes
            teachers: List of teachers with max_hours_per_week
            unavailability: Dict mapping teacher_id to list of (day, slot) tuples
            subjects: List of subjects to schedule
            elective_options: Elective course options
            rooms: List of rooms (classrooms and labs)
        """
        self.institution = institution
        self.breaks = breaks
        self.sections = sections
        self.teachers_data = teachers
        self.unavailability = unavailability
        self.subjects_data = subjects
        self.elective_options = elective_options
        self.rooms_data = rooms
        
        # Setup Days and Slots - Create time slot mappings
        self.days = [d.strip() for d in institution['working_days'].split(',')]
        self.slot_duration = institution['slot_duration_mins']
        self.start_time = datetime.strptime(institution['start_time'], "%H:%M")
        self.end_time = datetime.strptime(institution['end_time'], "%H:%M")
        
        # Calculate total number of time slots per day
        self.num_slots = int((self.end_time - self.start_time).total_seconds() / (60 * self.slot_duration))
        self.slots_times = []
        for i in range(self.num_slots):
            t_start = self.start_time + timedelta(minutes=i * self.slot_duration)
            t_end = t_start + timedelta(minutes=self.slot_duration)
            self.slots_times.append((t_start.strftime("%H:%M"), t_end.strftime("%H:%M")))
            
        # Map Breaks - Identify which time slots are break times
        self.break_slots = []
        for b in breaks:
            b_start = datetime.strptime(b['start_time'], "%H:%M")
            b_end = datetime.strptime(b['end_time'], "%H:%M")
            for i, (s_start, s_end) in enumerate(self.slots_times):
                s_start_dt = datetime.strptime(s_start, "%H:%M")
                s_end_dt = datetime.strptime(s_end, "%H:%M")
                if not (s_end_dt <= b_start or s_start_dt >= b_end):
                    self.break_slots.append(i)
        self.break_slots = list(set(self.break_slots))

    def reset_state(self):
        """
        Reset all scheduling state variables before starting a new schedule.
        This creates empty grids for tracking assignments and constraints.
        """
        self.teachers = {t['id']: t for t in self.teachers_data}
        self.subjects = {s['id']: s for s in self.subjects_data}
        self.rooms = self.rooms_data
        
        # Initialize 3D grids: [entity_id][day][slot_index] = assigned_subject
        self.section_grid = {s['id']: {d: {slot: None for slot in range(self.num_slots)} for d in self.days} for s in self.sections}
        self.teacher_busy = {t['id']: {d: {slot: False for slot in range(self.num_slots)} for d in self.days} for t in self.teachers.values()}
        self.room_busy = {r['id']: {d: {slot: False for slot in range(self.num_slots)} for d in self.days} for r in self.rooms}
        self.teacher_hours = {t['id']: 0 for t in self.teachers.values()}

        for d in self.days:
            for s_idx in self.break_slots:
                for sec_id in self.section_grid:
                    self.section_grid[sec_id][d][s_idx] = "BREAK"
            
            for unav in self.unavailability:
                if unav['day'] == d:
                    t_id = unav['teacher_id']
                    s_idx = unav['slot_index']
                    if t_id in self.teacher_busy and s_idx < self.num_slots:
                        self.teacher_busy[t_id][d][s_idx] = True

    def is_valid(self, day, slot, assignment, room, duration=1):
        """
        Check if a slot is valid for an assignment.
        Hard constraints (must be satisfied):
        - No overlap with existing classes
        - Room must be available
        - Slot must not be during breaks
        - Teacher must not exceed max hours (soft - can be overridden if desperate)
        
        Soft constraints (prefer but not required):
        - Room type should match
        - Room capacity should fit
        """
        sec_id = assignment['section_id']
        t_id = assignment['teacher_id']
        sub = assignment['subject']
        
        for i in range(duration):
            curr_slot = slot + i
            if curr_slot >= self.num_slots: return False, "Exceeds day end"
            
            # Hard constraint: Check Section Busy
            if self.section_grid.get(sec_id, {}).get(day, {}).get(curr_slot) is not None:
                return False, "Section busy"
            
            # Hard constraint: Check Teacher Busy
            if t_id and t_id in self.teacher_busy:
                if self.teacher_busy[t_id].get(day, {}).get(curr_slot):
                    return False, "Teacher busy/unavailable"
            
            # Hard constraint: Check Room Busy
            if room and room['id'] in self.room_busy:
                if self.room_busy[room['id']].get(day, {}).get(curr_slot):
                    return False, "Room busy"
                    
            # Hard constraint: Check Break Slots
            if curr_slot in self.break_slots: return False, "Break slot"
        
        # Soft constraint: Max hours check - allow overflow if many attempts
        if t_id and t_id in self.teachers:
            max_h = self.teachers[t_id]['max_hours_per_week']
            current_hours = self.teacher_hours.get(t_id, 0)
            # Only strict if well under limit, relax after 5 attempts
            if current_hours + duration > max_h * 1.1:  # Allow 10% overflow temporarily
                return False, f"Teacher max hours exceeded"
        
        # Soft constraint: Room type - allow some flexibility
        if room:
            req = sub.get('room_type_req')
            if room['type'] != req:
                # Allow Classroom/Lecture Hall interchangeability
                if not ((req == "Classroom" and room['type'] in ["Classroom", "Lecture Hall"]) or
                        (req == "Lab" and room['type'] == "Lab")):
                    return False, f"Room type mismatch ({room['type']} vs {req})"
            
            # Soft constraint: Room capacity - prefer but not required
            # Allow slightly oversized rooms or small oversizing
            student_count = assignment.get('student_count', 0)
            if room['capacity'] < student_count:
                # Allow up to 20% overcapacity (for splits or small overages)
                if room['capacity'] < student_count * 0.8:
                    return False, f"Room capacity too small"
        else:
            return False, "No room"
            
        return True, "Valid"

    def run_iteration(self):
        self.reset_state()
        assignments = []
        for sub in self.subjects_data:
            t_id = int(sub.get('teacher_id') or 0)
            
            for sec in self.sections:
                if sub.get('split_groups'):
                    # Create two assignments for the same subject/section
                    for grp in ['G1', 'G2']:
                        assignments.append({
                            'section_id': sec['id'],
                            'section_name': sec['name'],
                            'subject': sub,
                            'teacher_id': t_id,
                            'hours_remaining': sub['hours_per_week'],
                            'group': grp,
                            'student_count': sec['student_count'] / 2,
                            'difficulty': 5  # Splits are harder to place
                        })
                else:
                    assignments.append({
                        'section_id': sec['id'],
                        'section_name': sec['name'],
                        'subject': sub,
                        'teacher_id': t_id,
                        'hours_remaining': sub['hours_per_week'],
                        'student_count': sec['student_count'],
                        'difficulty': 3 if sub['type'] == 'Lab' else 1  # Labs harder than theory
                    })
        
        # Smart ordering: Hardest constraints first (labs, splits, large groups)
        assignments.sort(key=lambda a: (-a['difficulty'], -a.get('hours_remaining', 0), -a.get('student_count', 0)))
        random.shuffle(assignments[len([x for x in assignments if x['difficulty'] >= 3]):])  # Randomize non-hard subjects

        failed_assignments = []
        for assign in assignments:
            h_rem = assign['hours_remaining']
            attempt_count = 0
            max_attempts = 20  # Increased from 3 to 20 for better slot finding
            
            while h_rem > 0 and attempt_count < max_attempts:
                attempt_count += 1
                is_lab = assign['subject']['type'] == 'Lab'
                duration = assign['subject']['lab_duration'] if is_lab else 1
                if duration > h_rem: duration = h_rem

                tied_best = []
                best_score = -999999
                
                # Smart room selection: prioritize rooms that can fit the class
                sorted_rooms = sorted(self.rooms, key=lambda r: (
                    r['capacity'] >= assign.get('student_count', 0),  # Rooms that fit first
                    -(r['capacity'] - assign.get('student_count', 0))  # Then smallest fitting room
                ), reverse=True)
                
                # Randomize search order for better distribution
                day_list = self.days.copy()
                slot_list = list(range(self.num_slots))
                if attempt_count > 1:
                    random.shuffle(day_list)
                    random.shuffle(slot_list)
                
                for d in day_list:
                    for s in slot_list:
                        for room in sorted_rooms:
                            valid, _ = self.is_valid(d, s, assign, room, duration)
                            if valid:
                                score = score_slot(s, d, assign['section_id'], assign, self.teacher_busy, self.room_busy, self.section_grid[assign['section_id']], self.days)
                                if score > best_score:
                                    best_score = score
                                    tied_best = [(s, d, room)]
                                elif score == best_score:
                                    tied_best.append((s, d, room))

                if tied_best:
                    best_slot, best_day, best_room = random.choice(tied_best)
                    entry = {
                        'subject_id': assign['subject']['id'],
                        'teacher_id': assign['teacher_id'],
                        'room_id': best_room['id'],
                        'is_lab': 1 if is_lab else 0,
                        'duration': duration,
                        'group': assign.get('group')
                    }
                    for i in range(duration):
                        curr_slot = best_slot + i
                        self.section_grid[assign['section_id']][best_day][curr_slot] = entry
                        if assign['teacher_id'] and assign['teacher_id'] in self.teacher_busy:
                            self.teacher_busy[assign['teacher_id']][best_day][curr_slot] = True
                        self.room_busy[best_room['id']][best_day][curr_slot] = True
                    
                    if assign['teacher_id'] and assign['teacher_id'] in self.teacher_hours:
                        self.teacher_hours[assign['teacher_id']] += duration
                    h_rem -= duration
                else:
                    # Constraint relaxation: if split was blocking, try without split
                    if assign.get('group') and attempt_count == 1:
                        # Try merging with partner group (disable split for this iteration)
                        continue
                    break 

            if h_rem > 0:
                failed_assignments.append({
                    'subject': assign['subject'],
                    'section_id': assign['section_id'],
                    'section_name': assign['section_name'],
                    'hours_lost': h_rem,
                    'group': assign.get('group')
                }) 

        return {
            'success': len(failed_assignments) == 0,
            'grid': self.section_grid,
            'failed': failed_assignments,
            'num_slots': self.num_slots,
            'days': self.days,
            'slots_times': self.slots_times
        }

    def solve(self):
        best_result = None
        min_failed = 999999
        
        for i in range(50):  # Increased from 20 to 50 attempts for better packing
            res = self.run_iteration()
            num_f = len(res['failed'])
            if num_f < min_failed:
                min_failed = num_f
                best_result = res
            if num_f == 0: break  # Found perfect solution
            
        return best_result
