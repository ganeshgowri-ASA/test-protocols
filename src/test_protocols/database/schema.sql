-- Database schema for PV Test Protocol Framework
-- PostgreSQL compatible

-- Create enum types
CREATE TYPE test_category AS ENUM ('mechanical', 'environmental', 'electrical', 'thermal', 'optical');
CREATE TYPE test_status AS ENUM ('pending', 'in_progress', 'paused', 'completed', 'failed', 'aborted');
CREATE TYPE test_result AS ENUM ('pass', 'fail', 'warning', 'inconclusive');
CREATE TYPE calibration_status AS ENUM ('current', 'due', 'overdue');

-- Protocols table
CREATE TABLE protocols (
    protocol_id VARCHAR(20) PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category test_category NOT NULL,
    standard_name VARCHAR(50),
    standard_code VARCHAR(100),
    description TEXT,
    duration_minutes FLOAT,
    definition JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_protocols_category ON protocols(category);
CREATE INDEX idx_protocols_is_active ON protocols(is_active);

-- Test runs table
CREATE TABLE test_runs (
    test_run_id VARCHAR(100) PRIMARY KEY,
    protocol_id VARCHAR(20) NOT NULL REFERENCES protocols(protocol_id),
    protocol_version VARCHAR(20) NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    operator_id VARCHAR(100) NOT NULL,
    status test_status NOT NULL,
    current_step VARCHAR(50),
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_runs_sample ON test_runs(sample_id);
CREATE INDEX idx_test_runs_protocol ON test_runs(protocol_id);
CREATE INDEX idx_test_runs_status ON test_runs(status);
CREATE INDEX idx_test_runs_start_time ON test_runs(start_time);

-- Measurements table
CREATE TABLE measurements (
    measurement_id VARCHAR(36) PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    step_id VARCHAR(50) NOT NULL,
    measurement_type VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sensor_id VARCHAR(50),
    metadata JSONB
);

CREATE INDEX idx_measurements_test_run ON measurements(test_run_id);
CREATE INDEX idx_measurements_step ON measurements(step_id);
CREATE INDEX idx_measurements_type ON measurements(measurement_type);
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp);

-- Test results table
CREATE TABLE test_results (
    result_id VARCHAR(36) PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    step_id VARCHAR(50),
    result test_result NOT NULL,
    passed BOOLEAN,
    summary TEXT,
    details JSONB,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_results_test_run ON test_results(test_run_id);
CREATE INDEX idx_test_results_result ON test_results(result);

-- Equipment table
CREATE TABLE equipment (
    equipment_id VARCHAR(50) PRIMARY KEY,
    protocol_id VARCHAR(20) REFERENCES protocols(protocol_id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    manufacturer VARCHAR(100),
    calibration_required BOOLEAN DEFAULT TRUE,
    calibration_interval_days INTEGER,
    last_calibration_date TIMESTAMP,
    next_calibration_date TIMESTAMP,
    calibration_status calibration_status,
    location VARCHAR(100),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_calibration_status ON equipment(calibration_status);
CREATE INDEX idx_equipment_is_active ON equipment(is_active);

-- Samples table
CREATE TABLE samples (
    sample_id VARCHAR(100) PRIMARY KEY,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    manufacturing_date TIMESTAMP,
    rated_power_w FLOAT,
    rated_voltage_v FLOAT,
    rated_current_a FLOAT,
    dimensions_mm JSONB,
    weight_kg FLOAT,
    technology_type VARCHAR(50),
    received_date TIMESTAMP,
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_manufacturer ON samples(manufacturer);
CREATE INDEX idx_samples_model ON samples(model);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_protocols_updated_at BEFORE UPDATE ON protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equipment_updated_at BEFORE UPDATE ON equipment
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries

-- Active protocols view
CREATE VIEW active_protocols AS
SELECT
    protocol_id,
    version,
    name,
    category,
    standard_code,
    duration_minutes,
    created_at
FROM protocols
WHERE is_active = TRUE
ORDER BY category, protocol_id;

-- Test run summary view
CREATE VIEW test_run_summary AS
SELECT
    tr.test_run_id,
    tr.protocol_id,
    p.name AS protocol_name,
    tr.sample_id,
    tr.operator_id,
    tr.status,
    tr.start_time,
    tr.end_time,
    EXTRACT(EPOCH FROM (COALESCE(tr.end_time, CURRENT_TIMESTAMP) - tr.start_time)) / 60 AS duration_minutes,
    COUNT(DISTINCT m.measurement_id) AS total_measurements
FROM test_runs tr
JOIN protocols p ON tr.protocol_id = p.protocol_id
LEFT JOIN measurements m ON tr.test_run_id = m.test_run_id
GROUP BY tr.test_run_id, tr.protocol_id, p.name, tr.sample_id, tr.operator_id, tr.status, tr.start_time, tr.end_time
ORDER BY tr.start_time DESC;

-- Equipment calibration status view
CREATE VIEW equipment_calibration_status AS
SELECT
    equipment_id,
    name,
    type,
    model,
    last_calibration_date,
    next_calibration_date,
    CASE
        WHEN next_calibration_date < CURRENT_DATE THEN 'overdue'
        WHEN next_calibration_date < CURRENT_DATE + INTERVAL '30 days' THEN 'due'
        ELSE 'current'
    END AS status,
    CASE
        WHEN next_calibration_date < CURRENT_DATE
        THEN CURRENT_DATE - next_calibration_date
        ELSE NULL
    END AS days_overdue
FROM equipment
WHERE calibration_required = TRUE AND is_active = TRUE
ORDER BY next_calibration_date;

COMMENT ON TABLE protocols IS 'Test protocol definitions and metadata';
COMMENT ON TABLE test_runs IS 'Individual test execution instances';
COMMENT ON TABLE measurements IS 'Measurement data points collected during tests';
COMMENT ON TABLE test_results IS 'Test results and analysis data';
COMMENT ON TABLE equipment IS 'Test equipment inventory and calibration tracking';
COMMENT ON TABLE samples IS 'Test sample/module information';
