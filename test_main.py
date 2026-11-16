# Day 17: test_main.py — 6 tests, including 2 new ones for /search
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-17-en folder itself.
#
# Prerequisite: Day 13 must have run once so ./chroma_db exists,
# and sql_rag.db must have all 18 cases (Day 9 schema.sql +
# py build_db.py). If chroma_db/ is missing, the 2 new /search
# tests fail with 503 — that is the app telling you to run
# Day 13 first (py embed_cases.py), not a broken test.
#
# Run (Windows: use py, not python):
#   py -m pytest
# Done when pytest shows all tests passed (6 passed).
# Commit message: update README for week 3

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_cases():
    response = client.get("/cases")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 18
    assert cases[0]["id"] == 1
    assert cases[17]["id"] == 18


def test_read_last_case():
    response = client.get("/cases/18")
    assert response.status_code == 200
    case = response.json()
    assert case["id"] == 18
    assert case["title"] == "Use LEFT JOIN to Match Tables"


def test_check_correct_sql():
    response = client.post(
        "/cases/1/check", json={"sql": "SELECT Name FROM Customers;"}
    )
    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_check_wrong_sql():
    response = client.post(
        "/cases/1/check", json={"sql": "SELECT * FROM Customers;"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is False
    assert "expected" in body


def test_search_returns_three_cases():
    response = client.get("/search", params={"q": "How do I write a JOIN?"})
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 3
    assert [case["id"] for case in cases] == [17, 18, 1]
    assert cases[0]["title"] == "Use JOIN to Match Tables"


def test_search_unknown_wording_returns_three():
    # No word "join" in this question — keyword matching (Day 11)
    # misses it, but vector search still finds the JOIN cases.
    response = client.get(
        "/search", params={"q": "How can I combine data from two tables?"}
    )
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 3
    ids = [case["id"] for case in cases]
    assert 17 in ids
    assert 18 in ids
