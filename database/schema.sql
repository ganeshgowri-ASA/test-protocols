-- PV Testing Protocol Framework Database Schema
-- Version: 1.0.0
-- Date: 2025-01-14

-- =============================================================================
-- PROTOCOLS TABLE
-- Stores protocol definitions and metadata
-- =============================================================================
CREATE TABLE IF NOT EXISTS protocols (
    protocol_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    standards TEXT[], -- Array of applicable standards
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author VARCHAR(255),
    tags TEXT[],
    protocol_json JSONB NOT NULL, -- Full protocol definition
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(protocol_id, version)
);

CREATE INDEX idx_protocols_category ON protocols(category);
CREATE INDEX idx_protocols_active ON protocols(is_active);

-- =============================================================================
-- TEST RUNS TABLE
-- Stores information about test run executions
-- =============================================================================
CREATE TABLE IF NOT EXISTS test_runs (
    test_run_id VARCHAR(100) PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL REFERENCES protocols(protocol_id),
    protocol_version VARCHAR(20) NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    operator VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL, -- pending, in_progress, completed, failed, paused
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    current_phase VARCHAR(50),
    current_step VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_runs_protocol ON test_runs(protocol_id);
CREATE INDEX idx_test_runs_sample ON test_runs(sample_id);
CREATE INDEX idx_test_runs_status ON test_runs(status);
CREATE INDEX idx_test_runs_start_time ON test_runs(start_time);

-- =============================================================================
-- TEST PHASES TABLE
-- Tracks execution of individual test phases
-- =============================================================================
CREATE TABLE IF NOT EXISTS test_phases (
    phase_execution_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    phase_id VARCHAR(50) NOT NULL,
    phase_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL, -- not_started, in_progress, completed, failed, skipped
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_run_id, phase_id)
);

CREATE INDEX idx_test_phases_test_run ON test_phases(test_run_id);
CREATE INDEX idx_test_phases_status ON test_phases(status);

-- =============================================================================
-- TEST STEPS TABLE
-- Tracks execution of individual test steps within phases
-- =============================================================================
CREATE TABLE IF NOT EXISTS test_steps (
    step_execution_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    phase_id VARCHAR(50) NOT NULL,
    step_id VARCHAR(50) NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    result JSONB,
    UNIQUE(test_run_id, phase_id, step_id)
);

CREATE INDEX idx_test_steps_test_run ON test_steps(test_run_id);
CREATE INDEX idx_test_steps_phase ON test_steps(phase_id);

-- =============================================================================
-- MEASUREMENTS TABLE
-- Stores all measurement data collected during tests
-- =============================================================================
CREATE TABLE IF NOT EXISTS measurements (
    measurement_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    measurement_type_id VARCHAR(50) NOT NULL, -- e.g., M1, M2 from protocol
    measurement_name VARCHAR(255) NOT NULL,
    value NUMERIC NOT NULL,
    unit VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    phase VARCHAR(50),
    step VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurements_test_run ON measurements(test_run_id);
CREATE INDEX idx_measurements_type ON measurements(measurement_type_id);
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp);
CREATE INDEX idx_measurements_phase ON measurements(phase);

-- =============================================================================
-- QC RESULTS TABLE
-- Stores quality control evaluation results
-- =============================================================================
CREATE TABLE IF NOT EXISTS qc_results (
    qc_result_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    criterion_id VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(50) NOT NULL, -- critical, major, minor
    passed BOOLEAN NOT NULL,
    condition JSONB NOT NULL,
    actual_value NUMERIC,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_run_id, criterion_id)
);

CREATE INDEX idx_qc_results_test_run ON qc_results(test_run_id);
CREATE INDEX idx_qc_results_passed ON qc_results(passed);
CREATE INDEX idx_qc_results_severity ON qc_results(severity);

-- =============================================================================
-- NOTES TABLE
-- Stores notes and comments added during test execution
-- =============================================================================
CREATE TABLE IF NOT EXISTS notes (
    note_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(50) NOT NULL, -- general, warning, error, info
    note TEXT NOT NULL,
    phase VARCHAR(50),
    step VARCHAR(50),
    author VARCHAR(255)
);

CREATE INDEX idx_notes_test_run ON notes(test_run_id);
CREATE INDEX idx_notes_category ON notes(category);
CREATE INDEX idx_notes_timestamp ON notes(timestamp);

-- =============================================================================
-- REPORTS TABLE
-- Stores generated test reports
-- =============================================================================
CREATE TABLE IF NOT EXISTS reports (
    report_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL, -- summary, detailed, compliance, custom
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(255),
    report_data JSONB NOT NULL,
    file_path VARCHAR(500),
    format VARCHAR(20) -- pdf, html, json, csv
);

