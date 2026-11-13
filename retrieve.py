# Day 11: retrieve.py — first RAG step: keyword retrieval over the 18 cases
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-11-en folder itself.
#
# This is retrieval BEFORE vectors, and before any LLM. It reads all 18
# cases from sql_rag.db and prints the 3 most relevant cases for a
# question, by simple keyword matching. Week 3 will replace this
# keyword matching with embeddings (Chroma) and add an LLM call — this
# script is the skeleton that step will replace.
#
# How the score works (simplest version):
#   - Split the question into lowercase words, drop common stopwords
#     (how, do, i, a, the, ...) so only the real keywords count.
#   - A keyword in a case's title is worth 2 points, in its question
#     or answer SQL worth 1 point.
#   - Sort by score (highest first), ties broken by case id.
#
# Honest limit: keyword matching only sees exact words. For the sample
# question "How do I write a JOIN?", only "join" matches anything, so
# the top 2 are the JOIN cases and the 3rd has score 0. That is exactly
# why vectors come next — they can match meaning, not just words.
#
# Run (Windows: use py, not python):
#   py retrieve.py
#   py retrieve.py "How do I find the average math score?"
# Done when it prints the top 3 cases for the sample question.
# Commit message: add keyword retrieval over cases

import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "sql_rag.db"

STOPWORDS = {
    "how", "do", "does", "did", "i", "a", "an", "the", "to", "of", "in",
    "on", "for", "and", "or", "is", "are", "was", "were", "what", "which",
    "can", "you", "me", "my", "it", "with", "by", "from",
}


def keywords(text: str) -> set:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS}


def get_cases():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT id, title, question, answer_sql FROM cases ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def score_case(case: dict, words: set) -> int:
    title_words = set(re.findall(r"[a-z0-9]+", case["title"].lower()))
    body_words = set(
        re.findall(r"[a-z0-9]+", (case["question"] + " " + case["answer_sql"]).lower())
    )
    score = 0
    for word in words:
        if word in title_words:
            score += 2
        if word in body_words:
            score += 1
    return score


def retrieve(question: str, top_n: int = 3):
    words = keywords(question)
    scored = [(score_case(case, words), case) for case in get_cases()]
    scored.sort(key=lambda item: (-item[0], item[1]["id"]))
    return scored[:top_n]


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "How do I write a JOIN?"
    print(f"Question: {question}\n")
    print("Top 3 most relevant cases (keyword matching):\n")
    for score, case in retrieve(question):
        print(f"{case['id']}. {case['title']} (score: {score})")
        print(f"   {case['question']}")
        print(f"   {case['answer_sql']}\n")


if __name__ == "__main__":
    main()
