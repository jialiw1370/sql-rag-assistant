# Day 13: embed_cases.py — embed all 18 cases into Chroma
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-13-en folder itself.
#
# This replaces Day 11's keyword matching with vectors (the retrieval
# half of RAG). Each case becomes one document:
#   title + question + answer SQL
# Chroma's default embedding model turns that document into a vector
# of numbers, so later a question can be matched by MEANING, not just
# by exact words (e.g. "combine two tables" can find the JOIN cases).
#
# First run downloads the small embedding model (a few minutes, one
# time). The vector store is saved in ./chroma_db next to this file —
# that folder is local data, add "chroma_db/" to .gitignore and do
# not commit it.
#
# Setup (Windows: use py, not python):
#   py -m pip install chromadb
# Run:
#   py embed_cases.py
# Done when it prints "Embedded 18 cases" and the test query at the
# bottom returns the JOIN cases for "How do I write a JOIN?".
# Commit message: add Chroma embeddings for cases
# (commit embed_cases.py and the .gitignore line, NOT chroma_db/)

import sqlite3
from pathlib import Path

import chromadb

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sql_rag.db"
CHROMA_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "sql_cases"


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


def case_document(case: dict) -> str:
    return (
        f"Title: {case['title']}\n"
        f"Question: {case['question']}\n"
        f"Answer SQL: {case['answer_sql']}"
    )


def main():
    cases = get_cases()
    if len(cases) != 18:
        print(f"Expected 18 cases in sql_rag.db, found {len(cases)}.")
        print("Rebuild the database first: del sql_rag.db, then py build_db.py")
        return

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    # Recreate the collection so re-runs never duplicate cases.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[str(case["id"]) for case in cases],
        documents=[case_document(case) for case in cases],
        metadatas=[{"title": case["title"]} for case in cases],
    )
    print(f"Embedded {collection.count()} cases into Chroma ({CHROMA_PATH})")

    # Small built-in check: the same question Day 11 used.
    results = collection.query(
        query_texts=["How do I write a JOIN?"], n_results=3
    )
    print("\nTest query: How do I write a JOIN?")
    for case_id, title, distance in zip(
        results["ids"][0],
        [m["title"] for m in results["metadatas"][0]],
        results["distances"][0],
    ):
        print(f"  Case {case_id}: {title} (distance: {distance:.3f})")
    print("\nDone. Cases 17 and 18 should be in the top 2.")


if __name__ == "__main__":
    main()
