"""
Pydantic schemas for data validation and serialization.
"""

from datetime import date, datetime
import re
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator, field_validator


class StudentBase(BaseModel):
    """
    Shared fields across student request models.
    """
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the student (e.g. Alex Morgan)",
        examples=["Alex Morgan"]
    )
    date_of_birth: date = Field(
        ...,
        description="Student's date of birth (YYYY-MM-DD)",
        examples=["2002-05-14"]
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Valid email address (e.g. alex.morgan@example.com)",
        examples=["alex.morgan@example.com"]
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=7,
        max_length=25,
        description="Contact phone number (e.g. +1-555-019-2834)",
        examples=["+1-555-019-2834"]
    )
    course: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Enrolled program or course (e.g. Computer Science)",
        examples=["Computer Science"]
    )
    address: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Mailing or residential address",
        examples=["452 Innovation Way, Tech City, CA 94016"]
    )
    enrollment_date: Optional[date] = Field(
        default=None,
        description="Date when the student enrolled (YYYY-MM-DD)",
        examples=["2024-09-01"]
    )

    @field_validator("full_name")
    @classmethod
    def validate_name_not_blank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Full name cannot be empty or solely whitespace.")
        return trimmed

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_in_past(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Date of birth must be a date in the past.")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone_format(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        # Allow numbers, spaces, plus, hyphens, and parentheses
        if not re.match(r"^[\d\+\-\(\)\s]{7,25}$", trimmed):
            raise ValueError("Phone number contains invalid characters or formatting.")
        return trimmed


class StudentCreate(StudentBase):
    """
    Schema for creating a new student record (POST /students).
    """
    student_id: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique alphanumeric student ID (e.g. STU-1001)",
        examples=["STU-1001"]
    )

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: str) -> str:
        trimmed = value.strip()
        if not re.match(r"^[A-Za-z0-9_-]+$", trimmed):
            raise ValueError("Student ID must only contain alphanumeric characters, hyphens, or underscores.")
        return trimmed

    @model_validator(mode="after")
    def check_at_least_one_contact(self) -> "StudentCreate":
        if not self.email and not self.phone:
            raise ValueError("At least one contact method must be provided: either email or phone.")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "STU-1001",
                "full_name": "Alex Morgan",
                "date_of_birth": "2002-05-14",
                "email": "alex.morgan@example.com",
                "phone": "+1-555-019-2834",
                "course": "Computer Science",
                "address": "452 Innovation Way, Tech City, CA 94016",
                "enrollment_date": "2024-09-01"
            }
        }
    )


class StudentUpdate(StudentBase):
    """
    Schema for replacing/updating an existing student (PUT /students/{student_id}).
    Student ID is immutable and passed in the URL path.
    """
    @model_validator(mode="after")
    def check_at_least_one_contact(self) -> "StudentUpdate":
        if not self.email and not self.phone:
            raise ValueError("At least one contact method must be provided: either email or phone.")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Alex Morgan",
                "date_of_birth": "2002-05-14",
                "email": "alex.morgan.updated@example.com",
                "phone": "+1-555-019-2834",
                "course": "Software Engineering",
                "address": "789 Redwood Blvd, Tech City, CA 94016",
                "enrollment_date": "2024-09-01"
            }
        }
    )


class StudentPatch(BaseModel):
    """
    Schema for partially updating an existing student (PATCH /students/{student_id}).
    All fields are optional.
    """
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    phone: Optional[str] = Field(default=None, min_length=7, max_length=25)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    enrollment_date: Optional[date] = Field(default=None)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("Full name cannot be empty.")
            return trimmed
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value >= date.today():
            raise ValueError("Date of birth must be a date in the past.")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not re.match(r"^[\d\+\-\(\)\s]{7,25}$", trimmed):
                raise ValueError("Phone number contains invalid characters or formatting.")
            return trimmed
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "course": "Artificial Intelligence & Data Systems",
                "phone": "+1-555-019-9999"
            }
        }
    )


class StudentResponse(StudentBase):
    """
    Schema for serialized student responses.
    """
    student_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "student_id": "STU-1001",
                "full_name": "Alex Morgan",
                "date_of_birth": "2002-05-14",
                "email": "alex.morgan@example.com",
                "phone": "+1-555-019-2834",
                "course": "Computer Science",
                "address": "452 Innovation Way, Tech City, CA 94016",
                "enrollment_date": "2024-09-01",
                "created_at": "2026-10-25T12:00:00",
                "updated_at": "2026-10-25T12:00:00"
            }
        }
    )


class MessageResponse(BaseModel):
    """
    Generic message schema for delete confirmation and status alerts.
    """
    detail: str = Field(..., examples=["Student record deleted successfully."])


class HealthResponse(BaseModel):
    """
    Health check response schema.
    """
    status: str = Field(..., examples=["healthy"])
    database: str = Field(..., examples=["connected"])
    version: str = Field(..., examples=["1.0.0"])


class AIQueryRequest(BaseModel):
    """
    Request schema for natural-language questions about student records.
    """
    question: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Natural-language question about student records",
        examples=["How many students are there?"]
    )

    @field_validator("question")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Question cannot be empty or whitespace only.")
        return trimmed

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "How many students are enrolled in each course?"
            }
        }
    )


class AIQueryResponse(BaseModel):
    """
    Response schema for natural-language query answers grounded in SQLite data.
    """
    question: str = Field(..., examples=["How many students are there?"])
    answer: str = Field(..., examples=["There are currently 5 student record(s) registered in the database."])
    grounded_facts: dict = Field(..., description="Deterministic facts verified directly from SQLite")
    source: str = Field(..., description="Generation source: 'ollama' or 'deterministic_fallback'", examples=["ollama"])
    status: str = Field(..., examples=["success"])
    model: str = Field(..., examples=["llama3.2:1b"])

