-- =================================================================
-- Phase 1: Equipment Management System - DOWN Migration
-- Description: Rollback equipment and calibration tables
-- Created: 2025-12-01
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop view first
DROP VIEW IF EXISTS equipment_calibration_status CASCADE;

-- Drop triggers
DROP TRIGGER IF EXISTS calibration_status_update ON calibration_records;
DROP TRIGGER IF EXISTS equipment_update_timestamp ON equipment;

-- Drop functions
DROP FUNCTION IF EXISTS check_calibration_status() CASCADE;
DROP FUNCTION IF EXISTS update_equipment_timestamp() CASCADE;

-- Drop tables (cascade to remove foreign key constraints)
DROP TABLE IF EXISTS calibration_records CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;

-- Drop indexes (will be automatically dropped with tables, but explicitly listing for documentation)
-- DROP INDEX IF EXISTS idx_equipment_equipment_id;
-- DROP INDEX IF EXISTS idx_equipment_category;
-- DROP INDEX IF EXISTS idx_equipment_status;
-- DROP INDEX IF EXISTS idx_equipment_next_calibration;
-- DROP INDEX IF EXISTS idx_calibration_equipment_id;
-- DROP INDEX IF EXISTS idx_calibration_date;

COMMIT;