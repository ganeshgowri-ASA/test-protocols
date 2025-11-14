-- Test Protocols Database Schema
-- Version: 1.0.0
-- Description: Database schema for PV testing protocol framework

-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- PROTOCOLS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS protocols (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('draft', 'active', 'deprecated', 'archived')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    CONSTRAINT unique_protocol_version UNIQUE (protocol_id, version)
);

CREATE INDEX idx_protocols_category ON protocols(category);
CREATE INDEX idx_protocols_status ON protocols(status);
CREATE INDEX idx_protocols_protocol_id ON protocols(protocol_id);

COMMENT ON TABLE protocols IS 'Test protocol definitions and metadata';
COMMENT ON COLUMN protocols.definition IS 'Full JSON protocol definition';

-- ============================================================================
-- TEST SESSIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS test_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    protocol_id VARCHAR(50) NOT NULL REFERENCES protocols(protocol_id),
    protocol_version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('planned', 'in_progress', 'completed', 'cancelled', 'failed')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    started_by VARCHAR(100) NOT NULL,
    sample_ids TEXT[],
    equipment_ids TEXT[],
    notes TEXT,
    metadata JSONB,
    CONSTRAINT valid_completion CHECK (
        (status = 'completed' AND completed_at IS NOT NULL) OR
        (status != 'completed')
    )
);

CREATE INDEX idx_test_sessions_protocol ON test_sessions(protocol_id);
CREATE INDEX idx_test_sessions_status ON test_sessions(status);
CREATE INDEX idx_test_sessions_started_at ON test_sessions(started_at);
CREATE INDEX idx_test_sessions_started_by ON test_sessions(started_by);

COMMENT ON TABLE test_sessions IS 'Test execution sessions';

-- ============================================================================
-- TEST RESULTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    result_id UUID DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    step_id VARCHAR(50) NOT NULL,
    step_name VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    measurements JSONB NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pass', 'warning', 'fail')),
    operator VARCHAR(100) NOT NULL,
    notes TEXT,
    raw_data_path VARCHAR(500),
    CONSTRAINT unique_session_step UNIQUE (session_id, step_id, timestamp)
);

CREATE INDEX idx_test_results_session ON test_results(session_id);
CREATE INDEX idx_test_results_step ON test_results(step_id);
CREATE INDEX idx_test_results_timestamp ON test_results(timestamp);
CREATE INDEX idx_test_results_status ON test_results(status);
CREATE INDEX idx_test_results_measurements ON test_results USING GIN (measurements);

COMMENT ON TABLE test_results IS 'Individual step execution results';
COMMENT ON COLUMN test_results.measurements IS 'JSONB containing all measurement data';

-- ============================================================================
-- CALCULATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS calculations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    calculation_name VARCHAR(100) NOT NULL,
    result_value NUMERIC,
    unit VARCHAR(50),
    formula TEXT,
    variables JSONB,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculated_by VARCHAR(100),
    CONSTRAINT unique_session_calculation UNIQUE (session_id, calculation_name)
);

CREATE INDEX idx_calculations_session ON calculations(session_id);
CREATE INDEX idx_calculations_name ON calculations(calculation_name);

COMMENT ON TABLE calculations IS 'Derived calculations from test results';

-- ============================================================================
-- EVALUATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    overall_pass BOOLEAN NOT NULL,
    criteria_results JSONB NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evaluated_by VARCHAR(100),
    comments TEXT,
    CONSTRAINT one_evaluation_per_session UNIQUE (session_id)
);

CREATE INDEX idx_evaluations_session ON evaluations(session_id);
CREATE INDEX idx_evaluations_overall_pass ON evaluations(overall_pass);

COMMENT ON TABLE evaluations IS 'Pass/fail evaluations for test sessions';

-- ============================================================================
-- EQUIPMENT TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS equipment (
    id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    equipment_type VARCHAR(100),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    specifications JSONB,
    calibration_required BOOLEAN DEFAULT false,
    calibration_interval_days INTEGER,
    last_calibration_date DATE,
    next_calibration_date DATE,
    calibration_certificate VARCHAR(500),
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'in_use', 'maintenance', 'calibration', 'decommissioned')),
    location VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_next_calibration ON equipment(next_calibration_date);

COMMENT ON TABLE equipment IS 'Test equipment inventory and calibration tracking';

-- ============================================================================
-- SAMPLES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS samples (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(100) UNIQUE NOT NULL,
    sample_type VARCHAR(100),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    description TEXT,
    specifications JSONB,
    received_date DATE,
    received_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'in_test', 'tested', 'failed', 'discarded')),
    location VARCHAR(255),
    storage_conditions VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_status ON samples(status);
CREATE INDEX idx_samples_type ON samples(sample_type);
CREATE INDEX idx_samples_received_date ON samples(received_date);

COMMENT ON TABLE samples IS 'Test sample inventory and tracking';

