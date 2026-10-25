# API Testing Guide — Students Database CRUD Application

**Project:** Students Database CRUD Application  
**Internship Assignment:** Future Agents Internship — EWB Edu Tech Pvt. Ltd.  
**Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
**ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)  
**OpenAPI Specification:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)  

This guide provides step-by-step instructions for testing every endpoint implemented in the API using either Swagger UI or terminal commands (PowerShell / cURL).

---

## 1. Quick Start: Interactive Testing via Swagger UI (`/docs`)

1. Start the server:
   ```powershell
   cd students-database-crud
   .\.venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload
   ```
2. Open your web browser and navigate to:
   ```text
   http://127.0.0.1:8000/docs
   ```
3. Expand any route card (e.g., `POST /students`), click the **Try it out** button, fill in the sample parameters, and click **Execute**.
4. Inspect the **Response Body**, **Response Headers**, and **HTTP Status Code**.

---

## 2. Testing Endpoints via Terminal (cURL & PowerShell)

### Test 1: Check System Health
- **Endpoint:** `GET /health`
- **Expected Status:** `200 OK`
- **Expected Body:**
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "version": "1.0.0"
  }
  ```
- **PowerShell:**
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
  ```
- **cURL:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/health"
  ```

---

### Test 2: Register a New Student (All Fields)
- **Endpoint:** `POST /students`
- **Expected Status:** `201 Created`
- **PowerShell:**
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:8000/students" -Method Post -ContentType "application/json" -Body (@{
      student_id = "STU-DEMO-01"
      full_name = "Kavita Rao"
      date_of_birth = "2003-04-12"
      email = "kavita.rao@example.edu"
      phone = "+91-98765-00101"
      course = "Computer Science & Engineering"
      address = "12 Residency Road, Pune, Maharashtra"
      enrollment_date = "2024-08-01"
  } | ConvertTo-Json)
  ```
- **cURL:**
  ```bash
  curl -X POST "http://127.0.0.1:8000/students" \
    -H "Content-Type: application/json" \
    -d '{
      "student_id": "STU-DEMO-01",
      "full_name": "Kavita Rao",
      "date_of_birth": "2003-04-12",
      "email": "kavita.rao@example.edu",
      "phone": "+91-98765-00101",
      "course": "Computer Science & Engineering",
      "address": "12 Residency Road, Pune, Maharashtra",
      "enrollment_date": "2024-08-01"
    }'
  ```

---

### Test 3: Register a Student with Only Phone (No Email)
- **Endpoint:** `POST /students`
- **Expected Status:** `201 Created`
- **Note:** The validation schema requires at least one contact channel (email or phone). Providing only a phone is valid.
- **cURL:**
  ```bash
  curl -X POST "http://127.0.0.1:8000/students" \
    -H "Content-Type: application/json" \
    -d '{
      "student_id": "STU-DEMO-02",
      "full_name": "Tariq Ali",
      "date_of_birth": "2002-09-10",
      "phone": "+91-98111-22233",
      "course": "Mechanical Engineering"
    }'
  ```

---

### Test 4: List All Students & Filter by Course or Name
- **Endpoint:** `GET /students`
- **Supported Query Parameters:**
  - `name`: Substring match on full name (case-insensitive)
  - `course`: Filter by course name (case-insensitive)
  - `enrollment_date`: Filter by exact date (`YYYY-MM-DD`)
  - `skip`: Number of records to skip (default `0`)
  - `limit`: Number of records to return (default `100`, max `500`)
- **Filter Example (Course = "Computer"):**
  ```bash
  curl -X GET "http://127.0.0.1:8000/students?course=Computer&limit=5"
  ```
- **Filter Example (Name Substring = "Kavita"):**
  ```bash
  curl -X GET "http://127.0.0.1:8000/students?name=Kavita"
  ```

---

