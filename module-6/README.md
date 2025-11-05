## Module 6: Events (The "Scheduled Maintenance")

**Client Request:** "Finally, we have some cleanup tasks. We want to archive very old projects automatically so they don't clutter our active reports. Let's say, anything completed over 5 years ago."

### Part 6A: Guided Activity (Enabling the Event Scheduler)

**Concept:** The Event Scheduler is a database component that runs SQL statements at a specified time or on a recurring schedule.

**Guide:** First, you must ensure the scheduler is running.

**Check/Enable Scheduler:**

```sql
-- Check if it's on
SHOW VARIABLES LIKE 'event_scheduler';

-- Turn it on (if OFF)
SET GLOBAL event_scheduler = ON;
```

(Note: On some managed cloud databases, this might be on by default or set via a dashboard).

**Task:** Add these SHOW and SET commands to `06_events.sql`.

### Part 6B: Challenge Task (Creating an Archival Event)

Let's create the archival process.

**Task 1: Create Archive Table:**

Create a new table `archived_projects` that has the exact same structure as your `projects` table.

**Task 2: Create the Event:**

Create an EVENT named `ev_archive_old_projects`.

- **Schedule:** It should run once per month (e.g., `ON SCHEDULE EVERY 1 MONTH STARTS CURRENT_TIMESTAMP + INTERVAL 1 MONTH`).
- **Logic:** The event must do two things inside a transaction:
  1. `INSERT INTO archived_projects` all rows from `projects` where the `end_date` is not NULL and is older than 5 years (`end_date < CURDATE() - INTERVAL 5 YEAR`).
  2. `DELETE FROM projects` those same rows that were just archived.

**Deliverable:**
- Add the CREATE TABLE (archive table) and CREATE EVENT statements to `06_events.sql`.
- In your `README.md`, add a "Module 6 Challenge" section and explain how you would test this event safely without waiting a month. (Hint: You could temporarily change the schedule to `EVERY 1 MINUTE` or `AT CURRENT_TIMESTAMP + INTERVAL 5 SECOND`, or DISABLE the event and run its logic manually).

---