-- ============================================================================
-- ATTACHMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS attachments (
    id SERIAL PRIMARY KEY,
    attachment_id UUID DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    step_id VARCHAR(50),
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    description TEXT,
    category VARCHAR(50) CHECK (category IN ('image', 'document', 'data', 'report', 'other')),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100)
);

CREATE INDEX idx_attachments_session ON attachments(session_id);
CREATE INDEX idx_attachments_step ON attachments(step_id);
CREATE INDEX idx_attachments_category ON attachments(category);
CREATE INDEX idx_attachments_uploaded_at ON attachments(uploaded_at);

COMMENT ON TABLE attachments IS 'File attachments for test sessions (images, documents, etc.)';

-- ============================================================================
-- AUDIT LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'approve', 'archive')),
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at);
CREATE INDEX idx_audit_log_changed_by ON audit_log(changed_by);

COMMENT ON TABLE audit_log IS 'Audit trail for all data changes';

-- ============================================================================
-- USERS TABLE (Optional - for authentication)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) CHECK (role IN ('admin', 'engineer', 'technician', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

COMMENT ON TABLE users IS 'User accounts for access control';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Active test sessions view
CREATE OR REPLACE VIEW v_active_sessions AS
SELECT
    ts.session_id,
    ts.protocol_id,
    p.name AS protocol_name,
    ts.status,
    ts.started_at,
    ts.started_by,
    COUNT(DISTINCT tr.id) AS completed_steps,
    array_length(ts.sample_ids, 1) AS sample_count
FROM test_sessions ts
LEFT JOIN protocols p ON ts.protocol_id = p.protocol_id
LEFT JOIN test_results tr ON ts.session_id = tr.session_id
WHERE ts.status IN ('in_progress', 'planned')
GROUP BY ts.session_id, ts.protocol_id, p.name, ts.status, ts.started_at, ts.started_by;

-- Equipment calibration status view
CREATE OR REPLACE VIEW v_equipment_calibration_status AS
SELECT
    equipment_id,
    name,
    equipment_type,
    last_calibration_date,
    next_calibration_date,
    CASE
        WHEN next_calibration_date < CURRENT_DATE THEN 'OVERDUE'
        WHEN next_calibration_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'DUE_SOON'
        ELSE 'CURRENT'
    END AS calibration_status,
    status
FROM equipment
WHERE calibration_required = true;

-- Test session summary view
CREATE OR REPLACE VIEW v_session_summary AS
SELECT
    ts.session_id,
    ts.protocol_id,
    p.name AS protocol_name,
    p.category,
    ts.status,
    ts.started_at,
    ts.completed_at,
    ts.started_by,
    COUNT(DISTINCT tr.id) AS total_steps,
    SUM(CASE WHEN tr.status = 'pass' THEN 1 ELSE 0 END) AS passed_steps,
    SUM(CASE WHEN tr.status = 'warning' THEN 1 ELSE 0 END) AS warning_steps,
    SUM(CASE WHEN tr.status = 'fail' THEN 1 ELSE 0 END) AS failed_steps,
    e.overall_pass
FROM test_sessions ts
LEFT JOIN protocols p ON ts.protocol_id = p.protocol_id
LEFT JOIN test_results tr ON ts.session_id = tr.session_id
LEFT JOIN evaluations e ON ts.session_id = e.session_id
GROUP BY ts.session_id, ts.protocol_id, p.name, p.category, ts.status,
         ts.started_at, ts.completed_at, ts.started_by, e.overall_pass;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to relevant tables
CREATE TRIGGER update_protocols_timestamp
    BEFORE UPDATE ON protocols
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equipment_timestamp
    BEFORE UPDATE ON equipment
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_samples_timestamp
    BEFORE UPDATE ON samples
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Audit log trigger function
CREATE OR REPLACE FUNCTION log_audit_trail()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (entity_type, entity_id, action, changed_by, old_values)
        VALUES (TG_TABLE_NAME, OLD.id::text, 'delete', current_user, row_to_json(OLD));
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (entity_type, entity_id, action, changed_by, old_values, new_values)
        VALUES (TG_TABLE_NAME, NEW.id::text, 'update', current_user, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (entity_type, entity_id, action, changed_by, new_values)
        VALUES (TG_TABLE_NAME, NEW.id::text, 'create', current_user, row_to_json(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA FOR SEAL-001
-- ============================================================================

-- Insert SEAL-001 protocol
INSERT INTO protocols (protocol_id, name, version, category, description, definition, status, created_by)
VALUES (
    'SEAL-001',
    'Edge Seal Degradation Protocol',
    '1.0.0',
    'degradation',
    'Accelerated aging test protocol for evaluating PV module edge seal integrity under combined thermal and humidity stress.',
    '{}'::jsonb,  -- Would contain full JSON definition
    'active',
    'System'
) ON CONFLICT (protocol_id, version) DO NOTHING;

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO test_protocol_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO test_protocol_user;
