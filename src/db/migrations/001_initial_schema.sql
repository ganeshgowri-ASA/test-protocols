-- Initial database schema for WIND-001 Wind Load Test Protocol
-- SQLite/PostgreSQL compatible migration

-- Create wind_load_tests table
CREATE TABLE IF NOT EXISTS wind_load_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id VARCHAR(100) NOT NULL UNIQUE,
    protocol_id VARCHAR(50) DEFAULT 'WIND-001',
    protocol_version VARCHAR(20) DEFAULT '1.0.0',

    -- Test metadata
    test_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    operator VARCHAR(200) NOT NULL,
    standard VARCHAR(100) NOT NULL,
    equipment_id VARCHAR(100),
    calibration_date TIMESTAMP,

    -- Sample information
    sample_id VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(200) NOT NULL,
    model VARCHAR(200) NOT NULL,
    serial_number VARCHAR(200),
    technology VARCHAR(50),
    rated_power REAL,
    dimensions TEXT, -- JSON

    -- Test parameters
    load_type VARCHAR(20) NOT NULL,
    pressure REAL NOT NULL,
    duration INTEGER NOT NULL,
    cycles INTEGER NOT NULL,
    temperature REAL,
    humidity REAL,
    mounting_configuration VARCHAR(100),

    -- Acceptance criteria
    acceptance_criteria TEXT, -- JSON

    -- Test results
    test_status VARCHAR(30) DEFAULT 'in_progress',
    power_degradation REAL,
    max_deflection_measured REAL,
    failure_modes TEXT, -- JSON array
    notes TEXT,
    reviewer VARCHAR(200),
    review_date TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wind_load_tests_test_id ON wind_load_tests(test_id);
CREATE INDEX idx_wind_load_tests_sample_id ON wind_load_tests(sample_id);
CREATE INDEX idx_wind_load_tests_test_date ON wind_load_tests(test_date);
CREATE INDEX idx_wind_load_tests_status ON wind_load_tests(test_status);


-- Create pre_test_measurements table
CREATE TABLE IF NOT EXISTS pre_test_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL UNIQUE,

    -- Visual inspection
    visual_inspection TEXT NOT NULL,

    -- Electrical performance
    voc REAL NOT NULL,
    isc REAL NOT NULL,
    vmp REAL NOT NULL,
    imp REAL NOT NULL,
    pmax REAL NOT NULL,

    -- Insulation resistance
    insulation_resistance REAL NOT NULL,

    -- Timestamp
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (test_id) REFERENCES wind_load_tests(id) ON DELETE CASCADE
);


-- Create post_test_measurements table
CREATE TABLE IF NOT EXISTS post_test_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL UNIQUE,

    -- Visual inspection
    visual_inspection TEXT NOT NULL,

    -- Electrical performance
    voc REAL NOT NULL,
    isc REAL NOT NULL,
    vmp REAL NOT NULL,
    imp REAL NOT NULL,
    pmax REAL NOT NULL,

    -- Insulation resistance
    insulation_resistance REAL NOT NULL,

    -- Defects
    defects_observed TEXT, -- JSON array

    -- Timestamp
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (test_id) REFERENCES wind_load_tests(id) ON DELETE CASCADE
);


-- Create cycle_measurements table
CREATE TABLE IF NOT EXISTS cycle_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    cycle_number INTEGER NOT NULL,

    -- Measurements
    actual_pressure REAL NOT NULL,
    deflection_center REAL NOT NULL,
    deflection_edges TEXT, -- JSON array

    -- Observations
    observations TEXT,

    -- Timestamp
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (test_id) REFERENCES wind_load_tests(id) ON DELETE CASCADE,
    UNIQUE(test_id, cycle_number)
);

CREATE INDEX idx_cycle_measurements_test_id ON cycle_measurements(test_id);


-- Create test_attachments table
CREATE TABLE IF NOT EXISTS test_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,

    -- File information
    filename VARCHAR(500) NOT NULL,
    filepath VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    description TEXT,

    -- Metadata
    file_size INTEGER,
    mime_type VARCHAR(100),

    -- Timestamp
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (test_id) REFERENCES wind_load_tests(id) ON DELETE CASCADE
);

CREATE INDEX idx_test_attachments_test_id ON test_attachments(test_id);


-- Create protocol_configs table
CREATE TABLE IF NOT EXISTS protocol_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    description TEXT,

    -- Configuration data
    config_data TEXT NOT NULL, -- JSON
    schema_data TEXT NOT NULL, -- JSON

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT 1,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Create test_audit_logs table
CREATE TABLE IF NOT EXISTS test_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    user VARCHAR(200) NOT NULL,
    details TEXT, -- JSON
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_audit_logs_test_id ON test_audit_logs(test_id);
CREATE INDEX idx_test_audit_logs_timestamp ON test_audit_logs(timestamp);


-- Insert WIND-001 protocol configuration
INSERT INTO protocol_configs (protocol_id, name, category, version, description, config_data, schema_data, is_active)
VALUES (
    'WIND-001',
    'Wind Load Test',
    'mechanical',
    '1.0.0',
    'Wind load testing for PV modules to verify structural integrity under wind pressure and suction loads',
    '{}', -- Will be populated from config.json
    '{}', -- Will be populated from schema.json
    1
);
