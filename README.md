[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/9-Jl7uxY)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=21479098)
# Big3 Construction: Phase 2 - Optimizing & Automating Operations

## Project Overview

**Scenario:** Big3 Construction was thrilled with the normalized 5NF database your team delivered in the Design Activity. The data is clean, redundant-free, and an order of magnitude more reliable.

Now that they've been using it for a few months, they've come back to you with a new set of "Phase 2" requirements. They don't just want to store data; they want to optimize performance, simplify access for different user roles, and automate common business processes.

Your team has been retained to implement these advanced features.

**Total Points:** 200 points  
**Team Size:** 3 members (this is a pair programming assignment) 

## Learning Objectives

By completing this project, you will:

- Analyze query performance and create **Indexes** to optimize data retrieval.
- Write complex, multi-level **Subqueries** and advanced **JOINs** to answer sophisticated business questions.
- Implement **Views** to simplify data access and enhance security.
- Create **Stored Procedures** to encapsulate and automate repetitive, multi-step business logic.
- Enforce complex business rules and maintain data integrity using **Triggers**.
- Schedule automated, recurring database tasks using **Events**.

## Phase 1 Standard Schema

To ensure all teams are working from a consistent, normalized database, this Phase 2 assignment is based on the following official 5NF schema.

Your Phase 1 implementation (your `01_create_tables.sql` and `02_insert_data.sql` scripts) must match this structure. All modules in this assignment assume your table and column names match this ERD.

```mermaid
erDiagram
    clients {
        int client_id PK "AUTO_INCREMENT"
        varchar_100 client_name "NOT NULL, UNIQUE"
        varchar_20 client_phone
    }
    projects {
        varchar_10 project_id PK "e.g., 'P001'"
        varchar_100 project_name "NOT NULL"
        varchar_200 site_address
        varchar_50 site_city
        date start_date
        date end_date
        decimal_12_2 budget
        int client_id FK "REFERENCES clients(client_id)"
    }
    workers {
        int worker_id PK "AUTO_INCREMENT"
        varchar_100 first_name "NOT NULL"
        varchar_100 last_name "NOT NULL"
        varchar_20 phone
        decimal_10_2 salary
    }
    skills {
        int skill_id PK "AUTO_INCREMENT"
        varchar_100 skill_name "NOT NULL, UNIQUE"
    }
    worker_skills {
        int worker_id FK "REFERENCES workers(worker_id)"
        int skill_id FK "REFERENCES skills(skill_id)"
    }
    certifications {
        int cert_id PK "AUTO_INCREMENT"
        varchar_100 cert_name "NOT NULL"
        date expiry_date
        int worker_id FK "REFERENCES workers(worker_id)"
    }
    project_assignments {
        int assignment_id PK "AUTO_INCREMENT"
        int worker_id FK "REFERENCES workers(worker_id)"
        varchar_10 project_id FK "REFERENCES projects(project_id)"
        date assignment_date
    }
    suppliers {
        int supplier_id PK "AUTO_INCREMENT"
        varchar_100 supplier_name "NOT NULL"
        varchar_20 supplier_phone
    }
    materials {
        int material_id PK "AUTO_INCREMENT"
        varchar_100 material_name "NOT NULL"
        decimal_10_2 unit_cost "NOT NULL"
    }
    project_materials {
        int project_material_id PK "AUTO_INCREMENT"
        varchar_10 project_id FK "REFERENCES projects(project_id)"
        int material_id FK "REFERENCES materials(material_id)"
        int supplier_id FK "REFERENCES suppliers(supplier_id)"
        int quantity "NOT NULL"
        decimal_12_2 total_cost "NOT NULL"
    }
    clients ||--o{ projects : "has"
    projects ||--|| project_assignments : "has"
    workers ||--|| project_assignments : "assigned to"
    workers ||--|| worker_skills : "has"
    skills ||--|| worker_skills : "possessed by"
    workers ||--o{ certifications : "holds"
    projects ||--o{ project_materials : "uses"
    materials ||--o{ project_materials : "used in"
    suppliers ||--o{ project_materials : "supplies"
```

