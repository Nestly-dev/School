USE big3_construction;

-- ============================================
-- MIGRATION 08: Update Project Coordinates
-- Updates all projects with realistic Kigali, Rwanda coordinates
-- ============================================

-- Verify latitude and longitude columns exist
SET @column_check = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'big3_construction' 
    AND TABLE_NAME = 'projects' 
    AND COLUMN_NAME IN ('latitude', 'longitude')
);

-- If columns don't exist, create them first
SET @sql = IF(@column_check < 2, 
    'ALTER TABLE projects ADD COLUMN latitude DECIMAL(10, 8) DEFAULT 0.0, ADD COLUMN longitude DECIMAL(11, 8) DEFAULT 0.0', 
    'SELECT "Coordinates columns already exist" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Update Project 1: Kigali Convention Center Renovation (Kimihurura area)
-- Coordinates: -1.9441, 30.0619 (Kimihurura, Kigali)
UPDATE projects
SET latitude = -1.9441,
    longitude = 30.0619
WHERE project_name = 'Kigali Convention Center Renovation'
  AND (latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL);

-- Update Project 2: Affordable Housing - Batsinda Phase 2 (Batsinda area)
-- Coordinates: -1.9167, 30.1167 (Batsinda, Gasabo District)
UPDATE projects
SET latitude = -1.9167,
    longitude = 30.1167
WHERE project_name = 'Affordable Housing - Batsinda Phase 2'
  AND (latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL);

-- Update Project 3: MTN Office Expansion (Nyarugenge area)
-- Coordinates: -1.9500, 30.0583 (Nyarugenge, Kigali)
UPDATE projects
SET latitude = -1.9500,
    longitude = 30.0583
WHERE project_name = 'MTN Office Expansion'
  AND (latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL);

-- Update Project 4: Bank of Kigali Branch - Kimironko (Kimironko area)
-- Coordinates: -1.9333, 30.1167 (Kimironko Market Area)
UPDATE projects
SET latitude = -1.9333,
    longitude = 30.1167
WHERE project_name = 'Bank of Kigali Branch - Kimironko'
  AND (latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL);

-- Update Project 5: Highway Maintenance - RN1 (Bugesera Highway)
-- Coordinates: -1.9500, 30.1500 (Kigali-Bugesera Highway)
UPDATE projects
SET latitude = -1.9500,
    longitude = 30.1500
WHERE project_name = 'Highway Maintenance - RN1'
  AND (latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL);

-- Update Project 6: School Construction - Kicukiro (Kicukiro District)
-- Coordinates: -2.0167, 30.0833 (Kicukiro District)
UPDATE projects
SET latitude = -2.0167,
    longitude = 30.0833
WHERE project_name = 'School Construction - Kicukiro'
  AND (latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL);

-- Update Project 7: Hospital Wing Extension (Kacyiru area)
-- Coordinates: -1.9500, 30.0833 (Kacyiru, Gasabo District)
UPDATE projects
SET latitude = -1.9500,
    longitude = 30.0833
WHERE project_name = 'Hospital Wing Extension'
  AND (latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL);

-- Display updated projects with their coordinates
SELECT 
    project_id,
    project_name,
    latitude,
    longitude,
    CASE 
        WHEN latitude = 0.0 AND longitude = 0.0 THEN '⚠️ Still has zero coordinates'
        WHEN latitude IS NULL OR longitude IS NULL THEN '⚠️ Has NULL coordinates'
        ELSE '✅ Coordinates updated'
    END AS status
FROM projects
ORDER BY project_id;

-- Summary
SELECT 
    COUNT(*) AS total_projects,
    SUM(CASE WHEN latitude != 0.0 AND longitude != 0.0 AND latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) AS projects_with_coordinates,
    SUM(CASE WHEN latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) AS projects_needing_coordinates
FROM projects;

SELECT 'Migration 08 completed successfully' AS status;

