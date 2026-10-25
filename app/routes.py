"""
FastAPI route handlers for Student management endpoints.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentPatch,
    StudentResponse,
    MessageResponse,
    HealthResponse,
    AIQueryRequest,
    AIQueryResponse,
)
from app import crud, ai_service

router = APIRouter()


@router.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Register a new student record. Requires a unique student ID and at least one contact method (email or phone).",
    responses={
        201: {"description": "Student created successfully."},
        409: {"description": "Conflict - Student ID or email already registered."},
        422: {"description": "Validation Error - Invalid input data format."},
    },
)
def create_student_endpoint(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new student record.
    """
    # Check if student_id already exists
    existing_id = crud.get_student_by_id(db, student_id=student_in.student_id)
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with ID '{student_in.student_id}' already exists.",
        )

    # Check if email is provided and already taken
    if student_in.email:
        existing_email = crud.get_student_by_email(db, email=student_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with email '{student_in.email}' is already registered.",
            )

    return crud.create_student(db, student_in=student_in)


@router.get(
    "/students",
    response_model=List[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="List all students",
    description="Retrieve student records with optional search filters for name, course, and enrollment date, plus pagination.",
)
def list_students_endpoint(
    name: Optional[str] = Query(None, description="Search students by full name (case-insensitive substring)"),
    course: Optional[str] = Query(None, description="Filter by course/program name (case-insensitive)"),
    enrollment_date: Optional[date] = Query(None, description="Filter by exact enrollment date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Pagination offset: number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit: maximum records to return"),
    db: Session = Depends(get_db),
):
    """
    List students with optional query filters.
    """
    return crud.list_students(
        db,
        name=name,
        course=course,
        enrollment_date=enrollment_date,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/students/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get student by ID",
    description="Retrieve complete details for a specific student using their unique student ID.",
    responses={
        200: {"description": "Student record found."},
        404: {"description": "Student not found."},
    },
)
def get_student_endpoint(
    student_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single student record by their student ID.
    """
    student = crud.get_student_by_id(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found.",
        )
    return student


@router.put(
    "/students/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing student (Full replace)",
    description="Replace editable details for an existing student. At least one contact method must be provided.",
    responses={
        200: {"description": "Student updated successfully."},
        404: {"description": "Student not found."},
        409: {"description": "Conflict - Email already belongs to another student."},
        422: {"description": "Validation Error - Invalid input format."},
    },
)
def update_student_endpoint(
    student_id: str,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
):
    """
    Replace editable details for a student record.
    """
    db_student = crud.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found.",
        )

    # If updating email, ensure it is not taken by another student
    if student_in.email:
        existing_email_student = crud.get_student_by_email(db, email=student_in.email)
        if existing_email_student and existing_email_student.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{student_in.email}' is already associated with another student.",
            )

    return crud.update_student(db, db_student=db_student, student_in=student_in)


@router.patch(
    "/students/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update an existing student",
    description="Update only the fields supplied in the request body.",
    responses={
        200: {"description": "Student updated successfully."},
        404: {"description": "Student not found."},
        409: {"description": "Conflict - Email already belongs to another student."},
        422: {"description": "Validation Error."},
    },
)
def patch_student_endpoint(
    student_id: str,
    student_in: StudentPatch,
    db: Session = Depends(get_db),
):
    """
    Partially update specific fields of a student record.
    """
    db_student = crud.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found.",
        )

    # If updating email, ensure it is not taken by another student
    if student_in.email:
        existing_email_student = crud.get_student_by_email(db, email=student_in.email)
        if existing_email_student and existing_email_student.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{student_in.email}' is already associated with another student.",
            )

    # Compute future contact state to prevent leaving both email and phone blank
    fields_set = student_in.model_fields_set
    future_email = student_in.email if "email" in fields_set else db_student.email
    future_phone = student_in.phone if "phone" in fields_set else db_student.phone
    if not future_email and not future_phone:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot update record: at least one contact method (email or phone) must remain active.",
        )

    return crud.patch_student(db, db_student=db_student, student_in=student_in)


@router.delete(
    "/students/{student_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a student by ID",
    description="Remove a student record permanently from the database.",
    responses={
        200: {"description": "Student record deleted successfully."},
        404: {"description": "Student not found."},
    },
)
def delete_student_endpoint(
    student_id: str,
    db: Session = Depends(get_db),
):
    """
    Permanently delete a student record by ID.
    """
    db_student = crud.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found.",
        )

    crud.delete_student(db, db_student=db_student)
    return MessageResponse(detail=f"Student with ID '{student_id}' was successfully deleted.")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="API Health Status",
    description="Check the operational status of the API and database connectivity.",
    tags=["System"],
)
def health_check_endpoint(db: Session = Depends(get_db)):
    """
    Return API health and database connectivity status.
    """
    try:
        # Execute quick SQLite ping query
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        version="1.0.0",
    )


@router.post(
    "/ask",
    response_model=AIQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about student records (Optional AI Extension)",
    description=(
        "Ask natural-language questions grounded in verified SQLite records. "
        "Calculates exact facts via Python and SQLite before optionally consulting "
        "a local Ollama model (e.g. llama3.2:1b). Falls back gracefully if Ollama is offline."
    ),
    tags=["AI Assistant"],
)
def ask_question_endpoint(
    request: AIQueryRequest,
    db: Session = Depends(get_db),
):
    """
    Answer natural-language questions using grounded database facts.
    """
    facts = ai_service.fetch_grounded_facts(db, question=request.question)
    ai_result = ai_service.ask_ollama(question=request.question, facts=facts)

    return AIQueryResponse(
        question=request.question,
        answer=ai_result["answer"],
        grounded_facts=facts,
        source=ai_result["source"],
        status=ai_result["status"],
        model=ai_result["model"],
    )

