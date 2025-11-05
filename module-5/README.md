## Module 5: Triggers (The "Automatic Rule-Enforcer")

**Client Request:** "We need to maintain a strict audit trail. Any time a project's budget is increased, I want it logged. Also, we have a new safety rule: no worker can be assigned to a project if their safety certification is expired!"

### Part 5A: Guided Activity (An "AFTER UPDATE" Audit Trigger)

**Concept:** A Trigger is a stored procedure that runs automatically when an event (INSERT, UPDATE, DELETE) occurs on a table. OLD and NEW keywords let you compare values.

**Guide:** Let's create the budget audit log.

**Create Log Table:**

```sql
CREATE TABLE project_budget_audit (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10),
    old_budget DECIMAL(12, 2),
    new_budget DECIMAL(12, 2),
    change_user VARCHAR(100),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Create Trigger:**

```sql
DELIMITER $$

CREATE TRIGGER trg_audit_project_budget_update
AFTER UPDATE ON projects
FOR EACH ROW
BEGIN
    -- Only log if the budget *increased*
    IF NEW.budget > OLD.budget THEN
        INSERT INTO project_budget_audit(project_id, old_budget, new_budget, change_user)
        VALUES (OLD.project_id, OLD.budget, NEW.budget, USER());
    END IF;
END$$

DELIMITER ;
```

**Verify:**

```sql
-- Test it
UPDATE projects SET budget = budget + 50000 WHERE project_id = 'P001';
-- Check the audit table
SELECT * FROM project_budget_audit;
```

**Task:** Add the CREATE TABLE (log table), CREATE TRIGGER, and UPDATE/SELECT (verification) statements to `05_triggers.sql`.

### Part 5B: Challenge Task (A "BEFORE INSERT" Validation Trigger)

This is the safety rule. This is a complex but realistic challenge.

**Task:** Create a BEFORE INSERT trigger on your `project_assignments` table.

**Logic:**
- Before a new row is inserted (using `NEW.worker_id`), the trigger must check the `certifications` table for that worker.
- It must find the certification named 'Basic Safety'.
- It must check the `expiry_date` for that specific certification.
- If the 'Basic Safety' cert doesn't exist OR if its `expiry_date` is in the past (e.g., `expiry_date < CURDATE()`), the trigger must prevent the insertion and signal an error.

(Hint: You'll need to DECLARE a variable to hold the expiry date, then SELECT it INTO your variable. Then use an IF statement. Use `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Worker safety certification is expired or missing.';` to stop the INSERT).

**Deliverable:**
- Add the CREATE TRIGGER statement to `05_triggers.sql`.
- In your `README.md`, add a section for "Module 5 Challenge" and explain how you tested your trigger (e.g., "First, I manually set a worker's 'Basic Safety' cert to be expired. Then I tried to assign them to a project, and the INSERT failed as expected.")

---