## Project Setup & Delivery

This assignment builds directly on your "Phase 1" implementation. You will use the `big3_construction` database you built and populated according to the standard schema provided above.

- **GitHub Classroom:** Accept the "Phase 2" assignment from the link on Canvas. This will create a new repository for your team, pre-populated with a folder structure and this README.md.
- **Viewing the Schema Diagram:** To view the Mermaid ERD diagram in this README within VS Code:
  1. Open the Extensions panel (`Ctrl+Shift+X` or `Cmd+Shift+X` on Mac)
  2. Search for "Markdown Preview Mermaid Support"
  3. Install the extension by Matt Bierner
  4. Open this README.md and press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac) to open the Markdown preview
  5. The Entity-Relationship Diagram will now render visually
  
  *Note: The diagram also renders automatically when you view this README on GitHub.com*
- **Tools:** We recommend DataGrip as its database management features are excellent for this task. You can manage your scripts, run queries, and easily inspect your database objects (like views, procedures, and triggers) from the UI. However, you may use any tool you are comfortable with (MySQL Workbench, DBeaver, etc.).
- **Collaboration:** This is a pair programming assignment. We highly recommend you work on the logic for the "Challenge" sections together, either in person or over a screen share.

## Submission Requirements

You will submit your work by committing your SQL files to your GitHub Classroom repository. Your repository must contain the following files:

- `01_indexes.sql`: All SQL for Module 1.
- `02_subqueries.sql`: All SQL queries for Module 2.
- `03_views.sql`: All SQL for Module 3.
- `04_procedures.sql`: All SQL for Module 4.
- `05_triggers.sql`: All SQL for Module 5.
- `06_events.sql`: All SQL for Module 6.
- `README.md`: You must edit this file to add your justifications for the "Challenge" sections and a brief Team Contribution Statement at the end.


## Assignment Modules

Follow each module in order. Each one contains a Client Request, a Guided Activity to learn the concept, and a Challenge Task to apply your knowledge.

### [Module 1: Indexes (The "Need for Speed")](module-1/README.md)

### [Module 2: Subqueries & Advanced Joins (The "Complex Questions")](module-2/README.md)

### [Module 3: Views (The "Simple & Secure" Reports)](module-3/README.md)

### [Module 4: Stored Procedures (The "One-Click" Tasks)](module-4/README.md)

### [Module 5: Triggers (The "Automatic Rule-Enforcer")](module-5/README.md)

### [Module 6: Events (The "Scheduled Maintenance")](module-6/README.md)

## Resources & Support

### Official Documentation

