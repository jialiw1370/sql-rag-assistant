# SQL RAG Assistant

Turn *SQL Detective Cases: A Beginner's Guide to SQL for Kids* (2026, 18 original cases)
into a RAG learning assistant you can ask questions to and practice with online.

When a user asks a SQL question (for example, "How do I write a JOIN?"), first retrieve the
2–3 most relevant cases from the 18, then use an LLM to generate an explanation and SQL
examples based on those cases.

## Current status

Day 1: Project scaffold only. No endpoints or pages yet.

- [ ] Day 2: `schema.sql` + first 3 cases into SQLite
- [ ] Day 3: FastAPI `GET /` and `GET /cases`
- [ ] Day 4: `GET /cases/{id}` + simplest SQL checker
- [ ] Day 5: Simplest HTML page
- [ ] Day 6: Grow cases to 8 + first pytest
- [ ] Day 7: README explains how to run it

Later (Weeks 5–10): Build the 18 cases into a knowledge base (Chroma vector database),
connect an LLM for RAG answers, and add manual evaluation on 10 test questions, written
into the README.

## How to run

Day 1 does not run yet. From Day 3:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/cases in your browser.

## Tech stack (planned)

- Python + FastAPI + SQLite
- RAG: Chroma + LLM API (from Week 5)
- Testing: pytest
- Frontend: HTML (currently learning)

