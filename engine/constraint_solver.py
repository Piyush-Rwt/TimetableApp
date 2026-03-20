import json
from engine.slot_scorer import score_slot

class ConstraintSolver:
    def __init__(self, institutions, breaks, teachers, courses, sections, subjects, subject_group_map, teacher_subject_map, rooms, config):
        self.sections = sections
        self.subjects = subjects
        self.teachers = {t['id']: t for t in teachers}
        self.rooms = rooms
        
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        # Hardcode 8 slots for now, normally based on start_time, end_time, slot_duration
        self.num_slots = 8 
        
        self.section_grid = {s['id']: {d: {slot: None for slot in range(self.num_slots)} for d in self.days} for s in self.sections}
        self.teacher_busy = {t['id']: {d: {slot: False for slot in range(self.num_slots)} for d in self.days} for t in self.teachers.values()}
        self.room_busy = {r['id']: {d: {slot: False for slot in range(self.num_slots)} for d in self.days} for r in self.rooms}
        
        # Mark break slots (Assume slot 4 is lunch/break for example purposes if no breaks supplied)
        self.break_slots = []
        if not breaks:
            self.break_slots = [4]
        else:
            # Need actual logic to map break time to slot index. 
            # Simplified:
            self.break_slots = [4] 

        for sec in self.section_grid.values():
            for d in self.days:
                for b_slot in self.break_slots:
                    sec[d][b_slot] = "BREAK"
                    
        self.assignments = []
        self._build_assignments(subject_group_map, teacher_subject_map)

    def _build_assignments(self, subject_group_map, teacher_subject_map):
        # Flatten requirements
        for sec in self.sections:
            for sub in self.subjects:
                # Check if subject belongs to section's group
                mapped = any(sgm['group_name'] == sec['group_name'] and sgm['subject_id'] == sub['id'] for sgm in subject_group_map)
                if not mapped and sec['group_name'] != 'Standard':
                     # Need better logic for standard vs group, assuming true for standard
                     if sec['group_type'] != 'Standard':
                         continue
                
                # Find teacher
                t_id = None
                for tsm in teacher_subject_map:
                    if tsm['subject_id'] == sub['id'] and (tsm['section_id'] == sec['id'] or tsm['section_id'] == 0):
                        t_id = tsm['teacher_id']
                        break
                
                if t_id:
                    self.assignments.append({
                        'section_id': sec['id'],
                        'subject': sub,
                        'teacher_id': t_id,
                        'hours_remaining': sub['hours_per_week']
                    })

        # Sort: is_lab DESC, hours DESC
        self.assignments.sort(key=lambda x: (x['subject']['is_lab'], x['subject']['hours_per_week']), reverse=True)

    def is_valid(self, day, slot, assignment, is_lab=False):
        sec_id = assignment['section_id']
        t_id = assignment['teacher_id']
        
        if self.section_grid[sec_id][day][slot] is not None: return False
        if self.teacher_busy[t_id][day][slot]: return False
        if slot in self.break_slots: return False
        
        if is_lab:
            if slot + 1 >= self.num_slots: return False
            if self.section_grid[sec_id][day][slot+1] is not None: return False
            if self.teacher_busy[t_id][day][slot+1]: return False
            if slot + 1 in self.break_slots: return False
            
        return True

    def solve(self):
        failed_assignments = []
        for assign in self.assignments:
            h_rem = assign['hours_remaining']
            while h_rem > 0:
                is_lab = assign['subject']['is_lab']
                hours_to_place = 2 if is_lab else 1
                if h_rem < hours_to_place:
                    hours_to_place = h_rem

                best_slot = None
                best_day = None
                best_score = -999

                for d in self.days:
                    for s in range(self.num_slots):
                        if self.is_valid(d, s, assign, is_lab=(hours_to_place > 1)):
                            # Score it
                            score = score_slot(s, d, assign['section_id'], assign['subject'], assign['teacher_id'], 
                                               self.teacher_busy, self.room_busy, self.section_grid[assign['section_id']])
                            if score > best_score:
                                best_score = score
                                best_slot = s
                                best_day = d

                if best_slot is not None:
                    # Place it
                    entry = {
                        'subject_id': assign['subject']['id'],
                        'teacher_id': assign['teacher_id'],
                        'is_lab': assign['subject']['is_lab']
                    }
                    self.section_grid[assign['section_id']][best_day][best_slot] = entry
                    self.teacher_busy[assign['teacher_id']][best_day][best_slot] = True
                    if hours_to_place > 1:
                        self.section_grid[assign['section_id']][best_day][best_slot+1] = entry
                        self.teacher_busy[assign['teacher_id']][best_day][best_slot+1] = True
                    
                    h_rem -= hours_to_place
                else:
                    failed_assignments.append(assign)
                    break # Cannot place remaining hours

        return {
            'success': len(failed_assignments) == 0,
            'grid': self.section_grid,
            'failed': failed_assignments
        }
