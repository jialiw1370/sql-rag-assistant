# Day 15: main.py — FastAPI app with vector search (SQL RAG Assistant)
# This file REPLACES the Day 5 main.py in the repo root (same filename,
# new version). Copy only this file to the sql-rag-assistant folder,
# next to schema.sql. Do not push the day-15-en folder itself.
#
# New in Day 15:
#   GET  /search?q=...      -> top 3 vector matches from Chroma
#                              (id, title, question, answer_sql) as JSON
#   GET  / and GET /cases, GET /cases/{id}, POST /cases/{id}/check,
#   GET  /page              -> unchanged from Day 5
#
# Prerequisite: Day 13 must have run once so ./chroma_db exists:
#   py embed_cases.py
# If chroma_db/ is missing, /search returns 503 with a clear message
# instead of crashing the whole app — /cases keeps working either way.
#
# Usage (in the sql-rag-assistant repo root, after Day 14 is done):
#   py -m uvicorn main:app --reload
# Then open in your browser:
#   http://127.0.0.1:8000/search?q=How%20do%20I%20write%20a%20JOIN%3F
#   http://127.0.0.1:8000/cases      -> still returns all 18 cases
#   http://127.0.0.1:8000/docs       -> try /search here too
# Commit message: add vector search endpoint
#
# Note: this file only reads the cases Day 2 put into sql_rag.db and
# the vectors Day 13 put into chroma_db/. It does not invent any case
# titles, questions, or SQL.

import re
import sqlite3
from pathlib import Path

import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="SQL RAG Assistant")

BASE_DIR = Path(__file__).resolve().parent
# sql_rag.db lives in the repo root, next to this file.
# *.db is already in the Day 1 .gitignore, so it will not be pushed to GitHub.
DB_PATH = BASE_DIR / "sql_rag.db"
CHROMA_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "sql_cases"


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


def search_cases(question: str, top_n: int = 3):
    """Vector-search Chroma, then load the full cases from SQLite.

    Chroma only stores the case id (plus title metadata), so the
    full question/answer_sql always comes from sql_rag.db — one
    source of truth, in Chroma's relevance order.
    """
    if not CHROMA_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Vector store not found. Run Day 13 first: py embed_cases.py",
        )
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Collection '{COLLECTION_NAME}' not found in chroma_db/. "
                "Re-run: py embed_cases.py"
            ),
        )
    results = collection.query(query_texts=[question], n_results=top_n)
    hits = []
    for case_id in results["ids"][0]:
        case = get_case(int(case_id))
        if case is not None:
            hits.append(case)
    return hits


class CheckRequest(BaseModel):
    sql: str


@app.get("/")
def read_root():
    return {"message": "Hello, SQL RAG Assistant!"}


@app.get("/page")
def read_page():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/cases")
def read_cases():
    return get_cases()


@app.get("/search")
def read_search(q: str):
    return search_cases(q)


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
