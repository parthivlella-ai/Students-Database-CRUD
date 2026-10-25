"""
SQLAlchemy ORM models for the Students Database.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, DateTime
from app.database import Base


class Student(Base):
    """
    SQLAlchemy model representing a student in the database.
    """
    __tablename__ = "students"

    # Unique student identification code (e.g., 'STU-1001')
    student_id = Column(String(50), primary_key=True, index=True, nullable=False)

    # Personal details
    full_name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)

    # Contact details (at least one is required by validation schemas)
    email = Column(String(120), unique=True, nullable=True, index=True)
    phone = Column(String(30), nullable=True)

    # Academic & residential details (optional)
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(Date, nullable=True, index=True)

    # Audit timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Student(id='{self.student_id}', name='{self.full_name}', course='{self.course}')>"
