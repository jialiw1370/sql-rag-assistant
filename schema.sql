-- Day 6 (Sat 11/14): schema.sql — Put the first 8 cases from the book into SQLite
-- This file REPLACES the Day 2 schema.sql in the repo root (same filename,
-- new version with 8 cases instead of 3). Copy only this file to the
-- sql-rag-assistant folder, next to main.py. Do not push the day-6-en
-- folder itself.
--
-- After replacing it, rebuild the database locally (the old sql_rag.db
-- still has only 3 cases, so delete it first, then rebuild):
--   del sql_rag.db
--   py build_db.py
-- Or with the sqlite3 tool, if you have it:
--   sqlite3 sql_rag.db < schema.sql
-- Note: *.db is already in the Day 1 .gitignore, so it will not be pushed.
-- Verify: python -c "import sqlite3; print(sqlite3.connect('sql_rag.db').execute('SELECT count(*) FROM cases').fetchone())"
--   should print (8,)
-- Commit message: add 5 more cases and first pytest
--
-- Source: "SQL Detective Cases: A Beginner's Guide to SQL for Kids" (2026)
-- Cases 1-8 copied verbatim. The question and answer SQL for each case are
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

-- Case 4: Use ORDER BY to Sort Data
INSERT INTO cases (id, title, question, answer_sql) VALUES
(4, 'Use ORDER BY to Sort Data', 'Show the class names and sort them in reverse alphabetical order (Z to A).', 'SELECT Class FROM Classes ORDER BY Class DESC;');

-- Case 5: Use DISTINCT to Remove Duplicates
INSERT INTO cases (id, title, question, answer_sql) VALUES
(5, 'Use DISTINCT to Remove Duplicates', 'Show the trainer names only once, then sort them from A to Z.', 'SELECT DISTINCT Name FROM Trainers ORDER BY Name;');

-- Case 6: Use COUNT to Count Items
INSERT INTO cases (id, title, question, answer_sql) VALUES
(6, 'Use COUNT to Count Items', 'Use the Quantity column to count how many items are on the shopping list.', 'SELECT COUNT(Quantity) FROM ShoppingList;');

-- Case 7: Use SUM to Add Numbers Together
INSERT INTO cases (id, title, question, answer_sql) VALUES
(7, 'Use SUM to Add Numbers Together', 'Add up all the dollars in the saving table.', 'SELECT SUM(Dollars) FROM Saving;');

-- Case 8: Use AVG to Find the Average
INSERT INTO cases (id, title, question, answer_sql) VALUES
(8, 'Use AVG to Find the Average', 'Find the average math score.', 'SELECT AVG(Math_score) FROM Students;');
