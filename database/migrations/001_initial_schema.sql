-- Migration: 001_initial_schema.sql
-- Description: Initial database schema for Test Protocols Framework
-- Author: Test Protocol Team
-- Date: 2025-11-14
-- Version: 1.0.0

-- This migration creates all tables, indexes, functions, triggers, and views
-- for the Test Protocols Framework including DIEL-001 support

BEGIN;

-- Set transaction isolation level
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Create schema version table
CREATE TABLE IF NOT EXISTS schema_versions (
    version_id SERIAL PRIMARY KEY,
    version_number VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100),
    checksum VARCHAR(64)
);

-- Record this migration
INSERT INTO schema_versions (version_number, description, applied_by)
VALUES ('001', 'Initial database schema', CURRENT_USER);

-- Load all schema files in order
\echo 'Creating test protocols schema...'
\i ../schemas/test_protocols.sql

\echo 'Creating test results schema...'
\i ../schemas/test_results.sql

\echo 'Creating quality checks schema...'
\i ../schemas/quality_checks.sql

\echo 'Creating audit log schema...'
\i ../schemas/audit_log.sql

-- Create additional helper functions

-- Function to get execution summary
CREATE OR REPLACE FUNCTION get_execution_summary(p_execution_id INTEGER)
RETURNS TABLE (
    execution_id INTEGER,
    protocol_name VARCHAR,
    module_id VARCHAR,
    test_date DATE,
    operator_name VARCHAR,
    status VARCHAR,
    result VARCHAR,
    total_measurements BIGINT,
    passed_qc_checks BIGINT,
    failed_qc_checks BIGINT,
    critical_failures BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.execution_id,
        p.protocol_name,
        e.module_id,
        e.test_date,
        e.operator_name,
        e.status,
        e.result,
        (SELECT COUNT(*) FROM measurements m WHERE m.execution_id = e.execution_id),
        (SELECT COUNT(*) FROM quality_checks q WHERE q.execution_id = e.execution_id AND q.result = 'pass'),
        (SELECT COUNT(*) FROM quality_checks q WHERE q.execution_id = e.execution_id AND q.result = 'fail'),
        (SELECT COUNT(*) FROM quality_checks q WHERE q.execution_id = e.execution_id AND q.result = 'fail' AND q.is_critical = TRUE)
    FROM test_executions e
    LEFT JOIN test_protocols p ON e.protocol_id = p.protocol_id
    WHERE e.execution_id = p_execution_id;
END;
$$ LANGUAGE plpgsql;

-- Function to check equipment calibration status
CREATE OR REPLACE FUNCTION check_equipment_calibration(p_equipment_id VARCHAR)
RETURNS TABLE (
    equipment_id VARCHAR,
    equipment_name VARCHAR,
    calibration_status VARCHAR,
    days_until_due INTEGER,
    is_overdue BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.equipment_id,
        e.equipment_name,
        CASE
            WHEN e.calibration_required = FALSE THEN 'not_required'
            WHEN e.next_calibration_date IS NULL THEN 'unknown'
            WHEN e.next_calibration_date < CURRENT_DATE THEN 'overdue'
            WHEN e.next_calibration_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'due_soon'
            ELSE 'current'
        END::VARCHAR,
        (e.next_calibration_date - CURRENT_DATE)::INTEGER,
        (e.calibration_required AND e.next_calibration_date < CURRENT_DATE)
    FROM equipment e
    WHERE e.equipment_id = p_equipment_id;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate test pass rate
CREATE OR REPLACE FUNCTION calculate_pass_rate(
    p_protocol_id VARCHAR DEFAULT NULL,
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL
)
RETURNS TABLE (
    protocol_id VARCHAR,
    protocol_name VARCHAR,
    total_tests BIGINT,
    passed BIGINT,
    failed BIGINT,
    pass_rate_pct NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.protocol_id,
        p.protocol_name,
        COUNT(*)::BIGINT as total_tests,
        COUNT(CASE WHEN e.result = 'pass' THEN 1 END)::BIGINT as passed,
        COUNT(CASE WHEN e.result = 'fail' THEN 1 END)::BIGINT as failed,
        ROUND(100.0 * COUNT(CASE WHEN e.result = 'pass' THEN 1 END) / NULLIF(COUNT(*), 0), 2) as pass_rate_pct
    FROM test_executions e
    LEFT JOIN test_protocols p ON e.protocol_id = p.protocol_id
    WHERE e.status = 'completed'
        AND (p_protocol_id IS NULL OR e.protocol_id = p_protocol_id)
        AND (p_start_date IS NULL OR e.test_date >= p_start_date)
        AND (p_end_date IS NULL OR e.test_date <= p_end_date)
    GROUP BY e.protocol_id, p.protocol_name;
END;
$$ LANGUAGE plpgsql;

-- Create materialized view for dashboard statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_statistics AS
SELECT
    (SELECT COUNT(*) FROM test_protocols WHERE is_active = TRUE) as active_protocols,
    (SELECT COUNT(*) FROM test_executions WHERE status = 'in_progress') as tests_in_progress,
    (SELECT COUNT(*) FROM test_executions WHERE test_date = CURRENT_DATE) as tests_today,
    (SELECT COUNT(*) FROM test_executions WHERE status = 'completed' AND test_date >= CURRENT_DATE - INTERVAL '7 days') as tests_this_week,
    (SELECT COUNT(*) FROM test_executions WHERE status = 'completed' AND test_date >= CURRENT_DATE - INTERVAL '30 days') as tests_this_month,
    (SELECT COUNT(*) FROM equipment WHERE status = 'active') as active_equipment,
    (SELECT COUNT(*) FROM equipment WHERE calibration_required = TRUE AND next_calibration_date < CURRENT_DATE) as overdue_calibrations,
    (SELECT COUNT(*) FROM non_conformance_reports WHERE status NOT IN ('closed', 'cancelled')) as open_ncrs,
    (SELECT COUNT(*) FROM quality_checks WHERE result = 'fail' AND is_critical = TRUE AND checked_at >= CURRENT_DATE - INTERVAL '7 days') as critical_failures_week,
    CURRENT_TIMESTAMP as last_updated;

CREATE UNIQUE INDEX ON dashboard_statistics ((TRUE));

-- Create refresh function for dashboard statistics
CREATE OR REPLACE FUNCTION refresh_dashboard_statistics()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_statistics;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your environment)
-- These are example grants - modify based on your user roles

-- Create roles if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'test_operator') THEN
        CREATE ROLE test_operator;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'test_supervisor') THEN
        CREATE ROLE test_supervisor;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'test_admin') THEN
        CREATE ROLE test_admin;
    END IF;
