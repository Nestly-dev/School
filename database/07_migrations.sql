USE big3_construction;

-- ============================================
-- MIGRATION 07: Users Table & Project Coordinates
-- ============================================

-- Create users table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Project Manager', 'Site Supervisor') NOT NULL,
    preferred_language VARCHAR(10) DEFAULT 'en',
    worker_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE SET NULL
);

-- Add indexes for better performance (if they don't exist)
-- Note: MySQL doesn't support IF NOT EXISTS for indexes, so we check first
SET @index_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = 'big3_construction' 
    AND TABLE_NAME = 'users' 
    AND INDEX_NAME = 'idx_users_email'
);

SET @sql = IF(@index_exists = 0, 
    'CREATE INDEX idx_users_email ON users(email)', 
    'SELECT "Index idx_users_email already exists" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @index_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = 'big3_construction' 
    AND TABLE_NAME = 'users' 
    AND INDEX_NAME = 'idx_users_role'
);

SET @sql = IF(@index_exists = 0, 
    'CREATE INDEX idx_users_role ON users(role)', 
    'SELECT "Index idx_users_role already exists" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add latitude and longitude to projects table (if columns don't exist)
SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'big3_construction' 
    AND TABLE_NAME = 'projects' 
    AND COLUMN_NAME = 'latitude'
);

SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE projects ADD COLUMN latitude DECIMAL(10, 8) DEFAULT 0.0', 
    'SELECT "Column latitude already exists" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'big3_construction' 
    AND TABLE_NAME = 'projects' 
    AND COLUMN_NAME = 'longitude'
);

SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE projects ADD COLUMN longitude DECIMAL(11, 8) DEFAULT 0.0', 
    'SELECT "Column longitude already exists" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Ensure legacy rows have default coordinates to prevent null math
UPDATE projects
SET latitude = 0.0,
    longitude = 0.0
WHERE latitude IS NULL
   OR longitude IS NULL;

-- Add index for geospatial queries (if it doesn't exist)
SET @index_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = 'big3_construction' 
    AND TABLE_NAME = 'projects' 
    AND INDEX_NAME = 'idx_projects_location'
);

SET @sql = IF(@index_exists = 0, 
    'CREATE INDEX idx_projects_location ON projects(latitude, longitude)', 
    'SELECT "Index idx_projects_location already exists" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'Migration 07 completed successfully' AS status;