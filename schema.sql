-- Day 8: schema.sql — Add Cases 9-13 from the book (13 cases total)
-- This file REPLACES the Day 6 schema.sql in the repo root.
-- After replacing it, rebuild the database locally:
--   del sql_rag.db
--   py build_db.py
-- Verify count should be (13,)
-- Commit message: add cases 9 to 13
--
-- Source: "SQL Detective Cases" (2026), Cases 9-13 verbatim from
-- each case's "Today's Challenge" section.
-- NOTE Case 13 uses ILIKE, which SQLite does not support for real
-- execution. The current checker compares answer text, so it is
-- fine for now; flag it when the checker starts executing SQL.

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

-- Case 9: Use MIN and MAX to Find the Smallest and Largest Values
INSERT INTO cases (id, title, question, answer_sql) VALUES
(9, 'Use MIN and MAX to Find the Smallest and Largest Values', 'Find the largest class size.', 'SELECT MAX(Number_of_people) FROM Enrollment;');

-- Case 10: Use AND to Find Data That Matches Two Conditions
INSERT INTO cases (id, title, question, answer_sql) VALUES
(10, 'Use AND to Find Data That Matches Two Conditions', 'Find the book that is published in 1952 and is in English.', 'SELECT Title FROM Books WHERE Published_year = 1952 AND Language = ''English'';');

-- Case 11: Use OR to Match Either Condition
INSERT INTO cases (id, title, question, answer_sql) VALUES
(11, 'Use OR to Match Either Condition', 'Find books that are Chinese or available.', 'SELECT Title FROM Books WHERE Language = ''Chinese'' OR Available = ''Yes'';');

-- Case 12: Use IN to Match One Value from a List
INSERT INTO cases (id, title, question, answer_sql) VALUES
(12, 'Use IN to Match One Value from a List', 'Find pets that are 2 or 4 years old.', 'SELECT * FROM Pets WHERE Age IN (2, 4);');

-- Case 13: Use LIKE to Find Keywords
INSERT INTO cases (id, title, question, answer_sql) VALUES
(13, 'Use LIKE to Find Keywords', 'Find toys that start with H, ignoring uppercase and lowercase letters.', 'SELECT * FROM Toys WHERE ToyName ILIKE ''h%'';');