CREATE INDEX idx_reports_test_run ON reports(test_run_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_generated_at ON reports(generated_at);

-- =============================================================================
-- SAMPLES TABLE
-- Stores information about test samples (modules, junction boxes, etc.)
-- =============================================================================
CREATE TABLE IF NOT EXISTS samples (
    sample_id VARCHAR(100) PRIMARY KEY,
    sample_type VARCHAR(50) NOT NULL, -- module, junction_box, cell, etc.
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    batch_number VARCHAR(255),
    manufacturing_date DATE,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_type ON samples(sample_type);
CREATE INDEX idx_samples_manufacturer ON samples(manufacturer);

-- =============================================================================
-- OPERATORS TABLE
-- Stores information about test operators
-- =============================================================================
CREATE TABLE IF NOT EXISTS operators (
    operator_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255),
    certification_level VARCHAR(50),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operators_name ON operators(name);
CREATE INDEX idx_operators_active ON operators(active);

-- =============================================================================
-- EQUIPMENT TABLE
-- Stores information about test equipment
-- =============================================================================
CREATE TABLE IF NOT EXISTS equipment (
    equipment_id VARCHAR(100) PRIMARY KEY,
    equipment_type VARCHAR(100) NOT NULL, -- IV_CURVE_TRACER, THERMAL_CHAMBER, etc.
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    calibration_date DATE,
    calibration_due_date DATE,
    status VARCHAR(50) DEFAULT 'available', -- available, in_use, maintenance, retired
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_status ON equipment(status);

-- =============================================================================
-- TEST_RUN_EQUIPMENT TABLE
-- Links test runs to equipment used
-- =============================================================================
CREATE TABLE IF NOT EXISTS test_run_equipment (
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    equipment_id VARCHAR(100) NOT NULL REFERENCES equipment(equipment_id),
    used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (test_run_id, equipment_id)
);

-- =============================================================================
-- AUDIT LOG TABLE
-- Tracks all changes to critical data
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_record ON audit_log(record_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(changed_at);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Active test runs summary
CREATE OR REPLACE VIEW active_test_runs AS
SELECT
    tr.test_run_id,
    tr.protocol_id,
    p.name AS protocol_name,
    tr.sample_id,
    tr.operator,
    tr.status,
    tr.start_time,
    tr.current_phase,
    COUNT(DISTINCT tp.phase_id) AS phases_completed,
    COUNT(DISTINCT m.measurement_id) AS measurements_count
FROM test_runs tr
LEFT JOIN protocols p ON tr.protocol_id = p.protocol_id
LEFT JOIN test_phases tp ON tr.test_run_id = tp.test_run_id AND tp.status = 'completed'
LEFT JOIN measurements m ON tr.test_run_id = m.test_run_id
WHERE tr.status IN ('in_progress', 'pending')
GROUP BY tr.test_run_id, p.name;

-- Test run summary with QC results
CREATE OR REPLACE VIEW test_run_summary AS
SELECT
    tr.test_run_id,
    tr.protocol_id,
    p.name AS protocol_name,
    tr.sample_id,
    tr.operator,
    tr.status,
    tr.start_time,
    tr.end_time,
    EXTRACT(EPOCH FROM (tr.end_time - tr.start_time))/3600 AS duration_hours,
    COUNT(DISTINCT qc.qc_result_id) AS total_qc_criteria,
    COUNT(DISTINCT CASE WHEN qc.passed = TRUE THEN qc.qc_result_id END) AS qc_passed,
    COUNT(DISTINCT CASE WHEN qc.passed = FALSE AND qc.severity = 'critical' THEN qc.qc_result_id END) AS critical_failures,
    COUNT(DISTINCT CASE WHEN qc.passed = FALSE AND qc.severity = 'major' THEN qc.qc_result_id END) AS major_failures,
    COUNT(DISTINCT CASE WHEN qc.passed = FALSE AND qc.severity = 'minor' THEN qc.qc_result_id END) AS minor_failures
FROM test_runs tr
LEFT JOIN protocols p ON tr.protocol_id = p.protocol_id
LEFT JOIN qc_results qc ON tr.test_run_id = qc.test_run_id
GROUP BY tr.test_run_id, p.name;

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for test_runs
CREATE TRIGGER update_test_runs_updated_at
    BEFORE UPDATE ON test_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for samples
CREATE TRIGGER update_samples_updated_at
    BEFORE UPDATE ON samples
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- SAMPLE DATA (for development/testing)
-- =============================================================================

-- Insert sample protocol
INSERT INTO protocols (protocol_id, name, version, category, description, author, protocol_json)
VALUES (
    'JBOX-001',
    'Junction Box Degradation Test',
    '1.0.0',
    'Degradation',
    'Comprehensive junction box degradation testing protocol',
    'PV Testing Framework',
    '{}'::jsonb
) ON CONFLICT DO NOTHING;

COMMENT ON TABLE protocols IS 'Stores test protocol definitions and metadata';
COMMENT ON TABLE test_runs IS 'Stores information about test run executions';
COMMENT ON TABLE measurements IS 'Stores all measurement data collected during tests';
COMMENT ON TABLE qc_results IS 'Stores quality control evaluation results';
COMMENT ON TABLE notes IS 'Stores notes and comments added during test execution';
COMMENT ON TABLE reports IS 'Stores generated test reports';
