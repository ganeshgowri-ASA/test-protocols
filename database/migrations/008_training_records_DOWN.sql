-- =================================================================
-- Migration 008: Training Records - DOWN Migration
-- Description: Rollback staff training and certification tracking
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop triggers and functions
DROP TRIGGER IF EXISTS staff_training_records_update_timestamp ON staff_training_records;
DROP TRIGGER IF EXISTS staff_training_update_timestamp ON staff_training;
DROP FUNCTION IF EXISTS update_staff_training_timestamp() CASCADE;
DROP FUNCTION IF EXISTS check_training_expiry() CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_user_competencies_status;
DROP INDEX IF EXISTS idx_user_competencies_competency;
DROP INDEX IF EXISTS idx_user_competencies_user;
DROP INDEX IF EXISTS idx_training_competencies_code;
DROP INDEX IF EXISTS idx_training_attendance_user;
DROP INDEX IF EXISTS idx_training_attendance_session;
DROP INDEX IF EXISTS idx_training_sessions_status;
DROP INDEX IF EXISTS idx_training_sessions_date;
DROP INDEX IF EXISTS idx_training_sessions_training;
DROP INDEX IF EXISTS idx_staff_training_records_expiry;
DROP INDEX IF EXISTS idx_staff_training_records_status;
DROP INDEX IF EXISTS idx_staff_training_records_user;
DROP INDEX IF EXISTS idx_staff_training_records_training;
DROP INDEX IF EXISTS idx_staff_training_active;
DROP INDEX IF EXISTS idx_staff_training_category;
DROP INDEX IF EXISTS idx_staff_training_id;

-- Drop tables
DROP TABLE IF EXISTS user_competencies CASCADE;
DROP TABLE IF EXISTS training_competencies CASCADE;
DROP TABLE IF EXISTS training_attendance CASCADE;
DROP TABLE IF EXISTS training_sessions CASCADE;
DROP TABLE IF EXISTS staff_training_records CASCADE;
DROP TABLE IF EXISTS staff_training CASCADE;

COMMIT;
