"""
Automated unit and integration tests for Students Database CRUD API.
Uses an isolated SQLite test database to ensure development data is never modified.
"""

from datetime import date
import os
from pathlib import Path
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure app package is in Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import Base, get_db
from app.main import app

# Isolated In-Memory SQLite database using StaticPool for thread-safe test execution
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Creates fresh database schema before each test and tears it down afterwards.
    """
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI TestClient wired to the test database session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==========================================
# 1. System & Health Endpoint Tests
# ==========================================

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "documentation" in data
    assert data["documentation"]["swagger_ui"] == "/docs"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data


# ==========================================
# 2. Student Creation Tests (POST /students)
# ==========================================

def test_create_student_success(client):
    payload = {
        "student_id": "STU-101",
        "full_name": "Kavita Rao",
        "date_of_birth": "2003-04-12",
        "email": "kavita.rao@example.edu",
        "phone": "+91-98765-00101",
        "course": "Computer Science",
        "address": "12 Residency Road, Pune",
        "enrollment_date": "2024-08-01",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU-101"
    assert data["full_name"] == "Kavita Rao"
    assert data["email"] == "kavita.rao@example.edu"
    assert data["course"] == "Computer Science"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_student_with_only_phone(client):
    payload = {
        "student_id": "STU-102",
        "full_name": "Amit Kumar",
        "date_of_birth": "2001-09-20",
        "phone": "+91-91234-56789",
        "course": "Mathematics",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU-102"
    assert data["email"] is None
    assert data["phone"] == "+91-91234-56789"


def test_create_student_with_only_email(client):
    payload = {
        "student_id": "STU-103",
        "full_name": "Sunita Sen",
        "date_of_birth": "2002-12-05",
        "email": "sunita.sen@example.edu",
        "course": "Physics",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU-103"
    assert data["email"] == "sunita.sen@example.edu"
    assert data["phone"] is None


def test_create_student_duplicate_id_conflict(client):
    payload = {
        "student_id": "STU-DUP-1",
        "full_name": "First Student",
        "date_of_birth": "2002-01-01",
        "email": "first@example.edu",
    }
    res1 = client.post("/students", json=payload)
    assert res1.status_code == 201

    duplicate_payload = {
        "student_id": "STU-DUP-1",
        "full_name": "Second Student With Same ID",
        "date_of_birth": "2003-02-02",
        "email": "second@example.edu",
    }
    res2 = client.post("/students", json=duplicate_payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_create_student_duplicate_email_conflict(client):
    payload1 = {
        "student_id": "STU-EM-1",
        "full_name": "Student A",
        "date_of_birth": "2002-01-01",
        "email": "duplicate.email@example.edu",
    }
    res1 = client.post("/students", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "student_id": "STU-EM-2",
        "full_name": "Student B",
        "date_of_birth": "2003-02-02",
        "email": "duplicate.email@example.edu",
    }
    res2 = client.post("/students", json=payload2)
    assert res2.status_code == 409
    assert "already registered" in res2.json()["detail"]


def test_create_student_missing_both_email_and_phone_validation_error(client):
    payload = {
        "student_id": "STU-NOCONTACT",
        "full_name": "No Contact Student",
        "date_of_birth": "2002-01-01",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert "At least one contact method must be provided" in response.text


def test_create_student_future_date_of_birth_rejected(client):
    payload = {
        "student_id": "STU-FUTURE",
        "full_name": "Future Student",
        "date_of_birth": "2099-01-01",
        "email": "future@example.edu",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert "Date of birth must be a date in the past" in response.text


def test_create_student_invalid_email_format(client):
    payload = {
        "student_id": "STU-BADEMAIL",
        "full_name": "Bad Email",
        "date_of_birth": "2002-01-01",
        "email": "not-an-email",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


# ==========================================
# 3. Listing & Query Filters (GET /students)
# ==========================================

def test_list_students_and_filtering(client):
    students = [
        {
            "student_id": "STU-S1",
            "full_name": "Rahul Bose",
            "date_of_birth": "2003-03-03",
            "email": "rahul.bose@example.edu",
            "course": "Robotics",
            "enrollment_date": "2024-07-01",
        },
        {
            "student_id": "STU-S2",
            "full_name": "Sneha Bose",
            "date_of_birth": "2002-05-15",
            "email": "sneha.bose@example.edu",
            "course": "Computer Science",
            "enrollment_date": "2024-07-01",
        },
        {
            "student_id": "STU-S3",
            "full_name": "Dev Mehta",
            "date_of_birth": "2001-11-20",
            "email": "dev.mehta@example.edu",
            "course": "Robotics",
            "enrollment_date": "2024-08-15",
        },
    ]
    for s in students:
        client.post("/students", json=s)

    # 1. List all
    res_all = client.get("/students")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 3

    # 2. Filter by name substring (case-insensitive "bose")
    res_name = client.get("/students?name=bose")
    assert res_name.status_code == 200
    data_name = res_name.json()
    assert len(data_name) == 2
    assert all("bose" in item["full_name"].lower() for item in data_name)

    # 3. Filter by course ("Robotics")
    res_course = client.get("/students?course=robotics")
    assert res_course.status_code == 200
    data_course = res_course.json()
    assert len(data_course) == 2
    assert all(item["course"] == "Robotics" for item in data_course)

    # 4. Filter by enrollment_date
    res_date = client.get("/students?enrollment_date=2024-07-01")
    assert res_date.status_code == 200
    assert len(res_date.json()) == 2

    # 5. Pagination
    res_page = client.get("/students?skip=1&limit=1")
    assert res_page.status_code == 200
    assert len(res_page.json()) == 1


# ==========================================
# 4. Read One Student (GET /students/{id})
# ==========================================

def test_get_existing_student_by_id(client):
    payload = {
        "student_id": "STU-READ-1",
        "full_name": "Arjun Nair",
        "date_of_birth": "2002-04-10",
        "email": "arjun.nair@example.edu",
    }
    client.post("/students", json=payload)

    response = client.get("/students/STU-READ-1")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "STU-READ-1"
    assert data["full_name"] == "Arjun Nair"


def test_get_nonexistent_student_returns_404(client):
    response = client.get("/students/DOES-NOT-EXIST")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


# ==========================================
# 5. Full Update (PUT /students/{id})
# ==========================================

def test_update_student_put_success(client):
    payload = {
        "student_id": "STU-PUT-1",
        "full_name": "Original Name",
        "date_of_birth": "2002-04-10",
        "email": "original@example.edu",
        "course": "Mechanical",
    }
    client.post("/students", json=payload)

    update_payload = {
        "full_name": "Updated Name",
        "date_of_birth": "2002-04-10",
        "email": "updated@example.edu",
        "phone": "+91-99999-88888",
        "course": "Mechatronics",
        "address": "New Address 101",
        "enrollment_date": "2024-09-01",
    }
    response = client.put("/students/STU-PUT-1", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "STU-PUT-1"
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.edu"
    assert data["course"] == "Mechatronics"


def test_update_student_put_nonexistent_returns_404(client):
    update_payload = {
        "full_name": "Ghost Student",
        "date_of_birth": "2002-04-10",
        "email": "ghost@example.edu",
    }
    response = client.put("/students/NONEXISTENT", json=update_payload)
    assert response.status_code == 404


def test_update_student_put_duplicate_email_conflict(client):
    # Student 1
    client.post("/students", json={
        "student_id": "STU-PUT-A",
        "full_name": "Student Alpha",
        "date_of_birth": "2002-01-01",
        "email": "alpha@example.edu",
    })
    # Student 2
    client.post("/students", json={
        "student_id": "STU-PUT-B",
        "full_name": "Student Beta",
        "date_of_birth": "2002-02-02",
        "email": "beta@example.edu",
    })

    # Try updating Student B's email to Student A's email
    response = client.put("/students/STU-PUT-B", json={
        "full_name": "Student Beta",
        "date_of_birth": "2002-02-02",
        "email": "alpha@example.edu",
    })
    assert response.status_code == 409
    assert "already associated with another student" in response.json()["detail"]


# ==========================================
# 6. Partial Update (PATCH /students/{id})
# ==========================================

def test_patch_student_success(client):
    client.post("/students", json={
        "student_id": "STU-PATCH-1",
        "full_name": "Maya Sen",
        "date_of_birth": "2003-07-14",
        "email": "maya.sen@example.edu",
        "course": "Civil Engineering",
    })

    patch_payload = {
        "course": "Structural Engineering & AI",
        "phone": "+91-98765-11223",
    }
    response = client.patch("/students/STU-PATCH-1", json=patch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["course"] == "Structural Engineering & AI"
    assert data["phone"] == "+91-98765-11223"
    # Unmodified fields remain intact
    assert data["full_name"] == "Maya Sen"
    assert data["email"] == "maya.sen@example.edu"


def test_patch_student_nonexistent_returns_404(client):
    response = client.patch("/students/NONEXISTENT", json={"course": "Biotech"})
    assert response.status_code == 404


def test_patch_student_cannot_strip_all_contact_methods(client):
    client.post("/students", json={
        "student_id": "STU-PATCH-2",
        "full_name": "Alok Roy",
        "date_of_birth": "2003-01-01",
        "email": "alok@example.edu",
        # No phone initially
    })

    # Attempting to clear the email while phone is None
    response = client.patch("/students/STU-PATCH-2", json={"email": None})
    assert response.status_code == 422
    assert "at least one contact method" in response.json()["detail"]


# ==========================================
# 7. Delete Student (DELETE /students/{id})
# ==========================================

def test_delete_student_success(client):
    client.post("/students", json={
        "student_id": "STU-DEL-1",
        "full_name": "Temporary Student",
        "date_of_birth": "2002-09-09",
        "email": "temp@example.edu",
    })

    # Verify exists
    assert client.get("/students/STU-DEL-1").status_code == 200

    # Delete
    response = client.delete("/students/STU-DEL-1")
    assert response.status_code == 200
    assert "was successfully deleted" in response.json()["detail"]

    # Verify no longer exists
    assert client.get("/students/STU-DEL-1").status_code == 404


def test_delete_nonexistent_student_returns_404(client):
    response = client.delete("/students/NONEXISTENT")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


# ==========================================
# 8. Data Persistence Verification
# ==========================================

def test_sqlite_persistence_between_sessions(tmp_path):
    """
    Verifies that records written to SQLite persist when a new database session
    or engine connects to the exact same file.
    """
    db_file = tmp_path / "persistence_test.db"
    file_engine = create_engine(f"sqlite:///{db_file.as_posix()}", connect_args={"check_same_thread": False})
    SessionMaker = sessionmaker(bind=file_engine)

    # 1. Initialize schema and insert a record
    Base.metadata.create_all(bind=file_engine)
    session1 = SessionMaker()
    from app.models import Student
    record = Student(
        student_id="STU-PERSIST-1",
        full_name="Persistent Record",
        date_of_birth=date(2002, 3, 10),
        email="persist@example.edu",
        course="Data Analytics",
    )
    session1.add(record)
    session1.commit()
    session1.close()

    # 2. Simulate server restart: dispose first engine, open brand new session
    file_engine.dispose()
    new_engine = create_engine(f"sqlite:///{db_file.as_posix()}", connect_args={"check_same_thread": False})
    NewSessionMaker = sessionmaker(bind=new_engine)
    session2 = NewSessionMaker()

    retrieved = session2.query(Student).filter(Student.student_id == "STU-PERSIST-1").first()
    assert retrieved is not None
    assert retrieved.full_name == "Persistent Record"
    assert retrieved.email == "persist@example.edu"
    assert retrieved.course == "Data Analytics"

    session2.close()
    new_engine.dispose()


# ==========================================
# 9. Optional AI Extension Tests (/ask)
# ==========================================

def test_ask_count_question_deterministic_fallback(client):
    # Seed 2 students
    client.post("/students", json={
        "student_id": "AI-TEST-1",
        "full_name": "Kiran Rao",
        "date_of_birth": "2003-05-10",
        "email": "kiran@example.edu",
        "course": "Computer Science",
    })
    client.post("/students", json={
        "student_id": "AI-TEST-2",
        "full_name": "Meera Sen",
        "date_of_birth": "2006-02-14",
        "phone": "+91-98765-43210",
        "course": "Data Science",
    })

    # Test count question (Ollama is offline in test environment, so fallback is exercised)
    response = client.post("/ask", json={"question": "How many students are there?"})
    assert response.status_code == 200
    data = response.json()
    assert data["grounded_facts"]["total_students"] == 2
    assert "2 student record(s)" in data["answer"]
    assert data["source"] == "deterministic_fallback"
    assert "ollama_offline" in data["status"]


def test_ask_born_after_question(client):
    client.post("/students", json={
        "student_id": "AI-BORN-1",
        "full_name": "Older Student",
        "date_of_birth": "2002-01-01",
        "email": "older@example.edu",
    })
    client.post("/students", json={
        "student_id": "AI-BORN-2",
        "full_name": "Younger Student",
        "date_of_birth": "2006-06-15",
        "email": "younger@example.edu",
    })

    response = client.post("/ask", json={"question": "List students born after 2005."})
    assert response.status_code == 200
    data = response.json()
    facts = data["grounded_facts"]
    assert facts["matched_count"] == 1
    assert facts["matched_students"][0]["student_id"] == "AI-BORN-2"
    assert "Younger Student" in data["answer"]


def test_ask_course_breakdown_question(client):
    client.post("/students", json={
        "student_id": "AI-CRS-1",
        "full_name": "CS Student 1",
        "date_of_birth": "2003-01-01",
        "email": "cs1@example.edu",
        "course": "Computer Science",
    })
    client.post("/students", json={
        "student_id": "AI-CRS-2",
        "full_name": "CS Student 2",
        "date_of_birth": "2003-02-02",
        "email": "cs2@example.edu",
        "course": "Computer Science",
    })
    client.post("/students", json={
        "student_id": "AI-CRS-3",
        "full_name": "IT Student 1",
        "date_of_birth": "2003-03-03",
        "email": "it1@example.edu",
        "course": "Information Technology",
    })

    response = client.post("/ask", json={"question": "How many students are enrolled in each course?"})
    assert response.status_code == 200
    data = response.json()
    breakdown = data["grounded_facts"]["course_breakdown"]
    assert breakdown.get("Computer Science") == 2
    assert breakdown.get("Information Technology") == 1


def test_ask_empty_question_rejected(client):
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 422


def test_ask_mocked_ollama_success(client, monkeypatch):
    from unittest.mock import MagicMock
    import httpx

    # Mock httpx.Client response to simulate a live Ollama server running llama3.2:1b
    class MockResponse:
        status_code = 200
        def json(self):
            return {"response": "According to the database, there are currently 0 students enrolled."}

    class MockClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def post(self, url, **kwargs):
            return MockResponse()

    monkeypatch.setattr(httpx, "Client", MockClient)

    response = client.post("/ask", json={"question": "How many students are there?"})
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "ollama"
    assert data["status"] == "success"
    assert "According to the database" in data["answer"]

