"""
Optional AI service integration using local Ollama.
Grounded in deterministic SQLite database queries.
"""

from datetime import date
import os
import re
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Student

# Configurable Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "10.0"))


def fetch_grounded_facts(db: Session, question: str) -> Dict[str, Any]:
    """
    Deterministic SQLite facts extraction based on the user's question.
    Extracts exact counts, filtered lists, or breakdowns to provide as
    grounded context for the language model.
    """
    q_lower = question.lower().strip()
    facts: Dict[str, Any] = {}

    # Total count query
    total_count = db.query(Student).count()
    facts["total_students"] = total_count

    # 1. Check for "born after/before/in <year>"
    born_match = re.search(r"born\s+(after|before|in)\s+(\d{4})", q_lower)
    if born_match:
        condition, year_str = born_match.groups()
        year = int(year_str)
        facts["filter_applied"] = f"born {condition} {year}"

        query = db.query(Student)
        if condition == "after":
            cutoff = date(year, 12, 31)
            matched = query.filter(Student.date_of_birth > cutoff).all()
        elif condition == "before":
            cutoff = date(year, 1, 1)
            matched = query.filter(Student.date_of_birth < cutoff).all()
        else:  # "in"
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            matched = query.filter(Student.date_of_birth >= start_date, Student.date_of_birth <= end_date).all()

        facts["matched_count"] = len(matched)
        facts["matched_students"] = [
            {
                "student_id": s.student_id,
                "full_name": s.full_name,
                "date_of_birth": s.date_of_birth.isoformat() if s.date_of_birth else None,
                "course": s.course,
            }
            for s in matched
        ]
        return facts

    # 2. Check for "enrolled in each course" or "course breakdown"
    if any(k in q_lower for k in ["each course", "per course", "course breakdown", "by course"]):
        breakdown = (
            db.query(Student.course, func.count(Student.student_id))
            .group_by(Student.course)
            .all()
        )
        facts["course_breakdown"] = {
            (course or "Unassigned"): count for course, count in breakdown
        }
        return facts

    # 3. Check for specific course query (e.g., "Computer Science")
    courses = db.query(Student.course).filter(Student.course.isnot(None)).distinct().all()
    matched_course = None
    for (c,) in courses:
        if c and c.lower() in q_lower:
            matched_course = c
            break

    if matched_course:
        students_in_course = db.query(Student).filter(Student.course == matched_course).all()
        facts["filter_applied"] = f"course: {matched_course}"
        facts["matched_count"] = len(students_in_course)
        facts["matched_students"] = [
            {"student_id": s.student_id, "full_name": s.full_name} for s in students_in_course
        ]
        return facts

    # 4. Simple count question
    if any(k in q_lower for k in ["how many", "total count", "number of students", "count"]):
        return facts

    # 5. Default overview (names and courses only, preserving privacy)
    students = db.query(Student).limit(20).all()
    facts["student_overview"] = [
        {"student_id": s.student_id, "full_name": s.full_name, "course": s.course}
        for s in students
    ]
    return facts


def generate_deterministic_summary(question: str, facts: Dict[str, Any]) -> str:
    """
    Construct a reliable, deterministic human-readable answer directly from
    the SQLite facts when Ollama is unavailable or offline.
    """
    total = facts.get("total_students", 0)

    if "course_breakdown" in facts:
        breakdown = facts["course_breakdown"]
        breakdown_str = ", ".join(f"{course}: {count}" for course, count in breakdown.items())
        return f"Course enrollment breakdown across all {total} students: {breakdown_str}."

    if "filter_applied" in facts and "matched_students" in facts:
        matched = facts["matched_students"]
        filter_name = facts["filter_applied"]
        if not matched:
            return f"No students found matching the condition '{filter_name}'."
        names = ", ".join(f"{s['full_name']} ({s['student_id']})" for s in matched)
        return f"Found {len(matched)} student(s) {filter_name}: {names}."

    if any(k in question.lower() for k in ["how many", "count", "number"]):
        return f"There are currently {total} student record(s) registered in the database."

    return f"The database contains {total} student record(s)."


def ask_ollama(question: str, facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send question and grounded facts to local Ollama.
    Falls back gracefully if Ollama is not installed, not running, or times out.
    """
    system_prompt = (
        "You are a helpful student database assistant for EWB Edu Tech. "
        "Answer the user's question using ONLY the provided verified database facts. "
        "Do not invent facts, student names, or numbers not present in the context. "
        "Keep the response concise, factual, and polite."
    )

    prompt = (
        f"{system_prompt}\n\n"
        f"Verified Database Context:\n{facts}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    try:
        with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
            response = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
            )

            if response.status_code == 200:
                data = response.json()
                ai_answer = data.get("response", "").strip()
                return {
                    "answer": ai_answer,
                    "source": "ollama",
                    "status": "success",
                    "model": OLLAMA_MODEL,
                }
            elif response.status_code == 404:
                return {
                    "answer": generate_deterministic_summary(question, facts),
                    "source": "deterministic_fallback",
                    "status": f"model_not_found: Model '{OLLAMA_MODEL}' is not pulled in Ollama. Run 'ollama pull {OLLAMA_MODEL}'.",
                    "model": OLLAMA_MODEL,
                }
            else:
                return {
                    "answer": generate_deterministic_summary(question, facts),
                    "source": "deterministic_fallback",
                    "status": f"ollama_http_error_{response.status_code}",
                    "model": OLLAMA_MODEL,
                }
    except httpx.ConnectError:
        return {
            "answer": generate_deterministic_summary(question, facts),
            "source": "deterministic_fallback",
            "status": f"ollama_offline: Ollama service is not running at {OLLAMA_BASE_URL}.",
            "model": OLLAMA_MODEL,
        }
    except httpx.TimeoutException:
        return {
            "answer": generate_deterministic_summary(question, facts),
            "source": "deterministic_fallback",
            "status": "ollama_timeout: Ollama request timed out.",
            "model": OLLAMA_MODEL,
        }
    except Exception as exc:
        return {
            "answer": generate_deterministic_summary(question, facts),
            "source": "deterministic_fallback",
            "status": f"ollama_error: {str(exc)}",
            "model": OLLAMA_MODEL,
        }
