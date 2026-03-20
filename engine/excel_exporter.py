import openpyxl
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
import os

def export_section_timetables(grid, sections, subjects, teachers, filepath="saved_tt/Section_Timetables.xlsx"):
    wb = openpyxl.Workbook()
    wb.remove(wb.active) # Remove default sheet
    
    sub_map = {s['id']: s['name'] for s in subjects}
    t_map = {t['id']: t['name'] for t in teachers}
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    header_fill = PatternFill(start_color="4F6EF7", end_color="4F6EF7", fill_type="solid")
    break_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")
    lab_fill = PatternFill(start_color="2ECC71", end_color="2ECC71", fill_type="solid")
    theory_fill = PatternFill(start_color="A9CCE3", end_color="A9CCE3", fill_type="solid")
    
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    for sec in sections:
        ws = wb.create_sheet(title=sec['name'])
        
        # Title
        ws.merge_cells('A1:G1')
        ws['A1'] = f"Timetable - {sec['name']} ({sec['group_name']})"
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal='center')
        
        # Headers
        headers = ["Slot"] + days
        for col_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col_idx)
            cell.value = h
            cell.fill = header_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal='center')
            cell.border = thin_border
            
        # Rows
        sec_data = grid.get(sec['id'], {})
        for slot in range(8): # 8 slots
            row_idx = slot + 3
            ws.cell(row=row_idx, column=1).value = f"Slot {slot+1}"
            ws.cell(row=row_idx, column=1).border = thin_border
            
            for col_idx, day in enumerate(days, 2):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                
                entry = sec_data.get(day, {}).get(slot)
                if entry == "BREAK":
                    cell.value = "BREAK"
                    cell.fill = break_fill
                elif entry:
                    sub_name = sub_map.get(entry['subject_id'], "Unknown")
                    t_name = t_map.get(entry['teacher_id'], "Unknown")
                    cell.value = f"{sub_name}
({t_name})"
                    cell.fill = lab_fill if entry['is_lab'] else theory_fill
                else:
                    cell.value = ""
                    
    wb.save(filepath)
    return filepath
