"""
Comprehensive QA Automation Script for Students Database CRUD Application.
Executes the full 15-step QA testing checklist with detailed logging.
"""

from datetime import date
import os
from pathlib import Path
import sys
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup project path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import Base, get_db
from app.main import app
from app.models import Student

QA_DB_PATH = PROJECT_ROOT / "data" / "qa_test_students.db"
QA_DATABASE_URL = f"sqlite:///{QA_DB_PATH.as_posix()}"

# Ensure clean QA test database
if QA_DB_PATH.exists():
    try:
        QA_DB_PATH.unlink()
    except Exception:
        pass

engine = create_engine(QA_DATABASE_URL, connect_args={"check_same_thread": False})
QASessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_qa_get_db():
    db = QASessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_qa_get_db
client = TestClient(app)

results = []


def record_result(step_num, description, method, url, payload, expected_status, actual_status, response_body):
    passed = (actual_status == expected_status)
    results.append({
        "step": step_num,
        "description": description,
        "request": f"{method} {url}",
        "payload": payload,
        "expected_status": expected_status,
        "actual_status": actual_status,
        "passed": passed,
        "response_body": response_body,
    })
    status_str = "PASS" if passed else "FAIL"
    print(f"[Step {step_num:02d}] {description}: {status_str} (Expected: {expected_status}, Got: {actual_status})")


