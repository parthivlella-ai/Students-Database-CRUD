# Students Database CRUD Application

**Internship Project Assignment**  
**Organization:** EWB Edu Tech Pvt. Ltd.  
**Program:** Future Agents Internship  
**Track:** Python Backend Development  
**Version:** 1.0.0  

---

## 1. Project Objective & Context

The **Students Database CRUD Application** is an individual backend development project built to fulfill the mandatory requirements of the **EWB Edu Tech Pvt. Ltd. Future Agents Internship** curriculum.

The primary objective is to build a reliable, beginner-friendly REST API for managing student academic records with all four standard CRUD operations (**C**reate, **R**ead, **U**pdate, and **D**elete). Data is stored persistently in a local **SQLite** database and accurately managed through a high-performance **FastAPI** application with strict schema validation powered by **Pydantic v2**.

---

## 2. Key Features

- **Complete CRUD Operations:**
  - **Create (`POST /students`):** Register new students with unique student IDs and validated contact channels.
  - **Read (`GET /students` & `GET /students/{student_id}`):** Retrieve individual student profiles by ID or list all students with pagination and search filters.
  - **Update (`PUT /students/{student_id}` & `PATCH /students/{student_id}`):** Perform full replacements via `PUT` or partial updates to selected fields via `PATCH`.
  - **Delete (`DELETE /students/{student_id}`):** Remove student records with confirmation and appropriate HTTP status codes.
- **Robust Input Validation (Pydantic v2):**
  - **Mandatory Contact Rule:** Every student record must have at least one valid contact method (email or phone).
  - **Date Constraints:** Verifies that the date of birth is a valid date in the past.
  - **Format Verification:** Enforces alphanumeric student IDs, RFC-compliant email formats, and validated phone numbers.
  - **Conflict Prevention:** Returns HTTP `409 Conflict` if a duplicate student ID or email is submitted.
- **Persistent Storage (SQLite + SQLAlchemy 2.0):**
  - Parameterized ORM queries to eliminate SQL injection vulnerabilities.
  - Auto-initialization on startup (`Base.metadata.create_all()`) that preserves existing records between server restarts.
- **Interactive Documentation:**
  - Interactive Swagger UI at `/docs`.
  - ReDoc documentation at `/redoc`.
  - Raw OpenAPI v3 specification at `/openapi.json`.
- **Comprehensive Automated Tests (Pytest):**
  - 22 automated integration tests running against an isolated in-memory test database, guaranteeing development data is never altered.
- **Safe Data Seeding Utility:**
  - Includes `scripts/seed_data.py` to populate realistic, strictly fictional student profiles for demonstration.

---

## 3. Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ (tested on Python 3.14) | Clean syntax, native typing, and async ecosystem |
| **API Framework** | FastAPI | Automatic OpenAPI docs, high performance, dependency injection |
| **ASGI Server** | Uvicorn | Production-ready asynchronous HTTP server |
| **Database** | SQLite3 | Persistent, zero-configuration local relational database |
| **ORM** | SQLAlchemy 2.0 | Safe parameterized queries and declarative modeling |
| **Validation** | Pydantic v2 & email-validator | Type-safe schema definitions and comprehensive validation rules |
| **Testing** | Pytest & HTTPX TestClient | Fast, isolated test execution with coverage of edge cases |
| **Configuration** | Python-Dotenv | Environment variable management via `.env` |

---

## 4. Project Directory Structure

```text
students-database-crud/
│
├── app/
│   ├── __init__.py           # Application package initializer
│   ├── main.py               # FastAPI entry point, lifespan, and CORS setup
│   ├── database.py           # SQLAlchemy engine, session maker, and get_db dependency
│   ├── models.py             # SQLAlchemy Student table model
│   ├── schemas.py            # Pydantic models (StudentCreate, StudentUpdate, StudentPatch, etc.)
│   ├── crud.py               # Database queries and persistence operations
│   └── routes.py             # Route handlers for /students and /health endpoints
│
├── docs/
│   └── api_testing_guide.md  # Detailed manual API testing walkthrough with cURL examples
│
├── tests/
│   ├── __init__.py           # Test package initializer
│   └── test_students.py      # Automated Pytest suite (22 tests against in-memory SQLite)
│
├── scripts/
│   ├── __init__.py           # Scripts package initializer
│   ├── seed_data.py          # Idempotent script to insert sample fictional records
│   └── qa_verification.py    # 15-step end-to-end QA verification workflow runner
│
├── data/
│   ├── .gitkeep              # Keeps the directory tracked in Git without committing .db files
│   └── students.db           # Persistent SQLite database file (created automatically)
│
├── .env.example              # Template for environment configuration
├── .gitignore                # Excludes virtual environments, cache files, and local databases
├── requirements.txt          # Explicit application dependencies
├── render.yaml               # Deployment blueprint for Render web services
└── README.md                 # Complete project guide and documentation
```

