# Day 16: explain.py — first LLM call (SQL RAG Assistant, OpenAI version)
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-16-en folder itself.
#
# This is the GENERATION half of RAG. It takes a question, retrieves
# the top 3 cases with vectors (same as Day 14), then asks OpenAI's
# gpt-4o-mini to explain them in simple words for a beginner.
# The model only ever sees YOUR book's cases — it explains those,
# it does not invent new SQL.
#
# Setup (Windows: use py, not python):
#   1. Get an API key at https://platform.openai.com/api-keys
#      (sign in, "Create new secret key"). Add a small amount of
#      credit under Billing first — the key itself is free, you pay
#      only per use, and gpt-4o-mini costs a fraction of a cent
#      per explanation here.
#   2. Create a file called .env in the repo root with one line:
#        OPENAI_API_KEY=sk-your-key-here
#      .env is already in .gitignore — NEVER commit it, and never
#      paste your key into chat or into any .py file.
#   3. py -m pip install -r requirements.txt
#
# Run:
#   py explain.py "How do I write a JOIN?"
# Done when it prints a short explanation that names the retrieved
# cases (17 and 18 for the JOIN question).
# Commit message: add first LLM explanation call

import os
import sqlite3
import sys
from pathlib import Path

import chromadb

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; the key must be set in the terminal

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sql_rag.db"
CHROMA_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "sql_cases"
MODEL = "gpt-4o-mini"


def get_case(case_id: int):
    """Read one case by id from SQLite, or None if it does not exist."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            "SELECT id, title, question, answer_sql FROM cases WHERE id = ?",
            (case_id,),
        ).fetchone()
        return dict(row) if row is not None else None
    finally:
        connection.close()


def retrieve_cases(question: str, top_n: int = 3):
    """Vector-search Chroma, then load the full cases from SQLite."""
    if not CHROMA_PATH.exists():
        raise SystemExit(
            "chroma_db/ not found. Run Day 13 first: py embed_cases.py"
        )
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        raise SystemExit(
            f"Collection '{COLLECTION_NAME}' not found in chroma_db/. "
            "Re-run: py embed_cases.py"
        )
    results = collection.query(query_texts=[question], n_results=top_n)
    cases = []
    for case_id in results["ids"][0]:
        case = get_case(int(case_id))
        if case is not None:
            cases.append(case)
    return cases


def build_prompt(question: str, cases: list) -> str:
    """Put the question and the retrieved cases into one prompt."""
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


def explain(question: str) -> str:
    """Retrieve the top 3 cases, then ask OpenAI to explain them."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is not set.\n"
            "Create a .env file in the repo root with one line:\n"
            "  OPENAI_API_KEY=sk-your-key-here\n"
            "Then run py explain.py again. Never commit .env."
        )
    from openai import OpenAI

    cases = retrieve_cases(question)
    if not cases:
        raise SystemExit("No cases retrieved. Check that chroma_db/ is built.")
    print("Retrieved cases:", ", ".join(f"Case {c['id']}" for c in cases), "\n")

    client = OpenAI(api_key=api_key)
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
    return response.choices[0].message.content


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "How do I write a JOIN?"
    print(f"Question: {question}\n")
    print(explain(question))


if __name__ == "__main__":
    main()
