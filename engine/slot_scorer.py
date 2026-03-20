def score_slot(slot_index, day_index, section_id, subject, teacher_id, teacher_busy, room_busy, section_busy):
    score = 50  # Base score
    
    # +20 if teacher has no gap created by this placement
    # Check if teacher has adjacent slots occupied
    has_adj = False
    if slot_index > 0 and teacher_busy.get(teacher_id, {}).get(day_index, {}).get(slot_index - 1):
        has_adj = True
    if teacher_busy.get(teacher_id, {}).get(day_index, {}).get(slot_index + 1):
        has_adj = True
    if has_adj:
        score += 20
    else:
        # -30 if placement creates a gap in teacher's day
        # Simplistic check: if teacher has classes today but not adjacent
        teacher_day_slots = teacher_busy.get(teacher_id, {}).get(day_index, {})
        if any(teacher_day_slots.values()):
            score -= 30

    # +15 if subject not already scheduled today for this section
    # Needs actual section grid or just checking section_busy for this subject?
    # Here we simulate by assuming section_busy has subject details or we just pass it in
    # For now, base implementation.
    subject_today = False
    for s_idx, subj_placed in section_busy.get(day_index, {}).items():
        if subj_placed == subject['id']:
            subject_today = True
            break
    if not subject_today:
        score += 15

    # -20 if teacher already has 3 slots today
    teacher_day_slots = teacher_busy.get(teacher_id, {}).get(day_index, {})
    if sum(1 for v in teacher_day_slots.values() if v) >= 3:
        score -= 20

    return score
