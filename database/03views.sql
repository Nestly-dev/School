USE big3_construction;

DROP VIEW IF EXISTS v_project_worker_assignments;
CREATE VIEW v_project_worker_assignments AS
SELECT
    pa.assignment_id,
    p.project_id,
    p.project_name,
    p.address AS site_address,
    w.worker_id,
    w.first_name,
    w.last_name,
    w.phone,
    pa.assigned_date AS assignment_date,
    pa.role_on_project
FROM projects p
JOIN project_assignments pa ON p.project_id = pa.project_id
JOIN workers w ON pa.worker_id = w.worker_id
ORDER BY p.project_name, w.last_name;

SELECT * FROM v_project_worker_assignments
WHERE project_name = 'Kigali Convention Center Renovation';

DROP VIEW IF EXISTS v_project_financial_summary;
CREATE VIEW v_project_financial_summary AS
SELECT 
    p.project_id,
    p.project_name,
    c.client_name,
    p.budget AS project_budget,
    COALESCE(SUM(pm.total_cost), 0) AS total_materials_cost,
    p.budget - COALESCE(SUM(pm.total_cost), 0) AS remaining_budget
FROM projects p
JOIN clients c ON p.client_id = c.client_id
LEFT JOIN project_materials pm ON p.project_id = pm.project_id
GROUP BY p.project_id, p.project_name, c.client_name, p.budget
ORDER BY p.project_name;

SELECT * FROM v_project_financial_summary;

SELECT * FROM v_project_financial_summary
WHERE remaining_budget < project_budget * 0.2
ORDER BY remaining_budget ASC;