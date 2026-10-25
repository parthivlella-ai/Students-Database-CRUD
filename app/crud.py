"""
CRUD (Create, Read, Update, Delete) database operations for Student records.
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentPatch


def get_student_by_id(db: Session, student_id: str) -> Optional[Student]:
    """
    Retrieve a single student by their unique student ID.
    """
    return db.query(Student).filter(Student.student_id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """
    Retrieve a student by email address to check for uniqueness.
    """
    if not email:
        return None
    return db.query(Student).filter(func.lower(Student.email) == email.lower()).first()


def list_students(
    db: Session,
    name: Optional[str] = None,
    course: Optional[str] = None,
    enrollment_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Student]:
    """
    Retrieve students with optional filtering and pagination.
    - name: Substring search on full_name (case-insensitive)
    - course: Filter by course (case-insensitive)
    - enrollment_date: Exact match on enrollment date
    """
    query = db.query(Student)

    if name:
        query = query.filter(Student.full_name.ilike(f"%{name.strip()}%"))

    if course:
        query = query.filter(Student.course.ilike(f"%{course.strip()}%"))

    if enrollment_date:
        query = query.filter(Student.enrollment_date == enrollment_date)

    return query.order_by(Student.student_id.asc()).offset(skip).limit(limit).all()


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """
    Create and persist a new student record in the database.
    """
    db_student = Student(
        student_id=student_in.student_id,
        full_name=student_in.full_name,
        date_of_birth=student_in.date_of_birth,
        email=student_in.email,
        phone=student_in.phone,
        course=student_in.course,
        address=student_in.address,
        enrollment_date=student_in.enrollment_date,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, db_student: Student, student_in: StudentUpdate) -> Student:
    """
    Replace all editable fields of an existing student record (PUT).
    """
    db_student.full_name = student_in.full_name
    db_student.date_of_birth = student_in.date_of_birth
    db_student.email = student_in.email
    db_student.phone = student_in.phone
    db_student.course = student_in.course
    db_student.address = student_in.address
    db_student.enrollment_date = student_in.enrollment_date

    db.commit()
    db.refresh(db_student)
    return db_student


def patch_student(db: Session, db_student: Student, student_in: StudentPatch) -> Student:
    """
    Partially update specified fields of an existing student record (PATCH).
    """
    update_data = student_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, db_student: Student) -> None:
    """
    Permanently delete a student record from the database.
    """
    db.delete(db_student)
    db.commit()
