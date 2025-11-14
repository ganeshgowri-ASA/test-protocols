-- Audit Log Schema
-- Database schema for comprehensive audit trail and activity logging

-- Audit Log Table
-- Comprehensive audit trail for all system activities
CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    log_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,

    -- Event identification
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'create', 'read', 'update', 'delete',
        'login', 'logout', 'authentication',
        'test_start', 'test_complete', 'test_abort',
        'approval', 'rejection', 'review',
        'export', 'import', 'configuration_change',
        'calibration', 'maintenance', 'other'
    )),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100),

    -- Related entities
    execution_id INTEGER REFERENCES test_executions(execution_id) ON DELETE SET NULL,
    protocol_id VARCHAR(50) REFERENCES test_protocols(protocol_id) ON DELETE SET NULL,

    -- User information
    user_name VARCHAR(100) NOT NULL,
    user_role VARCHAR(50),
    user_ip_address INET,
    user_agent TEXT,

    -- Action details
    action_summary VARCHAR(255) NOT NULL,
    action_details TEXT,

    -- Data changes
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],

    -- Context
    session_id VARCHAR(100),
    request_id VARCHAR(100),

    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Audit metadata
    severity VARCHAR(20) CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,

    -- Compliance
    compliance_relevant BOOLEAN DEFAULT FALSE,
    retention_years INTEGER DEFAULT 7
);

-- Create indexes for audit log
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_user ON audit_log(user_name);
CREATE INDEX idx_audit_log_event_type ON audit_log(event_type);
CREATE INDEX idx_audit_log_entity_type ON audit_log(entity_type);
CREATE INDEX idx_audit_log_entity_id ON audit_log(entity_id);
CREATE INDEX idx_audit_log_execution ON audit_log(execution_id);
CREATE INDEX idx_audit_log_protocol ON audit_log(protocol_id);
CREATE INDEX idx_audit_log_session ON audit_log(session_id);
CREATE INDEX idx_audit_log_compliance ON audit_log(compliance_relevant) WHERE compliance_relevant = TRUE;
CREATE INDEX idx_audit_log_severity ON audit_log(severity);
CREATE INDEX idx_audit_log_old_values ON audit_log USING GIN (old_values);
CREATE INDEX idx_audit_log_new_values ON audit_log USING GIN (new_values);

-- User Sessions Table
-- Tracks user login sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    user_role VARCHAR(50),

    -- Session details
    login_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    logout_timestamp TIMESTAMP WITH TIME ZONE,
    session_duration_seconds INTEGER,

    -- Connection information
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(50),

    -- Session status
    status VARCHAR(20) CHECK (status IN ('active', 'expired', 'logged_out', 'terminated')) DEFAULT 'active',
    termination_reason VARCHAR(100),

    -- Activity tracking
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activity_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_sessions_user ON user_sessions(user_name);
CREATE INDEX idx_user_sessions_status ON user_sessions(status);
CREATE INDEX idx_user_sessions_login ON user_sessions(login_timestamp);
CREATE INDEX idx_user_sessions_last_activity ON user_sessions(last_activity);

-- Data Access Log
-- Tracks access to sensitive or regulated data
CREATE TABLE IF NOT EXISTS data_access_log (
    access_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) REFERENCES user_sessions(session_id),

    -- Access details
    access_type VARCHAR(50) CHECK (access_type IN ('view', 'download', 'export', 'print', 'copy')),
    data_type VARCHAR(50),
    data_identifier VARCHAR(200),

    -- Execution context
    execution_id INTEGER REFERENCES test_executions(execution_id) ON DELETE SET NULL,

    -- Access metadata
    access_reason TEXT,
    data_classification VARCHAR(50) CHECK (data_classification IN ('public', 'internal', 'confidential', 'restricted')),

    -- Timestamp
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Context
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_data_access_user ON data_access_log(user_name);
CREATE INDEX idx_data_access_execution ON data_access_log(execution_id);
CREATE INDEX idx_data_access_timestamp ON data_access_log(accessed_at);
CREATE INDEX idx_data_access_type ON data_access_log(access_type);
CREATE INDEX idx_data_access_classification ON data_access_log(data_classification);

-- System Configuration Changes
-- Tracks changes to system configuration
CREATE TABLE IF NOT EXISTS configuration_changes (
    change_id SERIAL PRIMARY KEY,

    -- Configuration details
    config_key VARCHAR(200) NOT NULL,
    config_category VARCHAR(100),

    -- Change details
    old_value TEXT,
    new_value TEXT,
    change_type VARCHAR(50) CHECK (change_type IN ('create', 'update', 'delete')),

    -- Change metadata
    change_reason TEXT,
    impact_assessment TEXT,

    -- Approval
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP WITH TIME ZONE,

    -- User tracking
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Rollback
    can_rollback BOOLEAN DEFAULT TRUE,
    rolled_back BOOLEAN DEFAULT FALSE,
    rollback_by VARCHAR(100),
    rollback_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_config_changes_key ON configuration_changes(config_key);
CREATE INDEX idx_config_changes_category ON configuration_changes(config_category);
CREATE INDEX idx_config_changes_changed_at ON configuration_changes(changed_at);
CREATE INDEX idx_config_changes_changed_by ON configuration_changes(changed_by);

-- System Events Log
-- General system events and monitoring
CREATE TABLE IF NOT EXISTS system_events (
    event_id SERIAL PRIMARY KEY,

    -- Event details
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(50) CHECK (event_category IN ('system', 'application', 'security', 'performance', 'integration', 'error')),
    event_severity VARCHAR(20) CHECK (event_severity IN ('debug', 'info', 'warning', 'error', 'critical')) DEFAULT 'info',

    -- Event description
    event_summary VARCHAR(255) NOT NULL,
    event_details TEXT,
    event_data JSONB,

    -- Source
    source_component VARCHAR(100),
    source_function VARCHAR(100),

    -- Error tracking
    error_code VARCHAR(50),
    error_message TEXT,
    stack_trace TEXT,

    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Context
    user_name VARCHAR(100),
    session_id VARCHAR(100),
    execution_id INTEGER,

    -- Resolution
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT
);

CREATE INDEX idx_system_events_timestamp ON system_events(timestamp DESC);
CREATE INDEX idx_system_events_type ON system_events(event_type);
CREATE INDEX idx_system_events_category ON system_events(event_category);
CREATE INDEX idx_system_events_severity ON system_events(event_severity);
CREATE INDEX idx_system_events_component ON system_events(source_component);
CREATE INDEX idx_system_events_user ON system_events(user_name);
CREATE INDEX idx_system_events_resolved ON system_events(is_resolved);

-- Audit Helper Functions

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_event_type VARCHAR,
    p_entity_type VARCHAR,
    p_entity_id VARCHAR,
    p_user_name VARCHAR,
    p_action_summary VARCHAR,
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL,
    p_compliance_relevant BOOLEAN DEFAULT FALSE
)
RETURNS INTEGER AS $$
DECLARE
    v_log_id INTEGER;
    v_changed_fields TEXT[];
