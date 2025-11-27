DROP DATABASE IF EXISTS big3_construction;
CREATE DATABASE big3_construction;
USE big3_construction;

-- ============================================
-- 1. CORE TABLES
-- ============================================

-- Clients table
CREATE TABLE clients (
    client_id INT PRIMARY KEY AUTO_INCREMENT,
    client_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workers table
CREATE TABLE workers (
    worker_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    role VARCHAR(100),
    hire_date DATE,
    hourly_rate DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE projects (
    project_id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(255) NOT NULL,
    client_id INT,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15, 2),
    status ENUM('Planning', 'In Progress', 'Completed', 'On Hold') DEFAULT 'Planning',
    description TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE SET NULL
);

-- Project-Worker assignments (many-to-many)
CREATE TABLE project_assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    worker_id INT NOT NULL,
    assigned_date DATE DEFAULT (CURRENT_DATE),
    role_on_project VARCHAR(100),
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (project_id, worker_id)
);

-- Certifications table
CREATE TABLE certifications (
    certification_id INT PRIMARY KEY AUTO_INCREMENT,
    worker_id INT NOT NULL,
    certification_name VARCHAR(255) NOT NULL,
    issue_date DATE,
    expiration_date DATE,
    issuing_authority VARCHAR(255),
    FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE CASCADE
);

-- Suppliers table
CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Materials table
CREATE TABLE materials (
    material_id INT PRIMARY KEY AUTO_INCREMENT,
    material_name VARCHAR(255) NOT NULL,
    supplier_id INT,
    unit_price DECIMAL(10, 2),
    unit_of_measure VARCHAR(50),
    stock_quantity INT DEFAULT 0,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
);

