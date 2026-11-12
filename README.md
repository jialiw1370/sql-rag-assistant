# SQL RAG Assistant

Turn *SQL Detective Cases: A Beginner's Guide to SQL for Kids* (2026, 18 original cases)
into a RAG learning assistant you can ask questions to and practice with online.

When a user asks a SQL question (for example, "How do I write a JOIN?"), first retrieve the
2–3 most relevant cases from the 18, then use an LLM to generate an explanation and SQL
examples based on those cases.

## Current status

Week 1 is done — a working API, checker, HTML page, and first test, with 8 cases.

- [x] Day 1: Project scaffold — README, requirements, .gitignore
- [x] Day 2: `schema.sql` + first 3 cases into SQLite
- [x] Day 3: FastAPI `GET /` and `GET /cases`
- [x] Day 4: `GET /cases/{id}` + simplest SQL checker
- [x] Day 5: Simplest HTML page
- [x] Day 6: Grow cases to 8 + first pytest
- [x] Day 7: README explains how to run it

The 8 cases in the database so far, copied verbatim from the book's
"Today's Challenge" sections:

1. Help the Supermarket Owner with SELECT and FROM
2. Use LIMIT to Show Only Some Customers
3. Use WHERE to Find Exactly What You Want
4. Use ORDER BY to Sort Data
5. Use DISTINCT to Remove Duplicates
6. Use COUNT to Count Items
7. Use SUM to Add Numbers Together
8. Use AVG to Find the Average

Later (Weeks 5–10): Build the 18 cases into a knowledge base (Chroma vector database),
connect an LLM for RAG answers, and add manual evaluation on 10 test questions, written
into the README.

## Setup

```bash
py -m pip install -r requirements.txt
py -m pip install pytest httpx
```

On Windows, use `py` (the Python launcher). Plain `python` may open the
Microsoft Store instead of running Python.

Build the database (only needed once, or after `schema.sql` changes):

```bash
py build_db.py
```

This reads `schema.sql` and creates `sql_rag.db` in the repo root.
`build_db.py` is a local helper only — do not commit it.
`sql_rag.db` is ignored by `.gitignore` (the `*.db` line).

## How to run

```bash
py -m uvicorn main:app --reload
```

Leave that terminal running while you test. Press `CTRL+C` to stop it.

Then open in your browser:

- http://127.0.0.1:8000/page — the HTML page: pick a case, write SQL, check it
- http://127.0.0.1:8000/cases — all 8 cases as JSON
- http://127.0.0.1:8000/cases/1 — Case 1 as JSON
- http://127.0.0.1:8000/docs — try the API here, including
  `POST /cases/{id}/check` (a browser address bar can only do GET)

Example check — send `{"sql": "SELECT Name FROM Customers;"}` to
`POST /cases/1/check` and you get back `{"case_id": 1, "correct": true,
"message": "Correct!"}`.

## How to test

```bash
py -m pytest
```

Done when pytest shows `1 passed`. The test checks that `GET /cases`
returns 8 cases.

## Tech stack

- Python + FastAPI + SQLite
- RAG: Chroma + LLM API (from Week 5)
- Testing: pytest
- Frontend: HTML (currently learning)
