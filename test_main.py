# Day 10: test_main.py — expanded tests for all 18 cases
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-10-en folder itself.
#
# Run this ONLY after Day 9 is done: the database must have all 18
# cases (rebuild it with the Day 9 schema.sql first:
#   del sql_rag.db
#   py build_db.py
# You should see 18 cases printed).
#
# Install the test tools first (Windows: use py, not python):
#   py -m pip install pytest httpx
# Run:
#   py -m pytest
# Done when pytest shows all tests passed (4 passed).
# Commit message: expand tests to 18 cases

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
