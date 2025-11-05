## Module 3: Views (The "Simple & Secure" Reports)

**Client Request:** "Our site supervisors need to see who is on their project, but they absolutely should not see sensitive info like worker salaries or client contact details. Separately, our accounting team needs a simple financial report. Can you create 'saved' reports for them?"

### Part 3A: Guided Activity (Creating a View for Supervisors)

**Concept:** A View is a virtual table based on the result-set of a SELECT statement. It's used to simplify complex queries and restrict access to data.

**Guide:** Let's create a "safe" list for supervisors.

**Implementation:**

```sql
CREATE VIEW v_project_worker_assignments AS
SELECT
    p.project_name,
    p.site_address,
    w.first_name,
    w.last_name,
    w.phone,
    pa.assignment_date
FROM projects p
JOIN project_assignments pa ON p.project_id = pa.project_id
JOIN workers w ON pa.worker_id = w.worker_id
ORDER BY p.project_name, w.last_name;
```

**Verify:** Now, the supervisor can just run a simple, safe query.

```sql
SELECT * FROM v_project_worker_assignments
WHERE project_name = 'Downtown Plaza';
```

**Task:** Add the CREATE VIEW statement and the `SELECT * FROM v_project_worker_assignments...` query to `03_views.sql`.

### Part 3B: Challenge Task (Creating a Financial Summary View)

The accounting team wants a high-level financial summary.

**Task:** Create a VIEW named `v_project_financial_summary`. This view must show:
- `project_name`
- `client_name` (from the `clients` table)
- `project_budget` (from the `projects` table)
- `total_materials_cost` (This will require you to SUM the `total_cost` from the `project_materials` table for each project)
- `remaining_budget` (Calculated as `budget - total_materials_cost`)

**Deliverable:** Add the CREATE VIEW statement to `03_views.sql`.

---