END
$$;

-- Grant basic read access to operators
GRANT SELECT ON ALL TABLES IN SCHEMA public TO test_operator;
GRANT INSERT, UPDATE ON test_executions, measurements, time_series_data, test_comments TO test_operator;

-- Grant more permissions to supervisors
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO test_supervisor;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO test_supervisor;

-- Grant full access to admins
GRANT ALL ON ALL TABLES IN SCHEMA public TO test_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO test_admin;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO test_admin;

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_test_executions_composite ON test_executions(protocol_id, test_date, status, result);
CREATE INDEX IF NOT EXISTS idx_measurements_composite ON measurements(execution_id, measurement_name, is_valid);
CREATE INDEX IF NOT EXISTS idx_quality_checks_composite ON quality_checks(execution_id, result, is_critical);

-- Add table statistics collection
ANALYZE test_protocols;
ANALYZE test_executions;
ANALYZE measurements;
ANALYZE quality_checks;
ANALYZE equipment;
ANALYZE audit_log;

-- Create maintenance procedures

-- Function to archive old audit logs
CREATE OR REPLACE FUNCTION archive_old_audit_logs(p_retention_years INTEGER DEFAULT 7)
RETURNS INTEGER AS $$
DECLARE
    v_archived_count INTEGER;
    v_cutoff_date TIMESTAMP;
BEGIN
    v_cutoff_date := CURRENT_TIMESTAMP - (p_retention_years || ' years')::INTERVAL;

    WITH archived AS (
        DELETE FROM audit_log
        WHERE timestamp < v_cutoff_date
        AND compliance_relevant = FALSE
        RETURNING *
    )
    SELECT COUNT(*) INTO v_archived_count FROM archived;

    RETURN v_archived_count;
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup incomplete test executions
CREATE OR REPLACE FUNCTION cleanup_incomplete_tests(p_days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    v_cleaned_count INTEGER;
BEGIN
    WITH cleaned AS (
        UPDATE test_executions
        SET status = 'invalid',
            notes = COALESCE(notes || ' | ', '') || 'Automatically marked invalid due to incomplete status after ' || p_days_old || ' days'
        WHERE status IN ('pending', 'in_progress')
        AND test_date < CURRENT_DATE - p_days_old
        RETURNING *
    )
    SELECT COUNT(*) INTO v_cleaned_count FROM cleaned;

    RETURN v_cleaned_count;
END;
$$ LANGUAGE plpgsql;

-- Add comments
COMMENT ON FUNCTION get_execution_summary IS 'Get comprehensive summary of a test execution';
COMMENT ON FUNCTION check_equipment_calibration IS 'Check calibration status for equipment';
COMMENT ON FUNCTION calculate_pass_rate IS 'Calculate test pass rate for protocols within date range';
COMMENT ON FUNCTION refresh_dashboard_statistics IS 'Refresh materialized view for dashboard';
COMMENT ON FUNCTION archive_old_audit_logs IS 'Archive audit logs older than retention period';
COMMENT ON FUNCTION cleanup_incomplete_tests IS 'Mark old incomplete tests as invalid';

-- Success message
\echo ''
\echo '========================================'
\echo 'Migration 001 completed successfully!'
\echo '========================================'
\echo ''
\echo 'Created:'
\echo '  - Test protocols tables and indexes'
\echo '  - Test results tables and indexes'
\echo '  - Quality checks tables and indexes'
\echo '  - Audit log tables and indexes'
\echo '  - Helper functions and views'
\echo '  - Dashboard statistics materialized view'
\echo '  - User roles and permissions'
\echo ''
\echo 'Next steps:'
\echo '  1. Load initial protocol data'
\echo '  2. Configure equipment records'
\echo '  3. Set up user accounts'
\echo '========================================'

COMMIT;
