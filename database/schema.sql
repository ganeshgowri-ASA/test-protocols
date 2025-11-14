-- Test Protocols Database Schema
-- This schema supports storing test protocol definitions, test runs,
-- measurements, inspections, and QC results.

-- Enable foreign key constraints (SQLite)
PRAGMA foreign_keys = ON;

-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    definition_json JSON NOT NULL,
    standards JSON,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    author VARCHAR(100),
    tags JSON,
    CONSTRAINT uq_protocol_version UNIQUE (protocol_id, version)
);

CREATE INDEX idx_protocol_id ON protocols(protocol_id);
CREATE INDEX idx_protocol_category ON protocols(category);
CREATE INDEX idx_protocol_category_active ON protocols(category, is_active);

-- Test runs table
CREATE TABLE IF NOT EXISTS test_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id VARCHAR(100) UNIQUE NOT NULL,
    protocol_id INTEGER NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100),
    operator VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'planned',
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    planned_completion TIMESTAMP,
    test_data JSON,
    metadata JSON,
    test_result VARCHAR(50),
    total_cycles INTEGER,
    current_cycle INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (protocol_id) REFERENCES protocols(id) ON DELETE CASCADE
);

CREATE INDEX idx_testrun_id ON test_runs(run_id);
CREATE INDEX idx_testrun_protocol ON test_runs(protocol_id);
CREATE INDEX idx_testrun_sample ON test_runs(sample_id);
CREATE INDEX idx_testrun_status ON test_runs(status);
CREATE INDEX idx_testrun_status_date ON test_runs(status, start_date);
CREATE INDEX idx_testrun_operator ON test_runs(operator);

