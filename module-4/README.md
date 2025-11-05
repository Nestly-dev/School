## Module 4: Stored Procedures (The "One-Click" Tasks)

**Client Request:** "Our HR department is tired of running multiple INSERT statements just to add a new worker and their first skill. And our project managers want a simple way to assign a worker to a project without causing errors. We need to automate these."

### Part 4A: Guided Activity (A Simple IN Procedure)

**Concept:** A Stored Procedure is a set of SQL statements saved in the database. It can take input (IN) parameters, return output (OUT) parameters, and perform complex logic, all in one command.

**Guide:** Let's help HR add a new worker and their primary skill. (Note: You'll need to use DELIMITER to change the statement terminator).

**Implementation:**

```sql
DELIMITER $$

CREATE PROCEDURE sp_add_worker_with_skill(
    IN p_first_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_salary DECIMAL(10, 2),
    IN p_skill_name VARCHAR(100)
)
BEGIN
    -- Declare variables
    DECLARE v_worker_id INT;
    DECLARE v_skill_id INT;

    -- Start a transaction
    START TRANSACTION;

    -- Insert new worker
    INSERT INTO workers(first_name, last_name, phone, salary)
    VALUES (p_first_name, p_last_name, p_phone, p_salary);

    -- Get the new worker's ID
    SET v_worker_id = LAST_INSERT_ID();

    -- Find the skill's ID
    SELECT skill_id INTO v_skill_id FROM skills WHERE skill_name = p_skill_name;

    -- Add the skill, if it exists
    IF v_skill_id IS NOT NULL THEN
        INSERT INTO worker_skills(worker_id, skill_id)
        VALUES (v_worker_id, v_skill_id);
    END IF;

    -- Commit the transaction
    COMMIT;
END$$

DELIMITER ;
```

**Verify:**

```sql
CALL sp_add_worker_with_skill('Alice', 'Smith', '555-1234', 75000.00, 'Project Management');
-- Check your tables to see if Alice and her skill were added
```

**Task:** Add the CREATE PROCEDURE statement and the CALL statement to `04_procedures.sql`.

### Part 4B: Challenge Task (A Procedure with Logic & OUT Params)

The project managers want a "smart" procedure to assign workers.

**Task:** Create a stored procedure `sp_assign_worker_to_project` that takes `IN p_worker_id` (INT) and `IN p_project_id` (VARCHAR(10)). It must also have one OUT parameter `p_message VARCHAR(255)`.

**Logic:**
- Check if the worker is already assigned to that project (in `project_assignments`).
- If YES: Set `p_message` to `'Error: Worker already assigned to this project.'`
- If NO: Insert the new assignment into `project_assignments` (with `assignment_date = CURDATE()`) and set `p_message` to `'Success: Worker assigned.'`

(Hint: Use `IF EXISTS(...)` or `COUNT(*)` to check for the existing record).

**Deliverable:**
- Add the CREATE PROCEDURE statement to `04_procedures.sql`.
- Include a CALL statement to test it, along with a `SELECT @message;` to show the output.

---