-- Skills catalog
CREATE TABLE skills (
    skill_id INT PRIMARY KEY AUTO_INCREMENT,
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Worker skills link table
CREATE TABLE worker_skills (
    worker_skill_id INT PRIMARY KEY AUTO_INCREMENT,
    worker_id INT NOT NULL,
    skill_id INT NOT NULL,
    acquired_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    UNIQUE KEY unique_worker_skill (worker_id, skill_id)
);

-- Project materials usage
CREATE TABLE project_materials (
    project_material_id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    material_id INT NOT NULL,
    quantity DECIMAL(12, 2) NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,
    total_cost DECIMAL(15, 2) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE CASCADE
);

-- ============================================
-- 2. REQUIRED VIEW
-- ============================================

CREATE VIEW v_project_worker_assignments AS
SELECT 
    pa.assignment_id,
    pa.project_id,
    p.project_name,
    pa.worker_id,
    CONCAT(w.first_name, ' ', w.last_name) AS worker_name,
    w.email AS worker_email,
    pa.role_on_project,
    pa.assigned_date,
    p.status AS project_status
FROM project_assignments pa
JOIN projects p ON pa.project_id = p.project_id
JOIN workers w ON pa.worker_id = w.worker_id;

-- ============================================
-- 3. REQUIRED STORED PROCEDURE
-- ============================================

DELIMITER //

CREATE PROCEDURE sp_assign_worker_to_project(
    IN p_worker_id INT,
    IN p_project_id INT,
    IN p_role VARCHAR(100)
)
BEGIN
    -- Check if worker exists
    IF NOT EXISTS (SELECT 1 FROM workers WHERE worker_id = p_worker_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Worker does not exist';
    END IF;
    
    -- Check if project exists
    IF NOT EXISTS (SELECT 1 FROM projects WHERE project_id = p_project_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Project does not exist';
    END IF;
    
    -- Check if already assigned
    IF EXISTS (
        SELECT 1 FROM project_assignments 
        WHERE worker_id = p_worker_id AND project_id = p_project_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Worker already assigned to this project';
    END IF;
    
    -- Insert assignment
    INSERT INTO project_assignments (project_id, worker_id, role_on_project)
    VALUES (p_project_id, p_worker_id, p_role);
    
    SELECT 'Worker successfully assigned to project' AS message;
END //

DELIMITER ;

-- ============================================
-- 4. SAMPLE DATA
-- ============================================

-- Insert Clients
INSERT INTO clients (client_name, contact_email, contact_phone, address) VALUES
('Kigali City Council', 'projects@kigalicity.gov.rw', '+250788123456', 'KN 3 Ave, Kigali'),
('Rwanda Housing Authority', 'info@rha.gov.rw', '+250788234567', 'KG 7 Ave, Kigali'),
('MTN Rwanda', 'construction@mtn.rw', '+250788345678', 'MTN Center, Nyarugenge'),
('Bank of Kigali', 'facilities@bk.rw', '+250788456789', 'KCB Plaza, Kigali'),
('Ministry of Infrastructure', 'mininfra@gov.rw', '+250788567890', 'Kigali Heights');

-- Insert Workers
INSERT INTO workers (first_name, last_name, email, phone, role, hire_date, hourly_rate) VALUES
('Jean', 'Mugabo', 'jean.mugabo@big3.rw', '+250788111111', 'Project Manager', '2020-01-15', 25.00),
('Grace', 'Uwase', 'grace.uwase@big3.rw', '+250788222222', 'Site Supervisor', '2020-03-20', 20.00),
('David', 'Nkurunziza', 'david.nkurunziza@big3.rw', '+250788333333', 'Electrician', '2021-05-10', 18.00),
('Sarah', 'Mukamana', 'sarah.mukamana@big3.rw', '+250788444444', 'Carpenter', '2021-06-15', 17.00),
('Patrick', 'Habimana', 'patrick.habimana@big3.rw', '+250788555555', 'Plumber', '2021-07-01', 17.00),
('Claudine', 'Ingabire', 'claudine.ingabire@big3.rw', '+250788666666', 'Mason', '2021-08-20', 16.00),
('Eric', 'Nsengimana', 'eric.nsengimana@big3.rw', '+250788777777', 'Site Supervisor', '2022-01-10', 20.00),
('Agnes', 'Umutoni', 'agnes.umutoni@big3.rw', '+250788888888', 'Safety Officer', '2022-02-15', 19.00),
('Robert', 'Kayitare', 'robert.kayitare@big3.rw', '+250788999999', 'Heavy Equipment Operator', '2022-03-01', 18.00),
('Marie', 'Uwineza', 'marie.uwineza@big3.rw', '+250788101010', 'Surveyor', '2022-04-10', 21.00);

-- Insert Projects
INSERT INTO projects (project_name, client_id, start_date, end_date, budget, status, description, address) VALUES
('Kigali Convention Center Renovation', 1, '2024-01-15', '2024-12-31', 500000.00, 'In Progress', 'Complete renovation of main conference halls', 'KN 3 Ave, Kimihurura'),
('Affordable Housing - Batsinda Phase 2', 2, '2024-02-01', '2025-06-30', 2000000.00, 'In Progress', 'Construction of 200 housing units', 'Batsinda, Gasabo'),
('MTN Office Expansion', 3, '2024-03-15', '2024-09-30', 750000.00, 'Planning', 'New office wing and parking structure', 'MTN Center, Nyarugenge'),
('Bank of Kigali Branch - Kimironko', 4, '2024-04-01', '2024-11-30', 450000.00, 'In Progress', 'New bank branch construction', 'Kimironko Market Area'),
('Highway Maintenance - RN1', 5, '2024-05-01', '2024-08-31', 300000.00, 'Planning', 'Road resurfacing and drainage improvement', 'Kigali-Bugesera Highway'),
('School Construction - Kicukiro', 1, '2024-06-01', '2025-03-31', 1200000.00, 'Planning', 'New primary school with 20 classrooms', 'Kicukiro District'),
('Hospital Wing Extension', 5, '2023-09-01', '2024-06-30', 1800000.00, 'In Progress', 'New emergency and ICU wing', 'Kacyiru, Gasabo');

-- Insert Project Assignments
INSERT INTO project_assignments (project_id, worker_id, role_on_project) VALUES
(1, 1, 'Project Manager'),
(1, 2, 'Site Supervisor'),
(1, 3, 'Lead Electrician'),
(2, 1, 'Project Manager'),
(2, 7, 'Site Supervisor'),
(2, 4, 'Lead Carpenter'),
(3, 2, 'Site Supervisor'),
(4, 7, 'Site Supervisor'),
(4, 5, 'Lead Plumber'),
(7, 1, 'Project Manager'),
(7, 2, 'Site Supervisor');

-- Insert Certifications (some expiring soon!)
INSERT INTO certifications (worker_id, certification_name, issue_date, expiration_date, issuing_authority) VALUES
(1, 'Project Management Professional (PMP)', '2022-01-15', '2025-01-15', 'PMI'),
(2, 'Safety Management Certificate', '2023-06-01', '2024-12-15', 'Rwanda Standards Board'),
(3, 'Master Electrician License', '2021-03-10', '2024-12-20', 'Rwanda Utilities Regulatory Authority'),
(4, 'Advanced Carpentry Certificate', '2022-05-20', '2025-05-20', 'IPRC Kigali'),
(5, 'Plumbing License', '2023-02-15', '2025-02-15', 'Rwanda Standards Board'),
(6, 'Masonry Level 3 Certificate', '2022-08-10', '2025-08-10', 'IPRC Kigali'),
(7, 'Site Supervision Certificate', '2023-09-01', '2024-12-25', 'Rwanda Standards Board'),
(8, 'Occupational Safety and Health', '2023-03-15', '2024-12-10', 'Ministry of Labour'),
(9, 'Heavy Equipment Operation License', '2022-11-20', '2025-11-20', 'Rwanda Transport Authority'),
(10, 'Land Surveying License', '2021-07-30', '2024-12-30', 'Rwanda Land Management Authority');

-- Insert Suppliers
INSERT INTO suppliers (supplier_name, contact_email, contact_phone, address) VALUES
('Ruliba Clays & Cement', 'sales@ruliba.rw', '+250788123001', 'Ruliba, Karongi'),
('CIMERWA Limited', 'info@cimerwa.rw', '+250788123002', 'Rusizi District'),
('Tubura Steel Ltd', 'sales@tuburasteel.rw', '+250788123003', 'KK 15 Ave, Kigali'),
('Kigali Hardware Suppliers', 'info@kigalihardware.rw', '+250788123004', 'Gikondo Industrial Park'),
('Rwanda Timber Products', 'sales@rwandatimber.rw', '+250788123005', 'Huye District');

-- Insert Materials
INSERT INTO materials (material_name, supplier_id, unit_price, unit_of_measure, stock_quantity) VALUES
('Portland Cement', 2, 15.50, 'bag (50kg)', 500),
('Steel Rebar 12mm', 3, 8.25, 'meter', 2000),
('Concrete Blocks', 1, 0.75, 'piece', 5000),
('Roofing Sheets (Corrugated)', 4, 12.00, 'sheet', 300),
('Timber Planks (2x4)', 5, 3.50, 'piece (3m)', 800),
('Sand (Construction Grade)', 1, 25.00, 'cubic meter', 100),
('Gravel', 1, 30.00, 'cubic meter', 150),
('PVC Pipes 4"', 4, 5.75, 'meter', 400),
('Electrical Wire 2.5mm', 4, 1.20, 'meter', 1000),
('Paint (Exterior White)', 4, 18.00, 'gallon (5L)', 50);

-- Insert Skills
INSERT INTO skills (skill_name, description) VALUES
('Project Management', 'Planning, executing, and closing projects'),
('Electrical', 'Electrical wiring and safety'),
('Carpentry', 'Woodwork and structural framing'),
('Plumbing', 'Pipe installation and maintenance'),
('Masonry', 'Bricklaying and concrete work'),
('Safety Management', 'On-site safety protocols');

-- Link workers to skills
INSERT INTO worker_skills (worker_id, skill_id, acquired_date) VALUES
(1, 1, '2019-05-10'),
(2, 6, '2020-07-18'),
(3, 2, '2021-03-10'),
(4, 3, '2021-05-20'),
(5, 4, '2021-06-15'),
(6, 5, '2021-08-10'),
(7, 6, '2022-02-01');

-- Record material usage per project (costs generated automatically)
INSERT INTO project_materials (project_id, material_id, quantity, unit_cost) VALUES
(1, 1, 200.00, 15.50),
(1, 2, 500.00, 8.25),
(2, 3, 1500.00, 0.75),
(2, 5, 800.00, 3.50),
(3, 4, 250.00, 12.00),
(4, 7, 120.00, 30.00),
(5, 6, 60.00, 25.00);

-- ============================================
-- 5. VERIFY SETUP
-- ============================================

-- Test the view
SELECT * FROM v_project_worker_assignments LIMIT 5;

-- Test the stored procedure
CALL sp_assign_worker_to_project(8, 3, 'Safety Officer');

-- Show summary
SELECT 
    (SELECT COUNT(*) FROM clients) AS total_clients,
    (SELECT COUNT(*) FROM workers) AS total_workers,
    (SELECT COUNT(*) FROM projects) AS total_projects,
    (SELECT COUNT(*) FROM certifications) AS total_certifications,
    (SELECT COUNT(*) FROM suppliers) AS total_suppliers,
    (SELECT COUNT(*) FROM materials) AS total_materials;