---

## 5. Prerequisites

Before setting up the project, verify that your machine has:
- **Python 3.10 or newer** installed (`python --version` or `python3 --version`).
- **pip** package installer (`pip --version`).
- A command terminal: Windows PowerShell, Command Prompt, or bash/zsh on macOS/Linux.

---

## 6. Installation & Setup

### Step 1: Clone or Navigate to the Repository
```powershell
cd students-database-crud
```

### Step 2: Create a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
```

### Step 3: Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```
> **Note for Windows Users:** If you receive an execution policy restriction error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```
> and re-run `.\.venv\Scripts\Activate.ps1`.

**On Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Environment Configuration (Optional)
The application works immediately with default local settings. If you wish to configure a custom host, port, or database path, copy `.env.example`:
```powershell
Copy-Item .env.example .env
```

---

## 7. How to Run the Application

### 1. (Optional) Seed Sample Fictional Data
To populate the database with realistic sample records before testing:
```powershell
python scripts/seed_data.py
```
*Note: This script is idempotent; it safely checks for existing records and skips duplicates without modifying existing data.*

### 2. Start the FastAPI Development Server
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

When started, Uvicorn outputs:
```text
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 8. API Base URLs & Interactive Documentation

| Resource | URL | Description |
| :--- | :--- | :--- |
| **API Base URL** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Root endpoint with overview and links |
| **Interactive Swagger UI** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Test every endpoint directly in your browser |
| **ReDoc Documentation** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) | Clean, responsive alternative documentation |
| **OpenAPI Schema** | [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) | Machine-readable OpenAPI v3 JSON specification |
| **Health Check** | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) | API & SQLite connectivity health status |

---

## 9. API Endpoint Reference

| Method | Endpoint | Purpose | Expected Status | Error Responses |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/` | API overview and documentation links | `200 OK` | - |
| `GET` | `/health` | Check API and SQLite connectivity | `200 OK` | `503 Service Unavailable` |
| `POST` | `/students` | Register a new student record | `201 Created` | `409 Conflict`, `422 Unprocessable` |
| `GET` | `/students` | List students with optional query filters | `200 OK` | `422 Unprocessable` |
| `GET` | `/students/{student_id}` | Retrieve one student profile by ID | `200 OK` | `404 Not Found` |
| `PUT` | `/students/{student_id}` | Full replacement of editable student fields | `200 OK` | `404 Not Found`, `409 Conflict`, `422` |
| `PATCH` | `/students/{student_id}` | Partial update of specified student fields | `200 OK` | `404 Not Found`, `409 Conflict`, `422` |
| `DELETE` | `/students/{student_id}` | Permanently delete a student by ID | `200 OK` | `404 Not Found` |
| `POST` | `/ask` | Ask a natural-language question grounded in SQLite records | `200 OK` | `422 Unprocessable` |


---

## 10. Copyable Request Examples

### A. Create a Student (`POST /students`)
**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/students" -Method Post -ContentType "application/json" -Body (@{
    student_id = "STU-2024-001"
    full_name = "Aarav Sharma"
    date_of_birth = "2003-04-15"
    email = "aarav.sharma@example.edu"
    phone = "+91-98765-43210"
    course = "Computer Science & Engineering"
    address = "12 Lotus Residency, Cyber City, Bangalore"
    enrollment_date = "2024-07-10"
} | ConvertTo-Json)
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU-2024-001",
    "full_name": "Aarav Sharma",
    "date_of_birth": "2003-04-15",
    "email": "aarav.sharma@example.edu",
    "phone": "+91-98765-43210",
    "course": "Computer Science & Engineering",
    "address": "12 Lotus Residency, Cyber City, Bangalore",
    "enrollment_date": "2024-07-10"
  }'
```

