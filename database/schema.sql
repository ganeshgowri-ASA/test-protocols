-- Test Protocols Database Schema
-- PostgreSQL schema for production deployment

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    id VARCHAR(50) PRIMARY KEY,
    protocol_number VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    version VARCHAR(20) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',

    -- JSON fields
    definition JSONB NOT NULL,
    test_parameters JSONB,
    test_procedure JSONB,
    qc_checks JSONB,
    pass_fail_criteria JSONB,

    -- Metadata
    author VARCHAR(100),
    standard_references JSONB,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT protocols_status_check CHECK (status IN ('active', 'draft', 'deprecated'))
);

CREATE INDEX idx_protocols_category ON protocols(category);
CREATE INDEX idx_protocols_protocol_number ON protocols(protocol_number);
CREATE INDEX idx_protocols_status ON protocols(status);

-- Test runs table
CREATE TABLE IF NOT EXISTS test_runs (
    id VARCHAR(50) PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL REFERENCES protocols(id) ON DELETE CASCADE,

    -- Test identification
    module_serial_number VARCHAR(100),
    batch_id VARCHAR(100),
    operator VARCHAR(100),

    -- Execution details
    status VARCHAR(20) DEFAULT 'pending',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,

    -- Test parameters
    parameters JSONB,

    -- Progress tracking
    current_cycle INTEGER DEFAULT 0,
    total_cycles INTEGER,
    current_phase VARCHAR(50),

    -- Results
    results_summary JSONB,
    pass_fail_status BOOLEAN,
    failure_reason TEXT,

    -- Environmental conditions
    ambient_temperature NUMERIC(5,2),
    ambient_humidity NUMERIC(5,2),
    ambient_pressure NUMERIC(6,2),

    -- Equipment
    chamber_id VARCHAR(100),
    equipment_info JSONB,

    -- Integration
    lims_reference VARCHAR(100),
    qms_reference VARCHAR(100),
    project_reference VARCHAR(100),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    -- Constraints
    CONSTRAINT test_runs_status_check CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed', 'aborted'))
);

CREATE INDEX idx_test_runs_protocol ON test_runs(protocol_id);
CREATE INDEX idx_test_runs_status ON test_runs(status);
CREATE INDEX idx_test_runs_module_serial ON test_runs(module_serial_number);
CREATE INDEX idx_test_runs_batch ON test_runs(batch_id);
CREATE INDEX idx_test_runs_time ON test_runs(start_time, end_time);
CREATE INDEX idx_test_runs_protocol_status ON test_runs(protocol_id, status);

-- Data points table
CREATE TABLE IF NOT EXISTS data_points (
    id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(50) NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,

    -- Timing
    timestamp TIMESTAMP NOT NULL,
    cycle_number INTEGER,
    phase VARCHAR(50),

    -- Environmental parameters
    chamber_temperature NUMERIC(6,2),
    chamber_humidity NUMERIC(5,2),
    chamber_pressure NUMERIC(6,2),
    uv_irradiance NUMERIC(7,2),

    -- Module parameters
    module_temperature NUMERIC(6,2),
    voc NUMERIC(8,4),
    isc NUMERIC(8,4),
    vmp NUMERIC(8,4),
    imp NUMERIC(8,4),
    pmax NUMERIC(10,4),
    fill_factor NUMERIC(5,4),
    efficiency NUMERIC(5,2),

    -- Additional data
    additional_data JSONB,

    -- Data quality
    data_quality_flag VARCHAR(20),
    notes TEXT,

    -- Constraints
    CONSTRAINT data_points_quality_check CHECK (data_quality_flag IN ('good', 'questionable', 'bad', NULL))
);

CREATE INDEX idx_data_points_test_run ON data_points(test_run_id);
CREATE INDEX idx_data_points_timestamp ON data_points(timestamp);
CREATE INDEX idx_data_points_test_time ON data_points(test_run_id, timestamp);
CREATE INDEX idx_data_points_cycle_phase ON data_points(test_run_id, cycle_number, phase);

-- QC results table
CREATE TABLE IF NOT EXISTS qc_results (
    id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(50) NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,

    -- Check identification
    check_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(50),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cycle_number INTEGER,

    -- Results
    passed BOOLEAN NOT NULL,
    severity VARCHAR(20),
    action_taken VARCHAR(50),

    -- Details
    measured_value NUMERIC,
    threshold_value NUMERIC,
    deviation NUMERIC,
    details JSONB,
    notes TEXT,

    -- Constraints
    CONSTRAINT qc_results_severity_check CHECK (severity IN ('critical', 'major', 'minor', NULL)),
    CONSTRAINT qc_results_action_check CHECK (action_taken IN ('alert', 'flag', 'abort', NULL))
);

