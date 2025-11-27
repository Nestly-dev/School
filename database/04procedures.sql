USE big3_construction;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_add_worker_with_skill $$
CREATE PROCEDURE sp_add_worker_with_skill(
    IN p_first_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_hourly_rate DECIMAL(10, 2),
    IN p_skill_name VARCHAR(100)
)
BEGIN
    DECLARE v_worker_id INT;
    DECLARE v_skill_id INT;

    DECLARE exit handler FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    INSERT INTO workers(first_name, last_name, phone, hourly_rate, role, hire_date)
    VALUES (p_first_name, p_last_name, p_phone, p_hourly_rate, 'Specialist', CURRENT_DATE);

    SET v_worker_id = LAST_INSERT_ID();

    SELECT skill_id INTO v_skill_id FROM skills WHERE skill_name = p_skill_name LIMIT 1;

    IF v_skill_id IS NULL THEN
        INSERT INTO skills(skill_name) VALUES (p_skill_name);
        SET v_skill_id = LAST_INSERT_ID();
    END IF;

    INSERT INTO worker_skills(worker_id, skill_id, acquired_date)
    VALUES (v_worker_id, v_skill_id, CURRENT_DATE);

    COMMIT;

    SELECT CONCAT('Worker ', p_first_name, ' ', p_last_name, ' added with skill ', p_skill_name) AS message;
END $$

DROP PROCEDURE IF EXISTS sp_assign_worker_to_project_once $$
CREATE PROCEDURE sp_assign_worker_to_project_once(
    IN p_worker_id INT,
    IN p_project_id INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_assignment_count INT;

    SELECT COUNT(*) INTO v_assignment_count
    FROM project_assignments
    WHERE worker_id = p_worker_id AND project_id = p_project_id;

    IF v_assignment_count > 0 THEN
        SET p_message = 'Error: Worker already assigned to this project.';
    ELSE
        INSERT INTO project_assignments(worker_id, project_id, assigned_date)
        VALUES (p_worker_id, p_project_id, CURDATE());

        SET p_message = 'Success: Worker assigned.';
    END IF;
END $$

DELIMITER ;

CALL sp_add_worker_with_skill('Alice', 'Smith', '+250700000000', 25.00, 'Project Management');

SELECT w.worker_id, w.first_name, w.last_name, w.hourly_rate, s.skill_name
FROM workers w
LEFT JOIN worker_skills ws ON w.worker_id = ws.worker_id
LEFT JOIN skills s ON ws.skill_id = s.skill_id
WHERE w.first_name = 'Alice' AND w.last_name = 'Smith';

CALL sp_assign_worker_to_project_once(1, 1, @message);
SELECT @message AS assignment_result;

CALL sp_assign_worker_to_project_once(1, 1, @message);
SELECT @message AS assignment_result;

CALL sp_assign_worker_to_project_once(2, 1, @message);
SELECT @message AS assignment_result;