### B. List & Filter Students (`GET /students`)
The listing endpoint supports multiple query parameters:
- `name`: Substring match on `full_name` (case-insensitive)
- `course`: Substring match on `course` (case-insensitive)
- `enrollment_date`: Exact match on enrollment date (`YYYY-MM-DD`)
- `skip`: Pagination offset (default `0`)
- `limit`: Maximum number of records to return (default `100`, max `500`)

**Example: Filter by course and pagination:**
```bash
curl -X GET "http://127.0.0.1:8000/students?course=Computer&skip=0&limit=5"
```

**Example: Filter by student name substring:**
```bash
curl -X GET "http://127.0.0.1:8000/students?name=Sharma"
```

### C. Retrieve a Student by ID (`GET /students/{student_id}`)
```bash
curl -X GET "http://127.0.0.1:8000/students/STU-2024-001"
```

### D. Full Update (`PUT /students/{student_id}`)
Replaces all editable details. At least one contact method must be provided.
```bash
curl -X PUT "http://127.0.0.1:8000/students/STU-2024-001" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Aarav Sharma",
    "date_of_birth": "2003-04-15",
    "email": "aarav.updated@example.edu",
    "phone": "+91-98765-43210",
    "course": "Artificial Intelligence & Robotics",
    "address": "50 Silicon Park, Whitefield, Bangalore",
    "enrollment_date": "2024-07-10"
  }'
```

### E. Partial Update (`PATCH /students/{student_id}`)
Updates only the supplied fields; unmentioned fields remain unchanged:
```bash
curl -X PATCH "http://127.0.0.1:8000/students/STU-2024-001" \
  -H "Content-Type: application/json" \
  -d '{
    "course": "Robotics & Autonomous Systems",
    "phone": "+91-99887-76655"
  }'
```

### F. Delete a Student (`DELETE /students/{student_id}`)
```bash
curl -X DELETE "http://127.0.0.1:8000/students/STU-2024-001"
```
**Expected Response:**
```json
{
  "detail": "Student with ID 'STU-2024-001' was successfully deleted."
}
```

---

## 11. Automated Testing with Pytest

All tests are located in `tests/test_students.py` and run against an isolated in-memory SQLite database (`sqlite:///:memory:` with `StaticPool`). This ensures tests run quickly, concurrently, and **never alter development records** in `data/students.db`.

### Run the Complete Test Suite
```powershell
pytest -v tests
```

### Test Suite Coverage (27 Tests Total)
- [x] System root overview (`GET /`) and health check (`GET /health`).
- [x] Student creation with all fields, email only, and phone only.
- [x] Duplicate student ID conflict rejection (HTTP `409`).
- [x] Duplicate email conflict rejection (HTTP `409`).
- [x] Validation rejection when both email and phone are omitted (HTTP `422`).
- [x] Validation rejection for future date of birth (HTTP `422`).
- [x] Validation rejection for malformed email addresses (HTTP `422`).
- [x] Listing students and query filters (`name`, `course`, `enrollment_date`, `skip`, `limit`).
- [x] Retrieving existing student and non-existent student handling (HTTP `404`).
- [x] Full update (`PUT`) and duplicate email conflict check (HTTP `409`).
- [x] Partial update (`PATCH`) and safeguard preventing removal of all contact methods (HTTP `422`).
- [x] Deletion (`DELETE`) and verification that deleted records cannot be retrieved.
- [x] Multi-session SQLite persistence test verifying that records survive across database engine restarts.
- [x] Natural-language student count query with deterministic fallback.
- [x] Natural-language date filter query ("born after 2005") with exact ground truth.
- [x] Natural-language course breakdown query ("students enrolled in each course").
- [x] Validation error handling for empty or whitespace-only natural language queries (HTTP `422`).
- [x] Mocked live Ollama response verification (`source="ollama"`, `status="success"`).

---

## 12. SQLite Persistence & Database Location

- **Database Location:** Local file stored at `data/students.db` relative to the project root.
- **Persistence Mechanism:** All CRUD operations perform explicit database commits. SQLite writes directly to the disk file.
- **Safe Lifecycle:** When the server starts up, `init_db()` executes `Base.metadata.create_all()`. This only creates tables if they do not exist; it **never drops, wipes, or recreates existing tables**.

---

## 13. Security, Privacy & Data Handling Notes

1. **Strictly Fictional Data:**  
   Per EWB Edu Tech Pvt. Ltd. internship guidelines, **no real student personal information is used or stored**. All seed records and test cases utilize synthetic names and `@example.edu` emails.
