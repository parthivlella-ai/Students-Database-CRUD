"""
Database seeding script for Students Database CRUD.
Populates the database with realistic fictional student records for testing and demonstration.
Safe to run multiple times: skips records that already exist.
"""

from datetime import date
import sys
from pathlib import Path

# Add project root to sys.path so app modules can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal, init_db
from app.models import Student

# Sample fictional student dataset
SAMPLE_STUDENTS = [
    {
        "student_id": "STU-2024-001",
        "full_name": "Aarav Sharma",
        "date_of_birth": date(2003, 4, 15),
        "email": "aarav.sharma@example.edu",
        "phone": "+91-98765-43210",
        "course": "Computer Science & Engineering",
        "address": "12 Lotus Residency, Cyber City, Bangalore",
        "enrollment_date": date(2024, 7, 10),
    },
    {
        "student_id": "STU-2024-002",
        "full_name": "Priya Patel",
        "date_of_birth": date(2002, 11, 28),
        "email": "priya.patel@example.edu",
        "phone": "+91-98123-45678",
        "course": "Data Science & Artificial Intelligence",
        "address": "45 Green Meadows, Vastrapur, Ahmedabad",
        "enrollment_date": date(2024, 7, 12),
    },
    {
        "student_id": "STU-2024-003",
        "full_name": "Rohan Verma",
        "date_of_birth": date(2004, 1, 9),
        "email": "rohan.verma@example.edu",
        "phone": "+91-99887-76655",
        "course": "Information Technology",
        "address": "88 Palm Grove, Sector 62, Noida",
        "enrollment_date": date(2024, 8, 1),
    },
    {
        "student_id": "STU-2024-004",
        "full_name": "Ananya Iyer",
        "date_of_birth": date(2003, 8, 22),
        "email": "ananya.iyer@example.edu",
        "phone": "+91-91234-56780",
        "course": "Computer Science & Engineering",
        "address": "33 Temple Bay, Adyar, Chennai",
        "enrollment_date": date(2024, 7, 15),
    },
    {
        "student_id": "STU-2024-005",
        "full_name": "Kabir Das",
        "date_of_birth": date(2002, 6, 30),
        "email": "kabir.das@example.edu",
        "phone": "+91-97654-32109",
        "course": "Cyber Security",
        "address": "104 Heritage Park, Ballygunge, Kolkata",
        "enrollment_date": date(2024, 8, 5),
    },
]


def seed_database():
    """
    Safely seed sample records without overwriting or erasing existing data.
    """
    print("Ensuring database tables are initialized...")
    init_db()

    db = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    try:
        for student_data in SAMPLE_STUDENTS:
            existing = db.query(Student).filter(Student.student_id == student_data["student_id"]).first()
            if existing:
                print(f"Skipping existing student ID: {student_data['student_id']} ({existing.full_name})")
                skipped_count += 1
                continue

            student = Student(**student_data)
            db.add(student)
            inserted_count += 1
            print(f"Added fictional student: {student_data['student_id']} - {student_data['full_name']}")

        db.commit()
        print(f"\nSeeding complete! Added: {inserted_count}, Skipped (already existed): {skipped_count}.")
    except Exception as exc:
        db.rollback()
        print(f"Error while seeding database: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
