"""
Random Data Generator for Timetable App
Generates realistic random test data with configurable sizes and distributions.
"""

import random
import string
from typing import Dict, List, Tuple

class RandomDataGenerator:
    """
    Generates random but realistic data for the timetable scheduling system.
    Ensures data consistency and proper constraints.
    """
    
    # Fixed lists for realistic names and identifiers
    FIRST_NAMES = ["Raj", "Priya", "Amit", "Anjali", "Arjun", "Neha", "Vikram", "Deepika", 
                   "Rohan", "Kavya", "Aditi", "Nikhil", "Aisha", "Rahul", "Sneha"]
    LAST_NAMES = ["Kumar", "Singh", "Sharma", "Verma", "Gupta", "Patel", "Desai", "Rao", 
                  "Iyer", "Nair", "Reddy", "Bhat", "Menon", "Misra", "Saxena"]
    SUBJECT_PREFIXES = ["CS", "EC", "ME", "CE", "EE", "IT", "BT", "CL"]
    SUBJECT_NAMES = ["Algorithms", "Database", "Networks", "OS", "Compiler", "Web Dev", 
                     "AI", "Data Science", "Security", "Cloud Computing", "ML", "IoT", "Robotics"]
    SECTION_NAMES = ["A", "B", "C", "D", "E", "F", "G", "H"]
    SPECIALIZATION_NAMES = ["Cloud Computing", "Artificial Intelligence", "Cybersecurity", 
                           "Data Science", "Web Development", "DevOps", "Blockchain"]
    ROOM_PREFIXES = ["CR", "LAB", "LT", "SL"]  # Classroom, Lab, Lecture Theatre, Smart Lab
    
    def __init__(self, seed: int = None):
        """Initialize random data generator with optional seed for reproducibility."""
        if seed:
            random.seed(seed)
    
    def generate_institution_data(self) -> Dict:
        """Generate institution configuration with realistic timings."""
        return {
            "name": "Tech Institute",
            "department": random.choice(["Computer Science", "Electronics", "Mechanical", "Civil"]),
            "semester": str(random.randint(1, 8)),
            "working_days": "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday",
            "start_time": "08:00",
            "end_time": "18:00",
            "slot_duration_mins": 55
        }
    
    def generate_teachers(self, count: int = 50) -> List[Tuple[str, int]]:
        """
        Generate random teacher data.
        Args:
            count: Number of teachers to generate (default: 50)
        Returns:
            List of tuples (name, max_hours_per_week)
        """
        teachers = []
        used_names = set()
        
        while len(teachers) < count:
            first_name = random.choice(self.FIRST_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            name = f"{first_name} {last_name}"
            
            # Avoid duplicate names
            if name not in used_names:
                used_names.add(name)
                max_hours = random.randint(12, 28)
                teachers.append((name, max_hours))
        
        return teachers
    
    def generate_rooms(self, count: int = None) -> List[Tuple[str, str, int]]:
        """
        Generate random room data.
        Args:
            count: Number of rooms (default: random 20-25)
        Returns:
            List of tuples (room_name, room_type, capacity)
        """
        if count is None:
            count = random.randint(20, 25)
        
        rooms = []
        classroom_count = random.randint(12, 18)
        lab_count = count - classroom_count
        
        # Generate classrooms
        for i in range(1, classroom_count + 1):
            prefix = random.choice(["CR", "LT"])  # Classroom or Lecture Theatre
            room_name = f"{prefix} {100 + i}"
            capacity = random.randint(40, 90)
            rooms.append((room_name, "Classroom", capacity))
        
        # Generate labs
        for i in range(1, lab_count + 1):
            prefix = random.choice(["LAB", "SL"])  # Lab or Smart Lab
            room_name = f"{prefix} {i}"
            capacity = random.randint(20, 50)
            rooms.append((room_name, "Lab", capacity))
        
        return rooms
    
    def generate_sections(self, count: int = None) -> List[Tuple[str, int]]:
        """
        Generate random section data.
        Args:
            count: Number of sections (default: random 6-10)
        Returns:
            List of tuples (section_name, student_count)
        """
        if count is None:
            count = random.randint(6, 10)
        
        sections = []
        used_names = set()
        
        for i in range(count):
            # Create section names like A1, A2, B1, B2, etc.
            letter = self.SECTION_NAMES[i // 2]
            number = (i % 2) + 1
            name = f"{letter}{number}"
            
            if name not in used_names:
                used_names.add(name)
                student_count = random.randint(50, 80)
                sections.append((name, student_count))
        
        return sections
    
    def generate_specializations(self, count: int = None) -> List[str]:
        """
        Generate random specializations with 50/50 chance.
        Args:
            count: Number of specializations (default: random 3-5)
        Returns:
            List of specialization names
        """
        # 50/50 chance whether to include specializations
        if random.choice([True, False]):
            if count is None:
                count = random.randint(3, 5)
            return random.sample(self.SPECIALIZATION_NAMES, min(count, len(self.SPECIALIZATION_NAMES)))
        return []
    
    def generate_subjects(self, count: int = None, specializations: List[str] = None, 
                         teachers: List[Tuple[str, int]] = None) -> List[Dict]:
        """
        Generate random subject data with proper constraints.
        Args:
            count: Number of subjects (default: random 8-13)
            specializations: Available specializations to assign subjects to
            teachers: Available teachers (list of tuples with name as first element)
        Returns:
            List of subject dictionaries
        """
        if count is None:
            count = random.randint(8, 13)
        
        if teachers is None:
            teachers = self.generate_teachers(50)
        
        subjects = []
        used_codes = set()
        
        for i in range(count):
            # Generate unique subject code
            code = f"{random.choice(self.SUBJECT_PREFIXES)}{random.randint(100, 999)}"
            while code in used_codes:
                code = f"{random.choice(self.SUBJECT_PREFIXES)}{random.randint(100, 999)}"
            used_codes.add(code)
            
            # Generate subject details
            subject_name = random.choice(self.SUBJECT_NAMES)
            subject_type = random.choice(["Theory", "Lab", "Elective"])
            hours = random.randint(2, 4)
            teacher = random.choice(teachers)
            room_type = "Lab" if subject_type == "Lab" else "Classroom"
            lab_duration = 2 if subject_type == "Lab" else 0
            
            subject_dict = {
                "code": code,
                "name": f"{subject_name} {i+1}",
                "type": subject_type,
                "hours_per_week": hours,
                "teacher_name": teacher[0],
                "room_type_req": room_type,
                "lab_duration": lab_duration,
                "split_groups": 0,
                "specialization": random.choice(specializations) if specializations else None
            }
            subjects.append(subject_dict)
        
        return subjects
    
    def generate_breaks(self) -> List[Dict]:
        """Generate standard break times."""
        return [
            {"name": "Short Break", "start_time": "10:00", "end_time": "10:15"},
            {"name": "Mid Break", "start_time": "12:00", "end_time": "12:30"},
            {"name": "Lunch Break", "start_time": "13:30", "end_time": "14:15"}
        ]
    
    def generate_teacher_unavailability(self, teacher_idx: int, total_slots: int = 9) -> List[Tuple[str, int]]:
        """
        Generate random unavailable slots for a teacher.
        Args:
            teacher_idx: Index of teacher
            total_slots: Total number of time slots in a day
        Returns:
            List of tuples (day, slot_index)
        """
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        unavailable = []
        
        # 40% chance a teacher has some unavailability
        if random.random() < 0.4:
            num_unavailable = random.randint(1, 4)
            for _ in range(num_unavailable):
                day = random.choice(days)
                slot = random.randint(0, total_slots - 1)
                unavailable.append((day, slot))
        
        return unavailable
    
    def generate_all_data(self) -> Dict:
        """
        Generate complete dataset at once.
        Returns:
            Dictionary containing all generated data
        """
        # Generate core data
        institution = self.generate_institution_data()
        teachers = self.generate_teachers(50)
        rooms = self.generate_rooms()
        sections = self.generate_sections()
        specializations = self.generate_specializations()
        subjects = self.generate_subjects(specializations=specializations, teachers=teachers)
        breaks = self.generate_breaks()
        
        # Generate teacher unavailability
        teacher_unavailability = {}
        for idx, (teacher_name, _) in enumerate(teachers):
            unavailability = self.generate_teacher_unavailability(idx)
            if unavailability:
                teacher_unavailability[teacher_name] = unavailability
        
        return {
            "institution": institution,
            "teachers": teachers,
            "rooms": rooms,
            "sections": sections,
            "specializations": specializations,
            "subjects": subjects,
            "breaks": breaks,
            "teacher_unavailability": teacher_unavailability
        }


def generate_random_data(seed: int = None) -> Dict:
    """
    Convenience function to generate all random data.
    Args:
        seed: Optional seed for reproducibility
    Returns:
        Complete dataset dictionary
    """
    generator = RandomDataGenerator(seed=seed)
    return generator.generate_all_data()


if __name__ == "__main__":
    # Example usage
    data = generate_random_data()
    print(f"Teachers: {len(data['teachers'])}")
    print(f"Rooms: {len(data['rooms'])}")
    print(f"Sections: {len(data['sections'])}")
    print(f"Subjects: {len(data['subjects'])}")
    print(f"Specializations: {len(data['specializations'])}")