2. **SQL Injection Prevention:**  
   All queries are built using SQLAlchemy 2.0 ORM and parameterized query compilation. Raw string concatenation in SQL is strictly prohibited.
3. **No Secret Keys in Git:**  
   The application does not contain hard-coded API keys, passwords, or secrets. Environment variables are loaded safely via `.env` and excluded via `.gitignore`.
4. **No Unrestricted Model Access:**  
   The local language model is never given raw database handles or arbitrary SQL execution rights. Only verified, sanitized data extracts are passed as prompt context.

---

## 14. Current Limitations & Deployment Considerations

- **Single-Node SQLite:** SQLite is designed for single-instance applications. For high-concurrency distributed deployments across multiple containers, replace `DATABASE_URL` with a managed database service such as PostgreSQL.
- **Cloud Hosting & Ephemeral Disks:** When deploying to free-tier cloud platforms (such as Render or Railway), container disks are ephemeral and reset during application sleep or re-deploys. For permanent data retention in production, mount a persistent disk volume or connect to an external hosted SQL database.
- **Render Deployment Blueprint:** A pre-configured `render.yaml` file is included in the project for seamless deployment:
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Future Live URL:**
  `[Future Live URL - To Be Configured After Deployment]` *(This placeholder will be updated with the live hosting link once deployed to a public cloud provider).*

---

## 15. Optional AI Extension (Local Ollama Integration)

The project includes the optional bonus challenge from the assignment brief: an AI assistant grounded in the SQLite database using a local **Ollama** model (e.g. `llama3.2:1b`).

### Architecture & Grounding Principle
- **Core CRUD Independence:** The core CRUD API runs 100% independently. Starting the API does **not** require Ollama.
- **Deterministic Facts First:** When a user asks a question via `POST /ask`, Python and SQLite first calculate the exact, verified truth (e.g., student counts, course breakdowns, or date ranges).
- **No Unrestricted SQL Execution:** The model is never permitted to execute SQL, run terminal commands, or alter records.
- **Graceful Fallback:** If Ollama is not installed or currently offline, the API automatically falls back to the verified deterministic facts, returning HTTP `200 OK` with `source="deterministic_fallback"`.

### Supported Question Patterns
- `"How many students are there?"` -> Computes exact count from SQLite.
- `"List students born after 2005."` -> Filters students born after December 31, 2005.
- `"How many students are enrolled in each course?"` -> Groups by course and returns exact enrollment counts.
- Course queries (e.g., `"Who is enrolled in Computer Science?"`).

### How to Install and Run Ollama (Optional)
To test the live local LLM:

1. **Install Ollama:**
   - **Windows:** Download the installer from [ollama.com/download/windows](https://ollama.com/download/windows).
   - **macOS:** Download from [ollama.com/download/mac](https://ollama.com/download/mac) or install via Homebrew: `brew install ollama`.
   - **Linux:** Run `curl -fsSL https://ollama.com/install.sh | sh`.

2. **Pull the Model:**
   ```powershell
   ollama pull llama3.2:1b
   ```
   *(You can also use other models like `llama3.2` or `mistral` by setting `OLLAMA_MODEL` in `.env`)*.

3. **Verify Ollama is Running:**
   ```powershell
   ollama list
   ```
   *(Ollama automatically starts its background server at `http://localhost:11434`)*.

4. **Test the Endpoint via cURL or PowerShell:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "How many students are enrolled in each course?"
     }'
   ```
   **Response with Ollama Online:**
   ```json
   {
     "question": "How many students are enrolled in each course?",
     "answer": "Based on the verified records, there are 2 students in Computer Science & Engineering, 1 in Data Science & Artificial Intelligence, 1 in Information Technology, and 1 in Cyber Security.",
     "grounded_facts": {
       "total_students": 5,
       "course_breakdown": {
         "Computer Science & Engineering": 2,
         "Data Science & Artificial Intelligence": 1,
         "Information Technology": 1,
         "Cyber Security": 1
       }
     },
     "source": "ollama",
     "status": "success",
     "model": "llama3.2:1b"
   }
   ```

---

## 16. Author & Attribution

- **Project:** Students Database CRUD Application
- **Internship:** Future Agents Internship Program — EWB Edu Tech Pvt. Ltd.
- **Developer:** Parth

