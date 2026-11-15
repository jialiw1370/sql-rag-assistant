# Day 14: vector_retrieve.py — vector retrieval over the 18 cases (Chroma)
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the day-14-en folder itself.
#
# Same job as Day 11's retrieve.py, but the matching is by MEANING
# (vectors in Chroma) instead of keyword scoring. Run Day 13's
# embed_cases.py first so ./chroma_db exists.
#
# Run (Windows: use py, not python):
#   py vector_retrieve.py
#   py vector_retrieve.py "How do I find the average math score?"
#   py vector_retrieve.py "How can I combine data from two tables?"
# Done when the top 3 look sensible for all 3 questions, including
# the last one — keyword matching (Day 11) misses it, vectors don't.
# Commit message: add vector retrieval over cases

import sys
from pathlib import Path

import chromadb

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "sql_cases"


def retrieve(question: str, top_n: int = 3):
    if not CHROMA_PATH.exists():
        raise SystemExit(
            "chroma_db/ not found. Run Day 13 first: py embed_cases.py"
        )
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        raise SystemExit(
            f"Collection '{COLLECTION_NAME}' not found in chroma_db/. "
            "Re-run: py embed_cases.py"
        )
    results = collection.query(query_texts=[question], n_results=top_n)
    hits = []
    for case_id, metadata, document, distance in zip(
        results["ids"][0],
        results["metadatas"][0],
        results["documents"][0],
        results["distances"][0],
    ):
        hits.append(
            {
                "id": int(case_id),
                "title": metadata.get("title", ""),
                "document": document,
                "distance": distance,
            }
        )
    return hits


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "How do I write a JOIN?"
    print(f"Question: {question}\n")
    print("Top 3 most relevant cases (vector search):\n")
    for hit in retrieve(question):
        print(f"{hit['id']}. {hit['title']} (distance: {hit['distance']:.3f})")
        print(f"   {hit['document']}\n")


if __name__ == "__main__":
    main()