CREATE INDEX idx_qc_results_test_run ON qc_results(test_run_id);
CREATE INDEX idx_qc_results_check_name ON qc_results(check_name);
CREATE INDEX idx_qc_results_passed ON qc_results(test_run_id, passed);
CREATE INDEX idx_qc_results_test_check ON qc_results(test_run_id, check_name);

-- Interim tests table
CREATE TABLE IF NOT EXISTS interim_tests (
    id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(50) NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,

    -- Test identification
    cycle_number INTEGER NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- I-V Curve measurements
    voc NUMERIC(8,4),
    isc NUMERIC(8,4),
    vmp NUMERIC(8,4),
    imp NUMERIC(8,4),
    pmax NUMERIC(10,4),
    fill_factor NUMERIC(5,4),
    efficiency NUMERIC(5,2),

    -- Degradation
    power_retention_percent NUMERIC(5,2),
    degradation_percent NUMERIC(5,2),

    -- Insulation
    insulation_resistance NUMERIC(10,2),

    -- Visual inspection
    visual_defects JSONB,
    visual_inspection_passed BOOLEAN,

    -- Additional measurements
    additional_measurements JSONB,

    -- Pass/Fail
    passed BOOLEAN,
    failure_modes JSONB,
    notes TEXT
);

CREATE INDEX idx_interim_tests_test_run ON interim_tests(test_run_id);
CREATE INDEX idx_interim_tests_cycle ON interim_tests(test_run_id, cycle_number);
CREATE INDEX idx_interim_tests_type ON interim_tests(test_run_id, test_type);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_test_runs_updated_at BEFORE UPDATE ON test_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_protocols_last_modified BEFORE UPDATE ON protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries

-- Test run summary view
CREATE OR REPLACE VIEW test_run_summary AS
SELECT
    tr.id,
    tr.protocol_id,
    p.name AS protocol_name,
    tr.module_serial_number,
    tr.batch_id,
    tr.status,
    tr.start_time,
    tr.end_time,
    tr.duration_seconds,
    tr.current_cycle,
    tr.total_cycles,
    ROUND((tr.current_cycle::NUMERIC / NULLIF(tr.total_cycles, 0)) * 100, 2) AS progress_percent,
    tr.pass_fail_status,
    COUNT(DISTINCT dp.id) AS total_data_points,
    COUNT(DISTINCT qc.id) AS total_qc_checks,
    COUNT(DISTINCT it.id) AS total_interim_tests
FROM test_runs tr
JOIN protocols p ON tr.protocol_id = p.id
LEFT JOIN data_points dp ON tr.id = dp.test_run_id
LEFT JOIN qc_results qc ON tr.id = qc.test_run_id
LEFT JOIN interim_tests it ON tr.id = it.test_run_id
GROUP BY tr.id, p.name;

-- Protocol usage statistics view
CREATE OR REPLACE VIEW protocol_usage_stats AS
SELECT
    p.id,
    p.protocol_number,
    p.name,
    p.category,
    COUNT(tr.id) AS total_runs,
    COUNT(CASE WHEN tr.status = 'completed' THEN 1 END) AS completed_runs,
    COUNT(CASE WHEN tr.status = 'failed' THEN 1 END) AS failed_runs,
    COUNT(CASE WHEN tr.pass_fail_status = TRUE THEN 1 END) AS passed_runs,
    AVG(tr.duration_seconds) AS avg_duration_seconds,
    MAX(tr.end_time) AS last_run_date
FROM protocols p
LEFT JOIN test_runs tr ON p.id = tr.protocol_id
GROUP BY p.id, p.protocol_number, p.name, p.category;

-- Comments
COMMENT ON TABLE protocols IS 'Test protocol definitions and configurations';
COMMENT ON TABLE test_runs IS 'Individual test run executions';
COMMENT ON TABLE data_points IS 'Continuous data collection during test runs';
COMMENT ON TABLE qc_results IS 'Quality control check results';
COMMENT ON TABLE interim_tests IS 'Interim test measurements at specified intervals';
