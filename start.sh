#!/bin/bash
# Deploy start script for Render (SQL RAG Assistant)
# Copy this file to the sql-rag-assistant repo root, next to main.py.
# Do not push the deploy-en folder itself.
#
# Render runs this after `pip install -r requirements.txt`.
# It builds the two local data files the app needs — they are NOT in
# git (sql_rag.db and chroma_db/ are both gitignored), so a fresh
# server has to build them on first boot — then starts the API.
#
# Render sets the $PORT environment variable; the server must listen
# on 0.0.0.0:$PORT. On a free Render service the disk is wiped on
# each deploy, so this script rebuilds the data files whenever they
# are missing. First boot downloads the small embedding model (a few
# minutes, one time per deploy).

set -e
cd "$(dirname "$0")"

# 1. Build the SQLite database from schema.sql (only if missing).
if [ ! -f sql_rag.db ]; then
  echo "Building sql_rag.db from schema.sql..."
  python -c "import sqlite3; con = sqlite3.connect('sql_rag.db'); con.executescript(open('schema.sql', encoding='utf-8').read()); con.commit(); print('cases:', con.execute('SELECT COUNT(*) FROM cases').fetchone()[0]); con.close()"
fi

# 2. Build the Chroma vector store (only if missing).
if [ ! -d chroma_db ]; then
  echo "Embedding 18 cases into Chroma..."
  python embed_cases.py
fi

# 3. Start the API.
echo "Starting server on port ${PORT:-8000}..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
