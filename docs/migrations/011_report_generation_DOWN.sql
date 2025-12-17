-- =================================================================
-- Migration 011: Report Generation - DOWN Migration
-- Description: Rollback report templates and generation history
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop triggers and functions
DROP TRIGGER IF EXISTS report_templates_update_timestamp ON report_templates;
DROP FUNCTION IF EXISTS update_report_templates_timestamp() CASCADE;
DROP FUNCTION IF EXISTS generate_report_number(VARCHAR) CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_report_audit_trail_report;
DROP INDEX IF EXISTS idx_report_comments_report;
DROP INDEX IF EXISTS idx_report_signatures_report;
DROP INDEX IF EXISTS idx_report_distribution_log_report;
DROP INDEX IF EXISTS idx_report_sections_code;
DROP INDEX IF EXISTS idx_scheduled_reports_next_run;
DROP INDEX IF EXISTS idx_scheduled_reports_active;
DROP INDEX IF EXISTS idx_scheduled_reports_id;
DROP INDEX IF EXISTS idx_generated_reports_generated;
DROP INDEX IF EXISTS idx_generated_reports_template;
DROP INDEX IF EXISTS idx_generated_reports_status;
DROP INDEX IF EXISTS idx_generated_reports_number;
DROP INDEX IF EXISTS idx_generated_reports_id;
DROP INDEX IF EXISTS idx_report_templates_active;
DROP INDEX IF EXISTS idx_report_templates_type;
DROP INDEX IF EXISTS idx_report_templates_id;

-- Drop tables
DROP TABLE IF EXISTS report_audit_trail CASCADE;
DROP TABLE IF EXISTS report_comments CASCADE;
DROP TABLE IF EXISTS report_signatures CASCADE;
DROP TABLE IF EXISTS report_distribution_log CASCADE;
DROP TABLE IF EXISTS report_sections CASCADE;
DROP TABLE IF EXISTS scheduled_reports CASCADE;
DROP TABLE IF EXISTS generated_reports CASCADE;
DROP TABLE IF EXISTS report_templates CASCADE;

COMMIT;
