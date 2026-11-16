# SQL RAG Assistant

Turn *SQL Detective Cases: A Beginner's Guide to SQL for Kids* (2026, 18 original cases)
into a RAG learning assistant you can ask questions to and practice with online.

When a user asks a SQL question (for example, "How do I write a JOIN?"), first retrieve the
3 most relevant cases from the 18 by vector similarity, then use an LLM to generate an
explanation in simple words, based only on those retrieved cases.

## Current status

Week 1 is done — a working API, checker, HTML page, and first test, with 8 cases.
Week 2 is done — all 18 cases in the database, 4 tests, and the first retrieval step.
Week 3 is done — vector retrieval replaces keyword matching, `/search` exposes it in
the API, and the first LLM call explains the retrieved cases. 6 tests pass.

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
- [x] Day 13: Embed all 18 cases in Chroma (vector search)
- [x] Day 14: Vector retrieval (`vector_retrieve.py`) over the cases
- [x] Day 15: `GET /search?q=...` endpoint in the API
- [x] Day 16: First LLM call (`explain.py`, OpenAI `gpt-4o-mini`)
- [x] Day 17: README explains Week 3 + 2 tests for `/search` (6 tests total)

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

## How the RAG part works

The full flow is: question → vector retrieval → LLM explanation.

1. **Retrieval (vectors):** each case (title + question + answer SQL) was embedded
   into Chroma on Day 13. A question is embedded the same way, and Chroma returns
   the 3 closest cases by meaning — `vector_retrieve.py` (Day 14) and
   `GET /search?q=...` (Day 15) both do this.
2. **Generation (LLM):** `explain.py` (Day 16) takes the top 3 retrieved cases and
   asks OpenAI's `gpt-4o-mini` to explain them in short, simple words for a beginner,
   naming the case numbers it uses. The model only ever sees your book's cases —
   it explains those, it does not invent new SQL.

For "How do I write a JOIN?", retrieval returns Cases 17, 18, and 1, and the
explanation names Cases 17 and 18.

### Keyword vs vector — what actually changed

Keyword matching (Day 11, `retrieve.py`) scores each case by the question's exact
words — a keyword in the title is worth 2 points, in the question or answer SQL
worth 1 point. It works when the question uses the same words as the case: for
"How do I write a JOIN?" it returns Cases 17 and 18. But it misses differently
worded questions: "How can I combine data from two tables?" contains no word
"join", so keyword matching finds nothing useful. Vector search (Day 14) returns
Cases 17 and 18 first for that same paraphrased question, and Case 8 first for
"How do I find the average math score?". That is the whole point of Week 3:
matching by meaning, not by shared words.

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

Build the vector store (only needed once, or after the cases change):

```bash
py embed_cases.py
```

This embeds all 18 cases into `chroma_db/` in the repo root.
`chroma_db/` is local data — it is in `.gitignore`, do not commit it.

## How to run

```bash
py -m uvicorn main:app --reload
```

Leave that terminal running while you test. Press `CTRL+C` to stop it.

Then open in your browser:

- http://127.0.0.1:8000/page — the HTML page: pick a case, write SQL, check it
- http://127.0.0.1:8000/cases — all 18 cases as JSON
- http://127.0.0.1:8000/cases/1 — Case 1 as JSON
- http://127.0.0.1:8000/search?q=How%20do%20I%20write%20a%20JOIN%3F — top 3 vector matches as JSON
- http://127.0.0.1:8000/docs — try the API here, including
  `POST /cases/{id}/check` (a browser address bar can only do GET)

Example check — send `{"sql": "SELECT Name FROM Customers;"}` to
`POST /cases/1/check` and you get back `{"case_id": 1, "correct": true,
"message": "Correct!"}`.

If `chroma_db/` is missing, `/search` returns 503 with a message to run
Day 13 first — `/cases` keeps working either way.

## Retrieval (no server needed)

```bash
py retrieve.py
py retrieve.py "How do I find the average math score?"
py vector_retrieve.py "How can I combine data from two tables?"
```

`retrieve.py` prints the top 3 cases by keyword matching;
`vector_retrieve.py` prints the top 3 by vector similarity.

## First LLM call (no server needed)

`explain.py` needs an OpenAI API key. The key itself is free to create;
the API is pay-as-you-go, and each explanation with `gpt-4o-mini` costs
a fraction of a cent. Add a small amount of credit first (minimum $5)
under Billing at https://platform.openai.com/settings/organization/billing
— with $0 balance the call fails with "You have no credits remaining."

1. Create a key at https://platform.openai.com/api-keys
2. Create a file called `.env` in the repo root with one line:
   `OPENAI_API_KEY=sk-your-key-here` (your real key, no quotes, no spaces
   around `=`). `.env` is already in `.gitignore` — never commit it, and
   never paste the key into chat or into any `.py` file.
3. Run it:

```bash
py explain.py "How do I write a JOIN?"
```

Done when it prints a short explanation that names Cases 17 and 18.

## How to test

```bash
py -m pytest
```

Done when pytest shows `6 passed`. The tests check that `GET /cases`
returns 18 cases, `GET /cases/18` returns the LEFT JOIN case, a correct
SQL check returns `correct: true`, a wrong SQL check returns
`correct: false` with the expected answer, `GET /search?q=How do I write
a JOIN?` returns 200 with Cases 17, 18, and 1, and the paraphrased
question "How can I combine data from two tables?" still returns 3 cases
including 17 and 18.

## Tech stack

- Python + FastAPI + SQLite
- RAG: Chroma vector retrieval + OpenAI `gpt-4o-mini` for explanations
  (keyword retrieval in `retrieve.py` is kept for comparison)
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
