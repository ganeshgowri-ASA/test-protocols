-- =================================================================
-- Migration 006: Audit Trail Enhancement - UP Migration
-- Description: Add comprehensive audit logging fields
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Add additional columns to audit_logs table
DO $$
BEGIN
    -- Add entity_type for categorization
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'entity_type') THEN
        ALTER TABLE audit_logs ADD COLUMN entity_type VARCHAR(50);
    END IF;

    -- Add action_category for grouping actions
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'action_category') THEN
        ALTER TABLE audit_logs ADD COLUMN action_category VARCHAR(50);
    END IF;

    -- Add severity_level for importance classification
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'severity_level') THEN
        ALTER TABLE audit_logs ADD COLUMN severity_level VARCHAR(20) DEFAULT 'info';
    END IF;

    -- Add request_id for tracing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'request_id') THEN
        ALTER TABLE audit_logs ADD COLUMN request_id VARCHAR(100);
    END IF;

    -- Add correlation_id for linking related events
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'correlation_id') THEN
        ALTER TABLE audit_logs ADD COLUMN correlation_id VARCHAR(100);
    END IF;

    -- Add duration_ms for performance tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'duration_ms') THEN
        ALTER TABLE audit_logs ADD COLUMN duration_ms INTEGER;
    END IF;

    -- Add success flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'success') THEN
        ALTER TABLE audit_logs ADD COLUMN success BOOLEAN DEFAULT TRUE;
    END IF;

    -- Add error_message for failures
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'error_message') THEN
        ALTER TABLE audit_logs ADD COLUMN error_message TEXT;
    END IF;

    -- Add stack_trace for debugging
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'stack_trace') THEN
        ALTER TABLE audit_logs ADD COLUMN stack_trace TEXT;
    END IF;

    -- Add affected_fields for specific field tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'affected_fields') THEN
        ALTER TABLE audit_logs ADD COLUMN affected_fields JSONB;
    END IF;

    -- Add metadata for additional context
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'metadata') THEN
        ALTER TABLE audit_logs ADD COLUMN metadata JSONB;
    END IF;

    -- Add geo_location for location tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'geo_location') THEN
        ALTER TABLE audit_logs ADD COLUMN geo_location VARCHAR(100);
    END IF;

    -- Add device_info
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'audit_logs' AND column_name = 'device_info') THEN
        ALTER TABLE audit_logs ADD COLUMN device_info VARCHAR(200);
    END IF;
END $$;

-- Create login_history table for security tracking
CREATE TABLE IF NOT EXISTS login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    username VARCHAR(50),
    login_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_timestamp TIMESTAMP,
    session_duration_minutes INTEGER,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    location VARCHAR(100),
    success BOOLEAN DEFAULT TRUE,
    failure_reason VARCHAR(200),
    mfa_used BOOLEAN DEFAULT FALSE,
    session_token VARCHAR(255)
);

-- Create security_events table for security-related events
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- login_failed, password_changed, permission_denied, etc.
    severity VARCHAR(20) NOT NULL DEFAULT 'medium', -- low, medium, high, critical
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    username VARCHAR(50),
    ip_address VARCHAR(50),
    description TEXT NOT NULL,
    details JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by_id INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create data_change_log table for detailed field-level changes
CREATE TABLE IF NOT EXISTS data_change_log (
    id SERIAL PRIMARY KEY,
    audit_log_id INTEGER REFERENCES audit_logs(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    data_type VARCHAR(50),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit_retention_policy table
CREATE TABLE IF NOT EXISTS audit_retention_policy (
    id SERIAL PRIMARY KEY,
    policy_name VARCHAR(100) UNIQUE NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    retention_days INTEGER NOT NULL DEFAULT 365,
    archive_before_delete BOOLEAN DEFAULT TRUE,
    archive_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_cleanup_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_category ON audit_logs(action_category);
CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON audit_logs(severity_level);
CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation ON audit_logs(correlation_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON audit_logs(success);
CREATE INDEX IF NOT EXISTS idx_login_history_user ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_timestamp ON login_history(login_timestamp);
CREATE INDEX IF NOT EXISTS idx_login_history_ip ON login_history(ip_address);
CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);
CREATE INDEX IF NOT EXISTS idx_security_events_user ON security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_created ON security_events(created_at);
CREATE INDEX IF NOT EXISTS idx_data_change_log_audit ON data_change_log(audit_log_id);
CREATE INDEX IF NOT EXISTS idx_data_change_log_table ON data_change_log(table_name, record_id);

-- Insert default retention policies
INSERT INTO audit_retention_policy (policy_name, table_name, retention_days, archive_before_delete) VALUES
    ('audit_logs_policy', 'audit_logs', 730, TRUE),
    ('login_history_policy', 'login_history', 365, TRUE),
    ('security_events_policy', 'security_events', 1095, TRUE),
    ('data_change_log_policy', 'data_change_log', 365, TRUE)
ON CONFLICT (policy_name) DO NOTHING;

-- Create function to log security events
CREATE OR REPLACE FUNCTION log_security_event(
    p_event_type VARCHAR,
    p_severity VARCHAR,
    p_user_id INTEGER,
    p_description TEXT,
    p_ip_address VARCHAR DEFAULT NULL,
    p_details JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_event_id INTEGER;
BEGIN
    INSERT INTO security_events (event_type, severity, user_id, ip_address, description, details)
    VALUES (p_event_type, p_severity, p_user_id, p_ip_address, p_description, p_details)
    RETURNING id INTO v_event_id;

    RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;

COMMIT;
