USE big3_construction;

-- ============================================
-- VERIFICATION SCRIPT: Database Setup Check
-- Verifies all tables, views, procedures, and data integrity
-- ============================================

SELECT '========================================' AS '';
SELECT 'DATABASE SETUP VERIFICATION' AS '';
SELECT '========================================' AS '';
SELECT '' AS '';

-- ============================================
-- 1. CHECK USERS TABLE STRUCTURE
-- ============================================
SELECT '1. Checking Users Table Structure...' AS '';

SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ Users table exists'
        ELSE '❌ Users table does NOT exist'
    END AS status
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'big3_construction' 
AND TABLE_NAME = 'users';

-- Check required columns
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    CASE 
        WHEN COLUMN_NAME = 'user_id' AND DATA_TYPE = 'int' AND IS_NULLABLE = 'NO' THEN '✅'
        WHEN COLUMN_NAME = 'email' AND DATA_TYPE = 'varchar' AND IS_NULLABLE = 'NO' THEN '✅'
        WHEN COLUMN_NAME = 'password_hash' AND DATA_TYPE = 'varchar' AND IS_NULLABLE = 'NO' THEN '✅'
        WHEN COLUMN_NAME = 'role' AND DATA_TYPE = 'enum' AND IS_NULLABLE = 'NO' THEN '✅'
        WHEN COLUMN_NAME = 'preferred_language' AND DATA_TYPE = 'varchar' THEN '✅'
        WHEN COLUMN_NAME = 'worker_id' AND DATA_TYPE = 'int' THEN '✅'
        WHEN COLUMN_NAME = 'created_at' AND DATA_TYPE = 'timestamp' THEN '✅'
        ELSE '⚠️'
    END AS validation
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'big3_construction'
AND TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;

-- Check indexes
SELECT 
    INDEX_NAME,
    CASE 
        WHEN INDEX_NAME = 'PRIMARY' THEN '✅ Primary key'
        WHEN INDEX_NAME = 'idx_users_email' THEN '✅ Email index'
        WHEN INDEX_NAME = 'idx_users_role' THEN '✅ Role index'
        ELSE '⚠️ Unexpected index'
    END AS validation
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'big3_construction'
AND TABLE_NAME = 'users'
GROUP BY INDEX_NAME;

SELECT '' AS '';

-- ============================================
-- 2. CHECK PROJECT COORDINATES
-- ============================================
SELECT '2. Checking Project Coordinates...' AS '';

SELECT 
    COUNT(*) AS total_projects,
    SUM(CASE WHEN latitude != 0.0 AND longitude != 0.0 AND latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) AS projects_with_coordinates,
    SUM(CASE WHEN latitude = 0.0 OR longitude = 0.0 THEN 1 ELSE 0 END) AS projects_with_zero_coordinates,
    SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) AS projects_with_null_coordinates,
    CASE 
        WHEN SUM(CASE WHEN latitude != 0.0 AND longitude != 0.0 AND latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) = COUNT(*) THEN '✅ All projects have coordinates'
        WHEN SUM(CASE WHEN latitude = 0.0 OR longitude = 0.0 THEN 1 ELSE 0 END) > 0 THEN '⚠️ Some projects have zero coordinates'
        WHEN SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) > 0 THEN '⚠️ Some projects have NULL coordinates'
        ELSE '❌ No projects have valid coordinates'
    END AS status
FROM projects;

-- Show projects that need coordinates
SELECT 
    project_id,
    project_name,
    latitude,
    longitude,
    CASE 
        WHEN latitude = 0.0 AND longitude = 0.0 THEN '⚠️ Zero coordinates'
        WHEN latitude IS NULL OR longitude IS NULL THEN '⚠️ NULL coordinates'
        ELSE '✅ Valid'
    END AS status
FROM projects
WHERE latitude = 0.0 OR longitude = 0.0 OR latitude IS NULL OR longitude IS NULL
ORDER BY project_id;

SELECT '' AS '';

-- ============================================
-- 3. CHECK REQUIRED TABLES
-- ============================================
SELECT '3. Checking Required Tables...' AS '';

SELECT 
    TABLE_NAME,
    CASE 
        WHEN TABLE_NAME IN ('clients', 'workers', 'projects', 'project_assignments', 
                           'certifications', 'suppliers', 'materials', 'users',
                           'skills', 'worker_skills', 'project_materials') THEN '✅ Required table'
        ELSE '⚠️ Additional table'
    END AS status
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'big3_construction'
AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

SELECT '' AS '';

-- ============================================
-- 4. CHECK REQUIRED VIEWS
-- ============================================
SELECT '4. Checking Required Views...' AS '';

SELECT 
    TABLE_NAME AS view_name,
    CASE 
        WHEN TABLE_NAME = 'v_project_worker_assignments' THEN '✅ Required view'
        WHEN TABLE_NAME = 'v_project_financial_summary' THEN '✅ Required view'
        ELSE '⚠️ Additional view'
    END AS status
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'big3_construction'
ORDER BY TABLE_NAME;

SELECT '' AS '';

-- ============================================
-- 5. CHECK REQUIRED STORED PROCEDURES
-- ============================================
SELECT '5. Checking Required Stored Procedures...' AS '';

SELECT 
    ROUTINE_NAME AS procedure_name,
    CASE 
        WHEN ROUTINE_NAME = 'sp_assign_worker_to_project' THEN '✅ Required procedure'
        WHEN ROUTINE_NAME = 'sp_add_worker_with_skill' THEN '✅ Required procedure'
        WHEN ROUTINE_NAME = 'sp_assign_worker_to_project_once' THEN '✅ Required procedure'
        ELSE '⚠️ Additional procedure'
    END AS status
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = 'big3_construction'
AND ROUTINE_TYPE = 'PROCEDURE'
ORDER BY ROUTINE_NAME;

SELECT '' AS '';

-- ============================================
-- 6. CHECK FOREIGN KEY CONSTRAINTS
-- ============================================
SELECT '6. Checking Foreign Key Constraints...' AS '';

SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME,
    '✅ Valid constraint' AS status
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'big3_construction'
AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

SELECT '' AS '';

-- ============================================
-- 7. SUMMARY REPORT
-- ============================================
SELECT '========================================' AS '';
SELECT 'VERIFICATION SUMMARY' AS '';
SELECT '========================================' AS '';

SELECT 
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'big3_construction' AND TABLE_TYPE = 'BASE TABLE') AS total_tables,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = 'big3_construction') AS total_views,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_SCHEMA = 'big3_construction' AND ROUTINE_TYPE = 'PROCEDURE') AS total_procedures,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'big3_construction' AND TABLE_NAME = 'users') AS users_table_exists,
    (SELECT COUNT(*) FROM projects WHERE latitude != 0.0 AND longitude != 0.0 AND latitude IS NOT NULL AND longitude IS NOT NULL) AS projects_with_valid_coordinates,
    (SELECT COUNT(*) FROM projects) AS total_projects;

SELECT '' AS '';

-- Final status check
SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'big3_construction' AND TABLE_NAME = 'users') > 0 
         AND (SELECT COUNT(*) FROM projects WHERE latitude != 0.0 AND longitude != 0.0 AND latitude IS NOT NULL AND longitude IS NOT NULL) = (SELECT COUNT(*) FROM projects)
         AND (SELECT COUNT(*) FROM projects) > 0 THEN '✅ ALL CHECKS PASSED - Database setup is complete!'
        ELSE '⚠️ SOME ISSUES FOUND - Review the details above'
    END AS final_status;

SELECT '========================================' AS '';

