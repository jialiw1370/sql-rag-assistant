# Day 3 (Wed 11/11): main.py — FastAPI app for the SQL RAG Assistant
# Usage (in the sql-rag-assistant repo root, after Day 2 is done):
#   pip install -r requirements.txt
#   uvicorn main:app --reload
# Then open in your browser:
#   http://127.0.0.1:8000/        -> {"message": "Hello, SQL RAG Assistant!"}
#   http://127.0.0.1:8000/cases   -> JSON list of the cases from sql_rag.db
# Commit message: add FastAPI endpoint to list cases
#
# Note: this file only reads the cases Day 2 put into sql_rag.db.
# It does not invent any case titles, questions, or SQL.
# If sql_rag.db does not exist yet, run Day 2 first:
#   sqlite3 sql_rag.db < schema.sql

import sqlite3
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="SQL RAG Assistant")

# sql_rag.db lives in the repo root, next to this file.
# *.db is already in the Day 1 .gitignore, so it will not be pushed to GitHub.
DB_PATH = Path(__file__).resolve().parent / "sql_rag.db"


def get_cases():
    """Read all cases from SQLite, in id order."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT id, title, question, answer_sql FROM cases ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


@app.get("/")
def read_root():
    return {"message": "Hello, SQL RAG Assistant!"}


@app.get("/cases")
def read_cases():
    return get_cases()
