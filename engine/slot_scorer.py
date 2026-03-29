def score_slot(slot_idx, day, section_id, assignment, teacher_busy, room_busy, section_grid, days_list):
    """
    Scores a (day, slot) for a given assignment.
    Soft Constraints:
    - Distribute subjects evenly across week (+20 if subject not on same day)
    - Avoid teacher gaps (+15 if adjacent to existing class)
    - Labs preferably in morning or afternoon block (+10)
    - Same subject not on consecutive days (+10)
    """
    score = 100 # Base score
    subject = assignment['subject']
    teacher_id = assignment['teacher_id']
    
    # 1. Distribute subjects evenly: Avoid same subject on same day
    subject_on_day = False
    for s_idx, entry in section_grid[day].items():
        if isinstance(entry, dict) and entry.get('subject_id') == subject['id']:
            subject_on_day = True
            break
    if subject_on_day:
        score -= 40 # Strong penalty for doubling up same subject on same day
    
    # 2. Consecutive days: Prefer spacing out same subject
    day_idx = days_list.index(day)
    prev_day = days_list[day_idx-1] if day_idx > 0 else None
    next_day = days_list[day_idx+1] if day_idx < len(days_list)-1 else None
    
    for d in [prev_day, next_day]:
        if d:
            for s_idx, entry in section_grid[d].items():
                if isinstance(entry, dict) and entry.get('subject_id') == subject['id']:
                    score -= 10
                    break
                    
    # 3. Teacher Gaps: Prefer slots adjacent to teacher's existing classes
    if teacher_id and teacher_id in teacher_busy:
        has_adj = False
        if slot_idx > 0 and teacher_busy[teacher_id][day].get(slot_idx - 1):
            has_adj = True
        if teacher_busy[teacher_id][day].get(slot_idx + 1):
            has_adj = True
            
        if has_adj:
            score += 20
        else:
            # Penalty if teacher has other classes today but not adjacent
            if any(teacher_busy[teacher_id][day].values()):
                score -= 15
            
    # 4. Lab Block preference (Morning: slots 0-2, Afternoon: slots 5-7)
    if subject['type'] == 'Lab':
        if slot_idx <= 2 or slot_idx >= 5:
            score += 15
            
    # 5. Compactness: Prefer earlier slots in the day to fill gaps
    score += (len(section_grid[day]) - slot_idx) * 2
    
    # 6. Clustering: Small boost if scheduled next to ANY subject in this section
    has_any_adj = False
    if slot_idx > 0 and section_grid[day].get(slot_idx - 1):
        has_any_adj = True
    if section_grid[day].get(slot_idx + 1):
        has_any_adj = True
    if has_any_adj:
        score += 5
            
    return score
