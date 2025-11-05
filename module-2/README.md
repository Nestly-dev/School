## Module 2: Subqueries & Advanced Joins (The "Complex Questions")

**Client Request:** "We need to dig deeper into our data. I want to know which workers have a specific skill, and I want to find our 'all-star' projects—the ones with the most workers assigned."

### Part 2A: Guided Activity (Subqueries in WHERE and FROM)

**Concept:** A Subquery is a SELECT statement nested inside another statement. It's incredibly powerful for answering multi-part questions.

**Guide:** Let's find all workers who have the skill 'Heavy Equipment Operation' (or another skill from your skills table).

**Multi-Step Logic:**
1. First, we need the `skill_id` for 'Heavy Equipment Operation'.
2. Then, we need all `worker_ids` from `worker_skills` that have that `skill_id`.
3. Finally, we need the worker details from the `workers` table.

**Implementation:** We can combine this with subqueries. (Assuming your tables are named `workers`, `worker_skills`, and `skills` as per the ERD).

```sql
-- Using a subquery in the WHERE clause
SELECT first_name, last_name, phone
FROM workers
WHERE worker_id IN (
    SELECT worker_id
    FROM worker_skills
    WHERE skill_id = (
        SELECT skill_id FROM skills WHERE skill_name = 'Heavy Equipment Operation'
    )
);

-- This can also be done with JOINs, which is often more performant
SELECT w.first_name, w.last_name, w.phone
FROM workers w
JOIN worker_skills ws ON w.worker_id = ws.worker_id
JOIN skills s ON ws.skill_id = s.skill_id
WHERE s.skill_name = 'Heavy Equipment Operation';
```

**Task:** Add both of these query variations to your `02_subqueries.sql` file.

### Part 2B: Challenge Task (Subquery with Aggregation)

The client wants to find the project(s) with the highest number of assigned workers. This is a common "max of a count" problem.

**Task:** Write a single SQL query to find the `project_name` and the `worker_count` for the project(s) with the most workers. (Hint: This often involves a subquery in the FROM or HAVING clause. You'll need to join `projects` and `project_assignments`).

**Deliverable:** Add this complex query to your `02_subqueries.sql` file.

---