def run_qa_suite():
    print("=================================================================")
    print("STARTING END-TO-END QA WORKFLOW VERIFICATION")
    print("=================================================================\n")

    # Step 1: Check the health endpoint
    res1 = client.get("/health")
    record_result(
        1, "Check health endpoint", "GET", "/health", None,
        200, res1.status_code, res1.json()
    )

    # Step 2: Create a student with all required fields
    payload2 = {
        "student_id": "QA-STU-001",
        "full_name": "Divya Sharma",
        "date_of_birth": "2003-05-15",
        "email": "divya.sharma@example.edu",
        "phone": "+91-98765-43210",
        "course": "Computer Science & Engineering",
        "address": "42 Tech Boulevard, Hyderabad",
        "enrollment_date": "2024-07-20",
    }
    res2 = client.post("/students", json=payload2)
    record_result(
        2, "Create student with all fields", "POST", "/students", payload2,
        201, res2.status_code, res2.json()
    )

    # Step 3: Create a student using phone instead of email
    payload3 = {
        "student_id": "QA-STU-002",
        "full_name": "Tariq Ali",
        "date_of_birth": "2002-09-10",
        "phone": "+91-98111-22233",
        "course": "Mechanical Engineering",
    }
    res3 = client.post("/students", json=payload3)
    record_result(
        3, "Create student with phone only (no email)", "POST", "/students", payload3,
        201, res3.status_code, res3.json()
    )

    # Step 4: List all students
    res4 = client.get("/students")
    record_result(
        4, "List all students", "GET", "/students", None,
        200, res4.status_code, f"{len(res4.json())} students returned"
    )

    # Step 5: Filter the list using a supported filter (course="Computer")
    res5 = client.get("/students?course=Computer")
    data5 = res5.json()
    matches_filter = (len(data5) >= 1) and all("computer" in s["course"].lower() for s in data5)
    record_result(
        5, "Filter students by course (course=Computer)", "GET", "/students?course=Computer", None,
        200, res5.status_code, f"{len(data5)} matched filter (All match: {matches_filter})"
    )

    # Step 6: Retrieve a student by ID
    res6 = client.get("/students/QA-STU-001")
    record_result(
        6, "Retrieve student by ID (QA-STU-001)", "GET", "/students/QA-STU-001", None,
        200, res6.status_code, res6.json()
    )

    # Step 7: Update student details using PUT
    payload7 = {
        "full_name": "Divya Sharma",
        "date_of_birth": "2003-05-15",
        "email": "divya.updated@example.edu",
        "phone": "+91-98765-43210",
        "course": "Artificial Intelligence & Robotics",
        "address": "42 Tech Boulevard, Hyderabad",
        "enrollment_date": "2024-07-20",
    }
    res7 = client.put("/students/QA-STU-001", json=payload7)
    record_result(
        7, "Update student details using PUT", "PUT", "/students/QA-STU-001", payload7,
        200, res7.status_code, res7.json()
    )

    # Step 8: Change only one or two fields using PATCH
    payload8 = {
        "phone": "+91-99999-00000"
    }
    res8 = client.patch("/students/QA-STU-001", json=payload8)
    record_result(
        8, "Partially update phone using PATCH", "PATCH", "/students/QA-STU-001", payload8,
        200, res8.status_code, res8.json()
    )

    # Step 9: Try creating a duplicate student ID
    payload9 = {
        "student_id": "QA-STU-001",
        "full_name": "Duplicate Candidate",
        "date_of_birth": "2004-01-01",
        "email": "another.email@example.edu",
    }
    res9 = client.post("/students", json=payload9)
    record_result(
        9, "Reject duplicate student ID (HTTP 409)", "POST", "/students", payload9,
        409, res9.status_code, res9.json()
    )

    # Step 10: Try submitting invalid data (missing full_name and invalid future dob)
    payload10 = {
        "student_id": "QA-STU-INVALID",
        "date_of_birth": "2099-01-01",
        "email": "invalid@example.edu",
    }
    res10 = client.post("/students", json=payload10)
    record_result(
        10, "Reject invalid input / missing full_name (HTTP 422)", "POST", "/students", payload10,
        422, res10.status_code, res10.json()
    )

    # Step 11: Request a student ID that does not exist
    res11 = client.get("/students/NONEXISTENT-999")
    record_result(
        11, "Request non-existent student ID (HTTP 404)", "GET", "/students/NONEXISTENT-999", None,
        404, res11.status_code, res11.json()
    )

    # Step 12: Delete an existing test student
    res12 = client.delete("/students/QA-STU-002")
    record_result(
        12, "Delete existing student (QA-STU-002)", "DELETE", "/students/QA-STU-002", None,
        200, res12.status_code, res12.json()
    )

    # Step 13: Confirm deleted student can no longer be retrieved
    res13 = client.get("/students/QA-STU-002")
    record_result(
        13, "Confirm deleted student returns 404", "GET", "/students/QA-STU-002", None,
        404, res13.status_code, res13.json()
    )

    # Step 14: Restart application simulation and verify saved records remain in SQLite
    print("\nSimulating server restart (closing sessions and reconnecting new engine to same SQLite file)...")
    engine.dispose()
    client.close()

    new_engine = create_engine(QA_DATABASE_URL, connect_args={"check_same_thread": False})
    NewSession = sessionmaker(bind=new_engine)
    new_session = NewSession()

    surviving_student = new_session.query(Student).filter(Student.student_id == "QA-STU-001").first()
    persists = surviving_student is not None and surviving_student.full_name == "Divya Sharma"
    new_session.close()
    new_engine.dispose()

    record_result(
        14, "Verify data persistence after restart", "RESTART_VERIFY", QA_DATABASE_URL, None,
        200, 200 if persists else 500,
        {"persisted_student_id": "QA-STU-001", "persisted_name": surviving_student.full_name if surviving_student else None}
    )

    # Clean up QA database file
    try:
        if QA_DB_PATH.exists():
            QA_DB_PATH.unlink()
    except Exception:
        pass

    # Save summary report to JSON
    report_file = PROJECT_ROOT / "data" / "qa_report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    all_passed = all(r["passed"] for r in results)
    print("\n=================================================================")
    print(f"QA WORKFLOW SUMMARY: {'ALL 14 CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")
    print("=================================================================")
    return all_passed


if __name__ == "__main__":
    success = run_qa_suite()
    sys.exit(0 if success else 1)
