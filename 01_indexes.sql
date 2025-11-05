USE big3_construction;

-- Module 1: Indexes

-- Part 1A: Guided Activity
-- EXPLAIN before creating the index
EXPLAIN SELECT * FROM workers WHERE last_name = 'Johnson';

-- Create index to speed up lookups by last name
CREATE INDEX idx_worker_lastname ON workers(last_name);

-- EXPLAIN after creating the index
EXPLAIN SELECT * FROM workers WHERE last_name = 'Johnson';

-- Part 1B: Challenge Task
-- Composite index to optimize filtering by city and sorting by start date
CREATE INDEX idx_projects_city_date ON projects(site_city, start_date);
