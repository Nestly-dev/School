## Module 1: Indexes (The "Need for Speed")

**Client Request:** "Our project managers are complaining that the application is slow. Specifically, searching for a worker by their last name takes way too long, as does finding projects in a specific city. We need to speed this up!"

### Part 1A: Guided Activity (Creating a Simple Index)

**Concept:** An Index is a data structure (like an index in a book) that speeds up data retrieval on a table. It's essential for columns used frequently in WHERE clauses.

**Guide:** Let's analyze the "search by last name" problem.

1. **Analyze:** First, let's see why it's slow. Run this query in your client (in DataGrip, you can use the "Explain Plan" feature).

```sql
EXPLAIN SELECT * FROM workers WHERE last_name = 'Johnson';
```

Note the `type` (likely `ALL`) and `rows` (likely the full table count). This indicates a full table scan.

2. **Implement:** Now, let's create an index to fix it.

```sql
CREATE INDEX idx_worker_lastname ON workers(last_name);
```

3. **Verify:** Run the EXPLAIN query again.

```sql
EXPLAIN SELECT * FROM workers WHERE last_name = 'Johnson';
```

You should now see the `type` as `ref` and a much smaller `rows` count. The `key` should be `idx_worker_lastname`. It's now using the index!

**Task:** Add the EXPLAIN (before and after) and the CREATE INDEX statements to your `01_indexes.sql` file, separated by comments.

### Part 1B: Challenge Task (Creating a Composite Index)

The second request was about finding projects by city. After talking with the client, you learn they almost always search by `site_city` and then sort by `start_date`.

**Task:** Create an optimal composite index on the `projects` table to speed up this common query.

**Deliverable:**
- Add your CREATE INDEX statement to `01_indexes.sql`.
- In your `README.md`, add a section for "Module 1 Challenge" and justify your index. Why did you choose the columns in that specific order?

---