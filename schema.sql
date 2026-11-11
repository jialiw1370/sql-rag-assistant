-- Day 2 (Tue 11/10): schema.sql — Put the first 3 cases from the book into SQLite
-- Usage (in the sql-rag-assistant repo root):
--   sqlite3 sql_rag.db < schema.sql
-- Note: *.db is already in the Day 1 .gitignore, so it will not be pushed to GitHub.
-- Verify when done (Day 2 "done" criteria: Python can connect to the database and query these 3 cases):
--   python3 -c "import sqlite3; c=sqlite3.connect('sql_rag.db'); print(c.execute('SELECT id, title FROM cases').fetchall())"
-- Commit message: create cases table with first 3 SQL cases
--
-- Source: "SQL Detective Cases: A Beginner's Guide to SQL for Kids" (2026)
-- Cases 1-3 copied verbatim. The question and answer SQL for each case are
-- from that case's "Today's Challenge" section in the book.

CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    question TEXT NOT NULL,
    answer_sql TEXT NOT NULL
);

-- Case 1: Help the Supermarket Owner with SELECT and FROM
INSERT INTO cases (id, title, question, answer_sql) VALUES
(1, 'Help the Supermarket Owner with SELECT and FROM', 'Uncle Leon wants to know the names of all the customers who shopped at the supermarket.', 'SELECT Name FROM Customers;');

-- Case 2: Use LIMIT to Show Only Some Customers
INSERT INTO cases (id, title, question, answer_sql) VALUES
(2, 'Use LIMIT to Show Only Some Customers', 'Uncle Leon wants to see up to 100 products that customers bought.', 'SELECT Merchandise FROM Clients LIMIT 100;');

-- Case 3: Use WHERE to Find Exactly What You Want
INSERT INTO cases (id, title, question, answer_sql) VALUES
(3, 'Use WHERE to Find Exactly What You Want', 'Find Leo''s specialty.', 'SELECT Specialty FROM Trainers WHERE Name = ''Leo'';');
