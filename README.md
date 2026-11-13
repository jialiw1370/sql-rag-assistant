# SQL RAG Assistant

Turn *SQL Detective Cases: A Beginner's Guide to SQL for Kids* (2026, 18 original cases)
into a RAG learning assistant you can ask questions to and practice with online.

When a user asks a SQL question (for example, "How do I write a JOIN?"), first retrieve the
2–3 most relevant cases from the 18, then use an LLM to generate an explanation and SQL
examples based on those cases.

## Current status

Week 1 is done — a working API, checker, HTML page, and first test, with 8 cases.
Week 2 is done — all 18 cases in the database, 4 tests, and the first retrieval step.

- [x] Day 1: Project scaffold — README, requirements, .gitignore
- [x] Day 2: `schema.sql` + first 3 cases into SQLite
- [x] Day 3: FastAPI `GET /` and `GET /cases`
- [x] Day 4: `GET /cases/{id}` + simplest SQL checker
- [x] Day 5: Simplest HTML page
- [x] Day 6: Grow cases to 8 + first pytest
- [x] Day 7: README explains how to run it
- [x] Day 8: Add Cases 9–13 (MIN/MAX, AND, OR, IN, LIKE)
- [x] Day 9: Add Cases 14–18 (BETWEEN, GROUP BY, HAVING, JOIN, LEFT JOIN)
- [x] Day 10: Expand tests to 18 cases (4 tests)
- [x] Day 11: First keyword retrieval over the cases
- [x] Day 12: README explains Week 2

All 18 cases in the database, copied verbatim from the book's
"Today's Challenge" sections:

1. Help the Supermarket Owner with SELECT and FROM
2. Use LIMIT to Show Only Some Customers
3. Use WHERE to Find Exactly What You Want
4. Use ORDER BY to Sort Data
5. Use DISTINCT to Remove Duplicates
6. Use COUNT to Count Items
7. Use SUM to Add Numbers Together
8. Use AVG to Find the Average
9. Use MIN and MAX to Find the Smallest and Largest Values
10. Use AND to Find Data That Matches Two Conditions
11. Use OR to Match Either Condition
12. Use IN to Match One Value from a List
13. Use LIKE to Find Keywords
14. Use BETWEEN to Find Values in a Range
15. The Magic of GROUP BY
16. Use HAVING to Filter Groups
17. Use JOIN to Match Tables
18. Use LEFT JOIN to Match Tables

## How the RAG part will work

Today, retrieval is keyword matching (`retrieve.py`): it scores each case
by the question's keywords — a keyword in the title is worth 2 points,
in the question or answer SQL worth 1 point — and prints the top 3 cases.
For "How do I write a JOIN?", it returns Cases 17 and 18.

Keyword matching only sees exact words, so it misses questions phrased
differently. Week 3 replaces it with embeddings: embed each case
(title + question + answer SQL) into Chroma, retrieve by vector
similarity, then add the first LLM call to explain the retrieved cases.

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
- http://127.0.0.1:8000/cases — all 18 cases as JSON
- http://127.0.0.1:8000/cases/1 — Case 1 as JSON
- http://127.0.0.1:8000/docs — try the API here, including
  `POST /cases/{id}/check` (a browser address bar can only do GET)

Example check — send `{"sql": "SELECT Name FROM Customers;"}` to
`POST /cases/1/check` and you get back `{"case_id": 1, "correct": true,
"message": "Correct!"}`.

## Retrieval (no server needed)

```bash
py retrieve.py
py retrieve.py "How do I find the average math score?"
```

Prints the top 3 most relevant cases for the question, by keyword matching.

## How to test

```bash
py -m pytest
```

Done when pytest shows `4 passed`. The tests check that `GET /cases`
returns 18 cases, `GET /cases/18` returns the LEFT JOIN case, a correct
SQL check returns `correct: true`, and a wrong SQL check returns
`correct: false` with the expected answer.

## Tech stack

- Python + FastAPI + SQLite
- RAG: keyword retrieval now; Chroma + LLM API (from Week 3)
- Testing: pytest
- Frontend: HTML (currently learning)

## One thing to know

Case 13's answer uses `ILIKE`, which is PostgreSQL syntax — SQLite does
not support it. Right now the checker only compares the submitted text
with `answer_sql`, so Case 13 works fine. When the checker is upgraded to
actually execute SQL in SQLite, Case 13 will need a decision: rewrite it
as `LIKE` with a case-insensitive comparison, or accept that this one
case is text-checked only. Don't change it now, since the book's answer
is what the case teaches.
