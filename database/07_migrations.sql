-- Create users table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Project Manager', 'Site Supervisor') NOT NULL,
    preferred_language VARCHAR(10) DEFAULT 'en',
    worker_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE SET NULL
);

-- Add indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Add latitude and longitude to projects table
ALTER TABLE projects
ADD COLUMN latitude DECIMAL(10, 8) DEFAULT 0.0,
ADD COLUMN longitude DECIMAL(11, 8) DEFAULT 0.0;

-- Ensure legacy rows have default coordinates to prevent null math
UPDATE projects
SET latitude = 0.0,
    longitude = 0.0
WHERE latitude IS NULL
   OR longitude IS NULL;

-- Add index for geospatial queries
CREATE INDEX idx_projects_location ON projects(latitude, longitude);