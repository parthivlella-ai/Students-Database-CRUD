"""
Main application entry point for Students Database CRUD API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Ensures that database tables are safely created on startup without
    overwriting or dropping existing data.
    """
    init_db()
    yield


app = FastAPI(
    title="Students Database CRUD Application",
    description="""
## Future Agents Internship — EWB Edu Tech Pvt. Ltd.

A robust, production-grade Python backend REST API built with **FastAPI** and **SQLite** for managing student records.

### Key Features:
* **Full CRUD Operations**: Create, Read, Update (PUT/PATCH), and Delete student records.
* **Input Validation**: Rigorous validation with Pydantic v2 for student IDs, dates, email addresses, and phone numbers.
* **Persistent Storage**: Automated SQLite table creation preserving data across restarts.
* **Interactive Documentation**: Test endpoints directly via Swagger UI (`/docs`) and ReDoc (`/redoc`).
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

import os

# Configure CORS origins safely (configurable via ALLOWED_ORIGINS env variable)
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, tags=["Students"])


@app.get(
    "/",
    tags=["System"],
    summary="Root Welcome & API Overview",
    description="Welcome endpoint providing API status and quick links to documentation.",
)
def root_endpoint():
    """
    Root endpoint for API status and documentation links.
    """
    return JSONResponse(
        content={
            "project": "Students Database CRUD Application",
            "organization": "EWB Edu Tech Pvt. Ltd. - Future Agents Internship",
            "version": "1.0.0",
            "status": "online",
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json",
            },
            "endpoints": {
                "health": "/health",
                "students": "/students",
                "ask_ai": "/ask",
            },
        }
    )
