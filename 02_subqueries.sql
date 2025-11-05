USE big3_construction;

-- Module 2: Subqueries & Advanced Joins

-- 1) Workers who earn more than the average salary (scalar subquery)
SELECT w.worker_id, w.first_name, w.last_name, w.salary
FROM workers w
WHERE w.salary > (SELECT AVG(salary) FROM workers);

-- 2) Projects where total material cost exceeds 50% of project budget (aggregate + HAVING)
SELECT 
  p.project_id,
  p.project_name,
  p.budget,
  COALESCE(SUM(pm.total_cost), 0) AS total_material_cost
FROM projects p
LEFT JOIN project_materials pm ON pm.project_id = p.project_id
GROUP BY p.project_id, p.project_name, p.budget
HAVING COALESCE(SUM(pm.total_cost), 0) > p.budget * 0.5
ORDER BY total_material_cost DESC;

-- 3) Workers with no project assignments (NOT EXISTS)
SELECT w.worker_id, w.first_name, w.last_name
FROM workers w
WHERE NOT EXISTS (
  SELECT 1 
  FROM project_assignments pa 
  WHERE pa.worker_id = w.worker_id
);

-- 4) Clients without any projects (anti-join via NOT EXISTS)
SELECT c.client_id, c.client_name
FROM clients c
WHERE NOT EXISTS (
  SELECT 1 
  FROM projects p 
  WHERE p.client_id = c.client_id
);