BEGIN
    -- Determine changed fields if both old and new values provided
    IF p_old_values IS NOT NULL AND p_new_values IS NOT NULL THEN
        SELECT ARRAY_AGG(key)
        INTO v_changed_fields
        FROM (
            SELECT key FROM jsonb_each(p_old_values)
            EXCEPT
            SELECT key FROM jsonb_each(p_new_values)
            UNION
            SELECT key FROM jsonb_each(p_new_values)
            EXCEPT
            SELECT key FROM jsonb_each(p_old_values)
        ) changed;
    END IF;

    -- Insert audit log entry
    INSERT INTO audit_log (
        event_type,
        entity_type,
        entity_id,
        user_name,
        action_summary,
        old_values,
        new_values,
        changed_fields,
        compliance_relevant
    ) VALUES (
        p_event_type,
        p_entity_type,
        p_entity_id,
        p_user_name,
        p_action_summary,
        p_old_values,
        p_new_values,
        v_changed_fields,
        p_compliance_relevant
    )
    RETURNING log_id INTO v_log_id;

    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- Audit Triggers for test_executions

-- Function to audit test_executions changes
CREATE OR REPLACE FUNCTION audit_test_executions()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        PERFORM log_audit_event(
            'create',
            'test_execution',
            NEW.execution_id::TEXT,
            NEW.operator_name,
            'Created test execution for ' || NEW.module_id,
            NULL,
            row_to_json(NEW)::JSONB,
            TRUE
        );
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        PERFORM log_audit_event(
            'update',
            'test_execution',
            NEW.execution_id::TEXT,
            COALESCE(NEW.updated_by, NEW.operator_name),
            'Updated test execution for ' || NEW.module_id,
            row_to_json(OLD)::JSONB,
            row_to_json(NEW)::JSONB,
            TRUE
        );
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        PERFORM log_audit_event(
            'delete',
            'test_execution',
            OLD.execution_id::TEXT,
            OLD.operator_name,
            'Deleted test execution for ' || OLD.module_id,
            row_to_json(OLD)::JSONB,
            NULL,
            TRUE
        );
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create audit trigger for test_executions
CREATE TRIGGER trigger_audit_test_executions
    AFTER INSERT OR UPDATE OR DELETE ON test_executions
    FOR EACH ROW EXECUTE FUNCTION audit_test_executions();

-- Views for audit reporting

-- View: Recent Audit Events
CREATE OR REPLACE VIEW recent_audit_events AS
SELECT
    log_id,
    event_type,
    entity_type,
    entity_id,
    user_name,
    action_summary,
    timestamp,
    severity,
    success
FROM audit_log
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY timestamp DESC
LIMIT 1000;

-- View: User Activity Summary
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT
    user_name,
    COUNT(*) as total_actions,
    COUNT(DISTINCT DATE(timestamp)) as active_days,
    MAX(timestamp) as last_activity,
    COUNT(CASE WHEN event_type IN ('create', 'update', 'delete') THEN 1 END) as modification_count,
    COUNT(CASE WHEN success = FALSE THEN 1 END) as failed_actions
FROM audit_log
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY user_name
ORDER BY total_actions DESC;

-- View: Compliance Audit Trail
CREATE OR REPLACE VIEW compliance_audit_trail AS
SELECT
    log_id,
    event_type,
    entity_type,
    entity_id,
    user_name,
    action_summary,
    old_values,
    new_values,
    changed_fields,
    timestamp
FROM audit_log
WHERE compliance_relevant = TRUE
ORDER BY timestamp DESC;

-- Comments for documentation
COMMENT ON TABLE audit_log IS 'Comprehensive audit trail for all system activities';
COMMENT ON TABLE user_sessions IS 'User login session tracking';
COMMENT ON TABLE data_access_log IS 'Access log for sensitive/regulated data';
COMMENT ON TABLE configuration_changes IS 'System configuration change tracking';
COMMENT ON TABLE system_events IS 'General system events and monitoring';

COMMENT ON FUNCTION log_audit_event IS 'Helper function to create audit log entries';
COMMENT ON FUNCTION audit_test_executions IS 'Audit trigger function for test_executions table';

COMMENT ON COLUMN audit_log.compliance_relevant IS 'Flag for compliance-related events requiring longer retention';
COMMENT ON COLUMN audit_log.retention_years IS 'Number of years to retain this audit record';
COMMENT ON COLUMN audit_log.changed_fields IS 'Array of field names that were modified';
