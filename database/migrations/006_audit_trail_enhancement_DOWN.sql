-- =================================================================
-- Migration 006: Audit Trail Enhancement - DOWN Migration
-- Description: Rollback comprehensive audit logging fields
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop functions
DROP FUNCTION IF EXISTS log_security_event(VARCHAR, VARCHAR, INTEGER, TEXT, VARCHAR, JSONB) CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_data_change_log_table;
DROP INDEX IF EXISTS idx_data_change_log_audit;
DROP INDEX IF EXISTS idx_security_events_created;
DROP INDEX IF EXISTS idx_security_events_user;
DROP INDEX IF EXISTS idx_security_events_severity;
DROP INDEX IF EXISTS idx_security_events_type;
DROP INDEX IF EXISTS idx_login_history_ip;
DROP INDEX IF EXISTS idx_login_history_timestamp;
DROP INDEX IF EXISTS idx_login_history_user;
DROP INDEX IF EXISTS idx_audit_logs_success;
DROP INDEX IF EXISTS idx_audit_logs_correlation;
DROP INDEX IF EXISTS idx_audit_logs_severity;
DROP INDEX IF EXISTS idx_audit_logs_action_category;
DROP INDEX IF EXISTS idx_audit_logs_entity_type;

-- Drop tables
DROP TABLE IF EXISTS audit_retention_policy CASCADE;
DROP TABLE IF EXISTS data_change_log CASCADE;
DROP TABLE IF EXISTS security_events CASCADE;
DROP TABLE IF EXISTS login_history CASCADE;

-- Remove columns from audit_logs table
ALTER TABLE audit_logs DROP COLUMN IF EXISTS device_info;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS geo_location;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS metadata;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS affected_fields;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS stack_trace;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS error_message;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS success;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS duration_ms;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS correlation_id;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS request_id;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS severity_level;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS action_category;
ALTER TABLE audit_logs DROP COLUMN IF EXISTS entity_type;

COMMIT;