### Test 5: Retrieve a Student by ID
- **Endpoint:** `GET /students/{student_id}`
- **Expected Status:** `200 OK`
- **cURL:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/students/STU-DEMO-01"
  ```

---

### Test 6: Full Replacement Update (PUT)
- **Endpoint:** `PUT /students/{student_id}`
- **Expected Status:** `200 OK`
- **cURL:**
  ```bash
  curl -X PUT "http://127.0.0.1:8000/students/STU-DEMO-01" \
    -H "Content-Type: application/json" \
    -d '{
      "full_name": "Kavita Rao",
      "date_of_birth": "2003-04-12",
      "email": "kavita.updated@example.edu",
      "phone": "+91-98765-00101",
      "course": "Artificial Intelligence & Data Science",
      "address": "45 Innovation Hub, Pune",
      "enrollment_date": "2024-08-01"
    }'
  ```

---

### Test 7: Partial Update (PATCH)
- **Endpoint:** `PATCH /students/{student_id}`
- **Expected Status:** `200 OK`
- **Note:** Only fields included in the request body are modified.
- **cURL:**
  ```bash
  curl -X PATCH "http://127.0.0.1:8000/students/STU-DEMO-01" \
    -H "Content-Type: application/json" \
    -d '{
      "course": "Robotics & Embedded Systems"
    }'
  ```

---

### Test 8: Conflict Handling on Duplicate Student ID
- **Endpoint:** `POST /students`
- **Expected Status:** `409 Conflict`
- **Test:** Submit the exact same `student_id` (`STU-DEMO-01`) again.
- **Expected Response Body:**
  ```json
  {
    "detail": "Student with ID 'STU-DEMO-01' already exists."
  }
  ```

---

### Test 9: Input Validation Handling (HTTP 422)
- **Endpoint:** `POST /students`
- **Expected Status:** `422 Unprocessable Content`
- **Test:** Omit both `email` and `phone` or specify a future `date_of_birth`:
  ```bash
  curl -X POST "http://127.0.0.1:8000/students" \
    -H "Content-Type: application/json" \
    -d '{
      "student_id": "STU-INVALID",
      "full_name": "Invalid Student",
      "date_of_birth": "2099-01-01"
    }'
  ```

---

### Test 10: Non-Existent Record Handling (HTTP 404)
- **Endpoint:** `GET /students/NONEXISTENT-999`
- **Expected Status:** `404 Not Found`
- **Expected Response Body:**
  ```json
  {
    "detail": "Student with ID 'NONEXISTENT-999' was not found."
  }
  ```

---

### Test 11: Delete a Student Record
- **Endpoint:** `DELETE /students/{student_id}`
- **Expected Status:** `200 OK`
- **cURL:**
  ```bash
  curl -X DELETE "http://127.0.0.1:8000/students/STU-DEMO-02"
  ```
- **Expected Response Body:**
  ```json
  {
    "detail": "Student with ID 'STU-DEMO-02' was successfully deleted."
  }
  ```
- **Follow-up Check:** Calling `GET /students/STU-DEMO-02` immediately returns `404 Not Found`.

---

### Test 12: Ask a Natural-Language Question (Optional AI Extension)
- **Endpoint:** `POST /ask`
- **Expected Status:** `200 OK`
- **Description:** Grounded natural-language query. Returns verified SQLite facts along with an answer from local Ollama (or deterministic fallback if Ollama is not running).
- **cURL (Total Count):**
  ```bash
  curl -X POST "http://127.0.0.1:8000/ask" \
    -H "Content-Type: application/json" \
    -d '{
      "question": "How many students are there?"
    }'
  ```
- **cURL (Course Breakdown):**
  ```bash
  curl -X POST "http://127.0.0.1:8000/ask" \
    -H "Content-Type: application/json" \
    -d '{
      "question": "How many students are enrolled in each course?"
    }'
  ```
- **cURL (Date Filter):**
  ```bash
  curl -X POST "http://127.0.0.1:8000/ask" \
    -H "Content-Type: application/json" \
    -d '{
      "question": "List students born after 2005."
    }'
  ```
- **Expected Response Example:**
  ```json
  {
    "question": "How many students are enrolled in each course?",
    "answer": "Course enrollment breakdown across all 5 students: Computer Science & Engineering: 2, Data Science & Artificial Intelligence: 1, Information Technology: 1, Cyber Security: 1.",
    "grounded_facts": {
      "total_students": 5,
      "course_breakdown": {
        "Computer Science & Engineering": 2,
        "Data Science & Artificial Intelligence": 1,
        "Information Technology": 1,
        "Cyber Security": 1
      }
    },
    "source": "deterministic_fallback",
    "status": "ollama_offline: Ollama service is not running at http://localhost:11434.",
    "model": "llama3.2:1b"
  }
  ```


---

## 3. Automated Testing

To run all 22 automated integration and unit tests:
```powershell
pytest -v tests
```
The test suite utilizes an isolated in-memory SQLite database so that running tests never modifies or deletes your development database (`data/students.db`).