- **MySQL Reference Manual:** [https://dev.mysql.com/doc/refman/8.0/en/](https://dev.mysql.com/doc/refman/8.0/en/)
  - Indexes: [https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html)
  - Subqueries: [https://dev.mysql.com/doc/refman/8.0/en/subqueries.html](https://dev.mysql.com/doc/refman/8.0/en/subqueries.html)
  - Views: [https://dev.mysql.com/doc/refman/8.0/en/views.html](https://dev.mysql.com/doc/refman/8.0/en/views.html)
  - Stored Procedures: [https://dev.mysql.com/doc/refman/8.0/en/stored-routines.html](https://dev.mysql.com/doc/refman/8.0/en/stored-routines.html)
  - Triggers: [https://dev.mysql.com/doc/refman/8.0/en/triggers.html](https://dev.mysql.com/doc/refman/8.0/en/triggers.html)
  - Events: [https://dev.mysql.com/doc/refman/8.0/en/events.html](https://dev.mysql.com/doc/refman/8.0/en/events.html)

### Getting Help

- **Office Hours:** Check Canvas for your instructor's availability
- **Discussion Forum:** Use the Canvas discussion board to ask questions and help your peers
- **Team Communication:** Establish regular check-ins with your team members
- **Debugging Tips:**
  - Use `EXPLAIN` to analyze query performance
  - Test each database object individually before combining them
  - Check error logs if stored procedures, triggers, or events fail
  - Use `SHOW WARNINGS;` to identify issues with your SQL statements

### Recommended Practices

- Commit your work frequently to GitHub with descriptive commit messages
- Test all SQL scripts in a development environment before finalizing
- Document your reasoning for design decisions, especially in challenge sections
- Review each other's code within your team before submission
- Keep a log of issues encountered and how you resolved them

## AI Usage Policy

### Permitted Uses

This assignment is designed to help you develop practical database administration skills that you will use in your professional career. You may use AI tools (such as GitHub Copilot, ChatGPT, or similar) in the following ways:

- **Syntax assistance:** Getting help with SQL syntax, function parameters, or command structure
- **Debugging support:** Understanding error messages and identifying potential issues in your code
- **Concept clarification:** Asking for explanations of database concepts covered in the modules
- **Code review:** Having AI review your code for potential improvements or best practices
- **Documentation:** Generating comments or documentation for your completed code

### Required Practices

When using AI tools, you must:

1. **Understand every line of code:** You are responsible for understanding and being able to explain all code you submit, regardless of its source
2. **Adapt and customize:** Do not submit AI-generated code without reviewing, testing, and adapting it to the specific requirements of Big3 Construction
3. **Document AI usage:** In your Team Contribution Statement, acknowledge when AI tools were used and how they assisted your work
4. **Verify correctness:** AI-generated solutions may contain errors or inefficiencies. Test thoroughly and validate against the assignment requirements

### Prohibited Uses

The following uses of AI are not permitted:

- Submitting entire modules or solutions generated by AI without understanding or modification
- Using AI to complete the assignment without genuine engagement with the learning objectives
- Copying AI-generated code that you cannot explain or defend during discussions
- Relying solely on AI instead of consulting official documentation and course materials

### Academic Integrity

Remember that the goal of this assignment is to develop your skills and understanding. While AI can be a valuable tool, it should enhance your learning, not replace it. You will be expected to discuss and defend your design decisions in team presentations or individual assessments. Work that demonstrates a lack of understanding or engagement with the material may be subject to academic integrity review.

If you have questions about appropriate AI usage for specific situations, consult with me before proceeding.

## Challenge Justifications

### Module 1 Challenge: Index Design

For the frequent query pattern "filter by `site_city` then sort by `start_date`" on table `projects`, we added the composite index `idx_projects_city_date` on `(site_city, start_date)`.

- Filtering column first: `site_city` improves selectivity for the WHERE clause.
- Sorting column second: `start_date` allows the optimizer to return rows already ordered, avoiding an extra sort.
- The index can be used for both equality/range filters on `site_city` and for ORDER BY `start_date` within each city.

### Module 2 Notes: Subqueries & Advanced Joins

We prepared queries that demonstrate common patterns required in this module:

- Workers earning above the average salary (scalar subquery).
- Projects where total material cost exceeds 50% of budget (aggregate with HAVING over a join).
- Workers without assignments (NOT EXISTS anti-join).
- Clients without projects (NOT EXISTS anti-join).

These are placed in `02_subqueries.sql` and align with the schema provided in this README.

## Team Contribution Statement

Initial repository setup for Modules 1 and 2 completed: created `01_indexes.sql` and `02_subqueries.sql`, added Module 1 index justification, and outlined Module 2 query rationale. Remaining modules will be completed collaboratively.

## Final Deliverable Check

- ☐ `01_indexes.sql`
- ☐ `02_subqueries.sql`
- ☐ `03_views.sql`
- ☐ `04_procedures.sql`
- ☐ `05_triggers.sql`
- ☐ `06_events.sql`
- ☐ `README.md` is updated with all challenge justifications and the Team Contribution Statement.
- ☐ All SQL is well-commented and runnable.



Good luck, consultants!