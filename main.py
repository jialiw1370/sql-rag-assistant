# Day 5 (Fri 11/13): main.py — FastAPI app for the SQL RAG Assistant
# This file REPLACES the Day 4 main.py in the repo root (same filename,
# new version). Copy only this file, plus index.html, to the
# sql-rag-assistant folder, next to schema.sql. Do not push the
# day-5-en folder itself.
#
# New in Day 5:
#   GET  /page              -> serves index.html (the simple HTML page)
#   GET  /cases/{id}        -> one case by id (404 if the id does not exist)
#   POST /cases/{id}/check  -> submit SQL, get back correct / incorrect
#   GET  / and GET /cases   -> unchanged from Day 3
#
# How the checker works (simplest version):
#   It compares your SQL with the book's answer SQL as text — lowercased,
#   extra spaces collapsed, spaces around "=" ignored, trailing semicolon
#   ignored — so "select name from customers" counts as correct for
#   Case 1, and "name='Leo'" counts as correct for Case 3.
#   It does NOT run your SQL against a sample table, because the book's
#   cases (Customers, Clients, Trainers) ship no sample data to run
#   against. A text comparison is the honest Day 4 version; running SQL
#   against real tables comes later, once there is data for them.
#
# Usage (in the sql-rag-assistant repo root, after Day 4 is done):
#   pip install -r requirements.txt
#   uvicorn main:app --reload
# Then open in your browser:
#   http://127.0.0.1:8000/page          -> the HTML page (use this, not
#     double-clicking index.html, so the page and the API share one
#     address and the browser does not block the calls)
#   http://127.0.0.1:8000/cases/1      -> Case 1 as JSON
#   http://127.0.0.1:8000/docs        -> try POST /cases/{id}/check here
# Commit message: add simple HTML page to list cases and submit SQL
#
# Note: this file only reads the cases Day 2 put into sql_rag.db.
# It does not invent any case titles, questions, or SQL.
# If sql_rag.db does not exist yet, run Day 2 first:
#   sqlite3 sql_rag.db < schema.sql

import re
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="SQL RAG Assistant")

# sql_rag.db lives in the repo root, next to this file.
# *.db is already in the Day 1 .gitignore, so it will not be pushed to GitHub.
DB_PATH = Path(__file__).resolve().parent / "sql_rag.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_case(case_id: int):
    """Read one case by id, or None if it does not exist."""
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT id, title, question, answer_sql FROM cases WHERE id = ?",
            (case_id,),
        ).fetchone()
        return dict(row) if row is not None else None
    finally:
        connection.close()


def get_cases():
    """Read all cases from SQLite, in id order."""
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT id, title, question, answer_sql FROM cases ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def normalize_sql(sql: str) -> str:
    """Lowercase, drop a trailing semicolon, collapse whitespace.

    Also ignores spaces around "=" so "name='Leo'" matches the book's
    "Name = 'Leo'". The checker compares submitted SQL with the book's
    answer SQL as text. It does not run the SQL, because the book's
    cases name tables (Customers, Clients, Trainers) for which no
    sample data exists yet.
    """
    text = sql.strip().lower()
    if text.endswith(";"):
        text = text[:-1]
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s*=\s*", "=", text)


class CheckRequest(BaseModel):
    sql: str


@app.get("/")
def read_root():
    return {"message": "Hello, SQL RAG Assistant!"}


@app.get("/page")
def read_page():
    return FileResponse(Path(__file__).resolve().parent / "index.html")


@app.get("/cases")
def read_cases():
    return get_cases()


@app.get("/cases/{case_id}")
def read_case(case_id: int):
    case = get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.post("/cases/{case_id}/check")
def check_case(case_id: int, body: CheckRequest):
    case = get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    correct = normalize_sql(body.sql) == normalize_sql(case["answer_sql"])
    result = {"case_id": case_id, "correct": correct}
    if correct:
        result["message"] = "Correct!"
    else:
        result["message"] = "Not quite — compare with the book answer:"
        result["expected"] = case["answer_sql"]
    return result
