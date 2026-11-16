# Day 21: test_main.py — 8 tests, including 2 new ones for /ask
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-21-en folder itself.
#
# Prerequisite: Day 13 must have run once so ./chroma_db exists,
# and sql_rag.db must have all 18 cases (Day 9 schema.sql +
# py build_db.py). If chroma_db/ is missing, the /search and /ask
# tests fail with 503 — that is the app telling you to run
# Day 13 first (py embed_cases.py), not a broken test.
#
# The 2 new /ask tests do NOT call the real OpenAI API: they replace
# the OpenAI client with a fake one that returns a fixed explanation,
# so pytest costs nothing and needs no API key. The no-key test checks
# that /ask answers 503 with the .env instructions when no key is set.
#
# Run (Windows: use py, not python):
#   py -m pytest
# Done when pytest shows all tests passed (8 passed).
# Commit message: update README for week 4

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


class _FakeMessage:
    content = (
        "Case 17 shows a JOIN: SELECT ... FROM Clubs "
        "JOIN ClubTeachers ON Clubs.Club = ClubTeachers.Club;"
    )


class _FakeChoice:
    message = _FakeMessage()


class _FakeResponse:
    choices = [_FakeChoice()]


class _FakeCompletions:
    def create(self, model, messages):
        return _FakeResponse()


class _FakeChat:
    completions = _FakeCompletions()


class _FakeOpenAI:
    def __init__(self, api_key=None):
        self.chat = _FakeChat()


def test_ask_returns_explanation(monkeypatch):
    # Fake the OpenAI client so this test costs nothing and needs
    # no real key. main.py imports OpenAI inside the function, so
    # patching openai.OpenAI is enough.
    monkeypatch.setattr("openai.OpenAI", _FakeOpenAI)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key")
    response = client.post("/ask", json={"question": "How do I write a JOIN?"})
    assert response.status_code == 200
    body = response.json()
    assert body["question"] == "How do I write a JOIN?"
    assert [case["id"] for case in body["cases"]] == [17, 18, 1]
    assert "Case 17" in body["explanation"]


def test_ask_without_key_returns_503(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/ask", json={"question": "How do I write a JOIN?"})
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