-- Measurements table
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_run_id INTEGER NOT NULL,
    cycle_number INTEGER NOT NULL DEFAULT 0,
    measurement_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    voc REAL,
    isc REAL,
    pmax REAL,
    vmp REAL,
    imp REAL,
    ff REAL,
    rs REAL,
    rsh REAL,
    temperature REAL,
    humidity REAL,
    irradiance REAL,
    insulation_resistance REAL,
    wet_leakage_current REAL,
    ground_continuity BOOLEAN,
    raw_data JSON,
    notes TEXT,
    FOREIGN KEY (test_run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE INDEX idx_measurement_testrun ON measurements(test_run_id);
CREATE INDEX idx_measurement_testrun_cycle ON measurements(test_run_id, cycle_number);
CREATE INDEX idx_measurement_type ON measurements(measurement_type);

-- Visual inspections table
CREATE TABLE IF NOT EXISTS visual_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_run_id INTEGER NOT NULL,
    cycle_number INTEGER NOT NULL DEFAULT 0,
    inspection_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    visual_corrosion VARCHAR(50),
    corrosion_locations JSON,
    corrosion_area_mm2 REAL,
    delamination BOOLEAN DEFAULT 0,
    delamination_locations JSON,
    discoloration BOOLEAN DEFAULT 0,
    bubbles BOOLEAN DEFAULT 0,
    cracks BOOLEAN DEFAULT 0,
    hot_spots BOOLEAN DEFAULT 0,
    photos JSON,
    notes TEXT,
    inspector VARCHAR(100),
    FOREIGN KEY (test_run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE INDEX idx_inspection_testrun ON visual_inspections(test_run_id);
CREATE INDEX idx_inspection_testrun_cycle ON visual_inspections(test_run_id, cycle_number);

-- QC results table
CREATE TABLE IF NOT EXISTS qc_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_run_id INTEGER NOT NULL,
    criterion_id VARCHAR(100) NOT NULL,
    criterion_name VARCHAR(200) NOT NULL,
    criterion_type VARCHAR(50),
    severity VARCHAR(20) NOT NULL DEFAULT 'warning',
    passed BOOLEAN NOT NULL,
    measured_value REAL,
    expected_value REAL,
    threshold REAL,
    message TEXT,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checked_by VARCHAR(100),
    FOREIGN KEY (test_run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE INDEX idx_qc_testrun ON qc_results(test_run_id);
CREATE INDEX idx_qc_testrun_severity ON qc_results(test_run_id, severity, passed);

-- Equipment table
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    calibration_required BOOLEAN DEFAULT 0,
    last_calibration_date TIMESTAMP,
    next_calibration_date TIMESTAMP,
    calibration_interval_days INTEGER,
    location VARCHAR(100),
    status VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_id ON equipment(equipment_id);
CREATE INDEX idx_equipment_type ON equipment(type);
CREATE INDEX idx_equipment_type_status ON equipment(type, status);

-- Samples table
CREATE TABLE IF NOT EXISTS samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id VARCHAR(100) UNIQUE NOT NULL,
    serial_number VARCHAR(100),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    technology VARCHAR(100),
    length_mm REAL,
    width_mm REAL,
    thickness_mm REAL,
    weight_g REAL,
    area_m2 REAL,
    rated_power_w REAL,
    rated_voc_v REAL,
    rated_isc_a REAL,
    rated_vmp_v REAL,
    rated_imp_a REAL,
    received_date TIMESTAMP,
    condition_on_receipt VARCHAR(50),
    storage_location VARCHAR(100),
    status VARCHAR(50),
    metadata JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sample_id ON samples(sample_id);
CREATE INDEX idx_sample_serial ON samples(serial_number);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(50),
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_user_email ON users(email);

-- Views for common queries

-- View: Active test runs with protocol information
CREATE VIEW IF NOT EXISTS v_active_test_runs AS
SELECT
    tr.run_id,
    tr.sample_id,
    tr.operator,
    tr.status,
    tr.start_date,
    tr.current_cycle,
    tr.total_cycles,
    p.protocol_id,
    p.name AS protocol_name,
    p.category
FROM test_runs tr
JOIN protocols p ON tr.protocol_id = p.id
WHERE tr.status IN ('planned', 'in_progress');

-- View: QC failures summary
CREATE VIEW IF NOT EXISTS v_qc_failures AS
SELECT
    tr.run_id,
    tr.sample_id,
    p.protocol_id,
    p.name AS protocol_name,
    qc.criterion_name,
    qc.severity,
    qc.message,
    qc.checked_at
FROM qc_results qc
JOIN test_runs tr ON qc.test_run_id = tr.id
JOIN protocols p ON tr.protocol_id = p.id
WHERE qc.passed = 0 AND qc.severity = 'critical';

-- View: Degradation summary
CREATE VIEW IF NOT EXISTS v_degradation_summary AS
SELECT
    tr.run_id,
    tr.sample_id,
    p.protocol_id,
    baseline.pmax AS baseline_pmax,
    final.pmax AS final_pmax,
    ((baseline.pmax - final.pmax) / baseline.pmax * 100) AS degradation_percent,
    tr.test_result
FROM test_runs tr
JOIN protocols p ON tr.protocol_id = p.id
LEFT JOIN measurements baseline ON tr.id = baseline.test_run_id AND baseline.measurement_type = 'baseline'
LEFT JOIN measurements final ON tr.id = final.test_run_id AND final.measurement_type = 'final'
WHERE baseline.pmax IS NOT NULL AND final.pmax IS NOT NULL;

-- Triggers for updated_at timestamps

-- Trigger: Update protocols modified_date
CREATE TRIGGER IF NOT EXISTS trg_protocols_update_modified
AFTER UPDATE ON protocols
FOR EACH ROW
BEGIN
    UPDATE protocols SET modified_date = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Update test_runs updated_at
CREATE TRIGGER IF NOT EXISTS trg_test_runs_update_timestamp
AFTER UPDATE ON test_runs
FOR EACH ROW
BEGIN
    UPDATE test_runs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Update equipment updated_at
CREATE TRIGGER IF NOT EXISTS trg_equipment_update_timestamp
AFTER UPDATE ON equipment
FOR EACH ROW
BEGIN
    UPDATE equipment SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Update samples updated_at
CREATE TRIGGER IF NOT EXISTS trg_samples_update_timestamp
AFTER UPDATE ON samples
FOR EACH ROW
BEGIN
    UPDATE samples SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Sample data for development

-- Insert CORR-001 protocol
INSERT OR IGNORE INTO protocols (protocol_id, name, category, version, description, is_active, author)
VALUES (
    'CORR-001',
    'Corrosion Testing - Salt Spray and Humidity',
    'degradation',
    '1.0.0',
    'Comprehensive corrosion testing protocol for photovoltaic modules',
    1,
    'GenSpark Testing Team'
);

-- Insert sample users
INSERT OR IGNORE INTO users (username, email, full_name, role, department)
VALUES
    ('test.operator', 'operator@example.com', 'Test Operator', 'operator', 'Testing'),
    ('lab.manager', 'manager@example.com', 'Lab Manager', 'admin', 'Management');

-- Insert sample equipment
INSERT OR IGNORE INTO equipment (equipment_id, name, type, manufacturer, status, calibration_required)
VALUES
    ('SSC-001', 'Salt Spray Chamber', 'environmental_chamber', 'WeatherTest Inc', 'available', 1),
    ('HUM-001', 'Humidity Chamber', 'environmental_chamber', 'EnviroTest Co', 'available', 1),
    ('IVT-001', 'IV Curve Tracer', 'electrical_tester', 'SolarLab Systems', 'available', 1);
