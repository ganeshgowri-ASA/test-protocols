-- Initial Database Schema for Test Protocols
-- Migration: 001_initial_schema
-- Date: 2025-11-14
-- Description: Creates initial tables for protocol management, test execution, and data storage

-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_id VARCHAR(50) UNIQUE NOT NULL,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    version VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    effective_date TIMESTAMP,
    json_path VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_protocols_code ON protocols(code);
CREATE INDEX idx_protocols_category ON protocols(category);

-- Modules table
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id VARCHAR(100) UNIQUE NOT NULL,
    manufacturer VARCHAR(200) NOT NULL,
    model VARCHAR(200) NOT NULL,
    technology VARCHAR(50) NOT NULL,
    nameplate_power REAL NOT NULL,
    serial_number VARCHAR(100),
    manufacturing_date TIMESTAMP,
    dimensions_length REAL,
    dimensions_width REAL,
    dimensions_thickness REAL,
    weight REAL,
    additional_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_modules_module_id ON modules(module_id);
CREATE INDEX idx_modules_manufacturer ON modules(manufacturer);

-- Test Executions table
CREATE TABLE IF NOT EXISTS test_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    protocol_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    test_date TIMESTAMP NOT NULL,
    operator VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'not_started',
    result VARCHAR(50) DEFAULT 'not_evaluated',
    severity_level INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_hours REAL,

    -- Test conditions
    h2s_concentration REAL,
    temperature REAL,
    relative_humidity REAL,
    exposure_duration REAL,

    -- Baseline measurements
    baseline_voc REAL,
    baseline_isc REAL,
    baseline_vmp REAL,
    baseline_imp REAL,
    baseline_pmax REAL,
    baseline_ff REAL,
    baseline_insulation_mohm REAL,
    baseline_weight_kg REAL,

    -- Post-test measurements
    post_voc REAL,
    post_isc REAL,
    post_vmp REAL,
    post_imp REAL,
    post_pmax REAL,
    post_ff REAL,
    post_insulation_mohm REAL,
    post_weight_kg REAL,

    -- Degradation analysis
    degradation_pmax REAL,
    degradation_voc REAL,
    degradation_isc REAL,
    degradation_ff REAL,
    weight_change_pct REAL,

    -- Quality metrics
    environmental_stability_pass BOOLEAN,
    critical_failures INTEGER DEFAULT 0,
    major_failures INTEGER DEFAULT 0,
    minor_failures INTEGER DEFAULT 0,

    -- Additional data
    test_data TEXT,
    analysis_results TEXT,
    notes TEXT,
    abort_reason TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (protocol_id) REFERENCES protocols(id),
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

CREATE INDEX idx_executions_execution_id ON test_executions(execution_id);
CREATE INDEX idx_executions_test_date ON test_executions(test_date);
CREATE INDEX idx_executions_status ON test_executions(status);

-- Measurements table
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    value REAL,
    value_text TEXT,
    unit VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phase VARCHAR(100),
    step VARCHAR(50),
    notes TEXT,

    FOREIGN KEY (execution_id) REFERENCES test_executions(id) ON DELETE CASCADE
);

CREATE INDEX idx_measurements_execution ON measurements(execution_id);
CREATE INDEX idx_measurements_table ON measurements(table_name);

-- Environmental Logs table
CREATE TABLE IF NOT EXISTS environmental_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    h2s_ppm REAL,
    temperature_c REAL,
    humidity_rh REAL,
    chamber_pressure REAL,
    notes TEXT,

    FOREIGN KEY (execution_id) REFERENCES test_executions(id) ON DELETE CASCADE
);

CREATE INDEX idx_env_logs_execution ON environmental_logs(execution_id);
CREATE INDEX idx_env_logs_timestamp ON environmental_logs(timestamp);

-- Calibration Records table
CREATE TABLE IF NOT EXISTS calibration_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_name VARCHAR(200) NOT NULL,
    equipment_id VARCHAR(100) NOT NULL,
    calibration_date TIMESTAMP NOT NULL,
    next_calibration_date TIMESTAMP NOT NULL,
    calibration_authority VARCHAR(200),
    certificate_number VARCHAR(100),
    status VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_calibration_date ON calibration_records(calibration_date);
CREATE INDEX idx_calibration_next_date ON calibration_records(next_calibration_date);
CREATE INDEX idx_calibration_equipment ON calibration_records(equipment_id);

-- Quality Events table
CREATE TABLE IF NOT EXISTS quality_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    root_cause TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    status VARCHAR(50) NOT NULL,
    reported_by VARCHAR(200) NOT NULL,
    reported_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (execution_id) REFERENCES test_executions(id)
);

CREATE INDEX idx_quality_events_status ON quality_events(status);
CREATE INDEX idx_quality_events_reported_date ON quality_events(reported_date);

-- Create views for common queries

-- View: Recent test executions with protocol and module info
CREATE VIEW IF NOT EXISTS v_recent_tests AS
SELECT
    te.execution_id,
    te.test_date,
    te.operator,
    te.status,
    te.result,
    p.code AS protocol_code,
    p.name AS protocol_name,
    m.module_id,
    m.manufacturer,
    m.model,
    te.degradation_pmax,
    te.critical_failures,
    te.major_failures
FROM test_executions te
JOIN protocols p ON te.protocol_id = p.id
JOIN modules m ON te.module_id = m.id
ORDER BY te.test_date DESC;

-- View: Equipment calibration status
CREATE VIEW IF NOT EXISTS v_calibration_status AS
SELECT
    equipment_name,
    equipment_id,
    calibration_date,
    next_calibration_date,
    CASE
        WHEN next_calibration_date < DATE('now') THEN 'OVERDUE'
        WHEN next_calibration_date < DATE('now', '+30 days') THEN 'DUE_SOON'
        ELSE 'CURRENT'
    END AS calibration_status,
    certificate_number
FROM calibration_records
ORDER BY next_calibration_date;

-- View: Test statistics by protocol
CREATE VIEW IF NOT EXISTS v_protocol_statistics AS
SELECT
    p.code,
    p.name,
    COUNT(te.id) AS total_tests,
    SUM(CASE WHEN te.result = 'pass' THEN 1 ELSE 0 END) AS passed_tests,
    SUM(CASE WHEN te.result = 'fail' THEN 1 ELSE 0 END) AS failed_tests,
    AVG(te.degradation_pmax) AS avg_pmax_degradation,
    MAX(te.test_date) AS last_test_date
FROM protocols p
LEFT JOIN test_executions te ON p.id = te.protocol_id
GROUP BY p.id, p.code, p.name;
