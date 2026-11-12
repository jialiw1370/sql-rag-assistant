# Day 6 (Sat 11/14): test_main.py — first pytest for the SQL RAG Assistant
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-6-en folder itself.
#
# Before running it, rebuild the database with the Day 6 schema.sql
# (8 cases, not 3): delete the old sql_rag.db, then run py build_db.py.
#
# Install the test tools first (Windows: use py, not python):
#   py -m pip install pytest httpx
# Run:
#   py -m pytest
# Done when pytest shows 1 passed.
# Commit message: add 5 more cases and first pytest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_cases():
    response = client.get("/cases")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 8
    assert cases[0]["id"] == 1
    assert cases[7]["id"] == 8
