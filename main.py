# Day 18: main.py — FastAPI app with POST /ask (SQL RAG Assistant)
# This file REPLACES the Day 15 main.py in the repo root (same filename,
# new version). Copy only this file to the sql-rag-assistant folder,
# next to schema.sql. Do not push the day-18-en folder itself.
#
# New in Day 18:
#   POST /ask  {"question": "..."} -> the full RAG answer in one call:
#     {"question": "...",
#      "cases": [top 3 vector matches, same shape as GET /search],
#      "explanation": "short LLM explanation naming the cases"}
#   This is the endpoint the chat box (Day 19) will call. It reuses
#   Day 15's vector retrieval and Day 16's prompt + gpt-4o-mini call.
#
#   If chroma_db/ is missing, /ask returns 503 (same as /search).
#   If OPENAI_API_KEY is not set, /ask returns 503 with the .env
#   instructions instead of crashing. If OpenAI rejects the call
#   (for example 401 bad key, 429 no credits), /ask returns 502
#   with OpenAI's message, so the page can show it.
#
# Prerequisite: Day 13 must have run once so ./chroma_db exists,
# and .env must hold a real OPENAI_API_KEY with credit (Day 16).
# No new package is needed: openai and python-dotenv are already
# in requirements.txt since Day 16.
#
# Test it in the browser at /docs (POST /ask, Try it out):
#   {"question": "How do I write a JOIN?"}
# Done when it returns 200 with cases [17, 18, 1] and an explanation
# that names Case 17 or 18.
# Commit message: add ask endpoint that answers with retrieval plus LLM

import os
import re
import sqlite3
from pathlib import Path

import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; the key must be set in the terminal

app = FastAPI(title="SQL RAG Assistant")

BASE_DIR = Path(__file__).resolve().parent
# sql_rag.db lives in the repo root, next to this file.
# *.db is already in the Day 1 .gitignore, so it will not be pushed to GitHub.
DB_PATH = BASE_DIR / "sql_rag.db"
CHROMA_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "sql_cases"
MODEL = "gpt-4o-mini"


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


def build_prompt(question: str, cases: list) -> str:
    """Put the question and the retrieved cases into one prompt.

    Same prompt as Day 16's explain.py: the model only ever sees
    your book's cases — it explains those, it does not invent new SQL.
    """
    lines = [
        "You explain SQL to a beginner who is learning from a book of "
        "SQL case studies. Use ONLY the cases below to answer. "
        "Explain in short, simple words, name the case numbers you use, "
        "and show one SQL example from the cases.\n",
        f"Question: {question}\n",
        "Retrieved cases:",
    ]
    for case in cases:
        lines.append(
            f"\nCase {case['id']}: {case['title']}\n"
            f"Question: {case['question']}\n"
            f"Answer SQL: {case['answer_sql']}"
        )
    return "\n".join(lines)


def explain_with_llm(question: str, cases: list) -> str:
    """Ask OpenAI's gpt-4o-mini to explain the retrieved cases."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "OPENAI_API_KEY is not set. Create a .env file in the repo "
                "root with one line: OPENAI_API_KEY=[YOUR_REAL_KEY_HERE] "
                "(replace with your real key). Never commit .env."
            ),
        )
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly SQL tutor for beginners. "
                        "Explain using only the cases given to you."
                    ),
                },
                {"role": "user", "content": build_prompt(question, cases)},
            ],
        )
    except Exception as error:
        # 401 bad key, 429 no credits, network trouble: report it
        # as a 502 so the chat box can show OpenAI's own message.
        raise HTTPException(status_code=502, detail=f"OpenAI call failed: {error}")
    return response.choices[0].message.content


class CheckRequest(BaseModel):
    sql: str


class AskRequest(BaseModel):
    question: str


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


@app.post("/ask")
def ask_question(body: AskRequest):
    """Full RAG answer: retrieve the top 3 cases, then explain them."""
    cases = search_cases(body.question)
    if not cases:
        raise HTTPException(
            status_code=503, detail="No cases retrieved. Check that chroma_db/ is built."
        )
    explanation = explain_with_llm(body.question, cases)
    return {
        "question": body.question,
        "cases": cases,
        "explanation": explanation,
    }
