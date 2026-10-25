# Deployment Guide — Students Database CRUD Application

**Project:** Students Database CRUD Application  
**Target Platform:** Render (or any Python-compatible PaaS such as Railway, Fly.io, or AWS App Runner)  
**Framework:** FastAPI + SQLite3 (SQLAlchemy 2.0 ORM)  

This guide provides step-by-step instructions for deploying the backend to a cloud hosting platform safely and reliably.

---

## 1. Application Architecture & Configuration

| Parameter | Configuration | Notes |
| :--- | :--- | :--- |
| **FastAPI Import Path** | `app.main:app` | FastAPI instance `app` inside `app/main.py` |
| **Build Command** | `pip install -r requirements.txt` | Installs FastAPI, Uvicorn, SQLAlchemy, Pydantic, etc. |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Binds to all interfaces and respects dynamic `$PORT` |
| **Health Check Endpoint** | `/health` | Returns `200 OK` when SQLite connection is verified |
| **Swagger UI Documentation**| `/docs` | Interactive API documentation |
| **OpenAPI Schema** | `/openapi.json` | Raw OpenAPI v3 JSON definition |

---

## 2. Critical Notice on SQLite Persistence & Cloud Filesystems

> [!WARNING]
> **Ephemeral Storage on Cloud Free Tiers:**  
> On free-tier cloud hosting (such as the Render Free tier), container filesystems are **ephemeral**. This means:
> 1. Any records written to `data/students.db` persist while the container is running.
> 2. When the free service sleeps due to inactivity (after 15 minutes), restarts, or redeploys, the container filesystem is **reset to the Git state**.
> 3. Therefore, SQLite records created on the free tier will not persist permanently across instance recycles unless a persistent volume/disk is attached.

### Persistent Storage Options for SQLite

To achieve permanent SQLite persistence across redeployments:

1. **Render Persistent Disk (Starter Plan or higher):**
   - Cost: Requires upgrading from Free to a paid instance (e.g. Starter ~$7/month) plus persistent disk ($0.25/GB/month).
   - Setup: Attach a disk with `mountPath: /var/data` and set environment variable `DATABASE_URL=sqlite:////var/data/students.db`.
2. **Fly.io Persistent Volumes:**
   - Supports mounting permanent volume to `/data` (`fly volumes create`).
3. **Railway Persistent Volumes:**
   - Railway supports adding a Volume mounted to `/app/data`.

For internship demonstrations and grading, the default `render.yaml` free tier setup is sufficient to demonstrate all CRUD operations, automated tests, Swagger UI, and `/health`.

---

## 3. Step-by-Step Render Deployment (Manual Setup)

1. **Sign Up / Log In to Render:**  
   Go to [dashboard.render.com](https://dashboard.render.com/) and sign in with your GitHub account.

2. **Create a New Web Service:**  
   - Click **New +** > **Web Service**.
   - Select **Build and deploy from a Git repository**.
   - Choose your repository: `parthivlella-ai/Students-Database-CRUD`.

3. **Configure Service Settings:**
   - **Name:** `students-database-crud`
   - **Region:** Choose the region nearest to you (e.g., Oregon or Frankfurt).
   - **Branch:** `main`
   - **Root Directory:** Leave blank (if repo root) or `students-database-crud`.
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`

4. **Configure Environment Variables:**
   Under **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.12.0`
   - `DATABASE_URL`: `sqlite:///./data/students.db`
   - `ALLOWED_ORIGINS`: `*` (or your frontend domain URL for strict security)

5. **Configure Health Check:**
   - Expand **Advanced**.
   - Set **Health Check Path** to `/health`.

6. **Deploy the Service:**
   - Click **Create Web Service**.
   - Render will clone the repository, run the build command, and start Uvicorn.
   - Once deployed, your service will be assigned a live URL:  
     `https://students-database-crud-<hash>.onrender.com`

---

## 4. Alternative: Deploy Using Render Blueprint (`render.yaml`)

Because the repository includes [`render.yaml`](../render.yaml), you can also use Render's Blueprint feature:
1. In your Render Dashboard, click **New +** > **Blueprint**.
2. Select `parthivlella-ai/Students-Database-CRUD`.
3. Render automatically detects `render.yaml`, configures the build/start commands, sets environment variables, and configures the `/health` check.
4. Click **Apply**.

---

## 5. Monitoring & Inspecting Logs

1. In your Render Dashboard, click into your service.
2. Select the **Logs** tab:
   - Verify application startup:
     ```text
     INFO:     Started server process
     INFO:     Waiting for application startup.
     INFO:     Application startup complete.
     INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
     ```
   - Watch incoming HTTP requests in real time.

---

## 6. Testing the Deployed Application Safely

> [!IMPORTANT]
> **Data Privacy Notice:** When testing your live deployment, **never use real student personal data**. Use strictly fictional sample records.

### 1. Verify Health Status
Open your browser or terminal:
```bash
curl -X GET "https://<YOUR-RENDER-URL>.onrender.com/health"
```
**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### 2. Verify Interactive Documentation
Visit:
```text
https://<YOUR-RENDER-URL>.onrender.com/docs
```
Confirm that Swagger UI loads with all endpoints, models, and "Try it out" buttons.

### 3. Test Student Creation (Fictional Data)
```bash
curl -X POST "https://<YOUR-RENDER-URL>.onrender.com/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU-PROD-01",
    "full_name": "Aarav Sharma",
    "date_of_birth": "2003-04-15",
    "email": "aarav.sharma@example.edu",
    "phone": "+91-98765-43210",
    "course": "Computer Science & Engineering"
  }'
```
**Expected Response:** Status `201 Created` with serialized student JSON.

### 4. Test Student Query
```bash
curl -X GET "https://<YOUR-RENDER-URL>.onrender.com/students/STU-PROD-01"
```
**Expected Response:** Status `200 OK`.
