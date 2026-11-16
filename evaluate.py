# Day 20: evaluate.py — score keyword vs vector retrieval on 10 questions
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-20-en folder itself.
#
# This is the tiny evaluation Week 4 promised: 10 sample questions,
# each with the one case a beginner should get. It runs BOTH retrieval
# methods on every question — Day 11 keyword matching (retrieve.py)
# and Day 14 vector search (vector_retrieve.py) — and prints how often
# the expected case is ranked #1 and how often it is in the top 3.
#
# The questions are a mix: some use the case's own words (both methods
# should do well), some are paraphrases with different words (this is
# where keyword matching is expected to struggle). The numbers are the
# honest result of running it — whichever method wins, that is what
# you report in interviews. Do not tune the questions to make one side
# look better after seeing the scores.
#
# Prerequisite: sql_rag.db built (Day 9 schema.sql + py build_db.py)
# and chroma_db/ built (Day 13: py embed_cases.py). No API key needed,
# no LLM call — this only tests retrieval.
#
# Run (Windows: use py, not python):
#   py evaluate.py
# Done when it prints the per-question table and the summary line
# (top-1 and top-3 counts out of 10, for both methods).
# Commit message: add retrieval evaluation over 10 questions

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# (question, expected case id). The expected case is the one case
# whose title + question + answer SQL actually answers the question.
QUESTIONS = [
    ("How do I write a JOIN?", 17),
    ("How can I combine data from two tables?", 17),
    ("How do I find the average math score?", 8),
    ("How do I show only the first 100 results?", 2),
    ("How do I count how many items there are?", 6),
    ("How do I find the biggest class?", 9),
    ("How do I get each group's total separately?", 15),
    ("How do I keep only groups with a high average?", 16),
    ("How do I match rows that meet either of two conditions?", 11),
    ("How do I keep all movies even if they have no actors?", 18),
]


def main():
    if not (BASE_DIR / "sql_rag.db").exists():
        raise SystemExit(
            "sql_rag.db not found. Build it first: py build_db.py"
        )
    if not (BASE_DIR / "chroma_db").exists():
        raise SystemExit(
            "chroma_db/ not found. Run Day 13 first: py embed_cases.py"
        )

    from retrieve import retrieve as keyword_retrieve
    from vector_retrieve import retrieve as vector_retrieve

    keyword_top1 = 0
    keyword_top3 = 0
    vector_top1 = 0
    vector_top3 = 0

    print(f"{'Question':<55}{'Expected':<10}{'Keyword':<16}{'Vector':<16}")
    print("-" * 97)
    for question, expected in QUESTIONS:
        keyword_ids = [case["id"] for _, case in keyword_retrieve(question)]
        vector_ids = [hit["id"] for hit in vector_retrieve(question)]

        if keyword_ids[0] == expected:
            keyword_top1 += 1
        if expected in keyword_ids:
            keyword_top3 += 1
        if vector_ids[0] == expected:
            vector_top1 += 1
        if expected in vector_ids:
            vector_top3 += 1

        print(
            f"{question:<55}{expected:<10}"
            f"{str(keyword_ids):<16}{str(vector_ids):<16}"
        )

    print("-" * 97)
    total = len(QUESTIONS)
    print(f"Keyword retrieval: top-1 {keyword_top1}/{total}, top-3 {keyword_top3}/{total}")
    print(f"Vector retrieval:   top-1 {vector_top1}/{total}, top-3 {vector_top3}/{total}")


if __name__ == "__main__":
    main()
