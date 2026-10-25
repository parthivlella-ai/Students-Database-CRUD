"""
Database configuration and session management for Students Database CRUD.
Uses SQLite with SQLAlchemy ORM.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Base directory for the project (students-database-crud)
BASE_DIR = Path(__file__).resolve().parent.parent

# Database URL from environment variable or default local SQLite database in ./data/
DEFAULT_DB_PATH = BASE_DIR / "data" / "students.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# Ensure the directory for SQLite exists if using a file-based SQLite database
if DATABASE_URL.startswith("sqlite:///"):
    db_file_path = DATABASE_URL.replace("sqlite:///", "")
    # If not in-memory, create directory
    if db_file_path and db_file_path != ":memory:":
        target_dir = os.path.dirname(os.path.abspath(db_file_path))
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

# Create SQLAlchemy engine
# connect_args={"check_same_thread": False} is required for SQLite in multi-threaded FastAPI
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy database session per request.
    Ensures that the session is properly closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables safely.
    Uses SQLAlchemy's create_all(), which only creates tables that do not already exist
    and never drops or overwrites existing data.
    """
    Base.metadata.create_all(bind=engine)
