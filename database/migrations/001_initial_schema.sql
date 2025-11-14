-- Initial database schema for PV Testing Protocol Framework
-- Migration: 001_initial_schema
-- Date: 2025-01-14
-- Description: Creates initial tables for protocols, samples, equipment, test executions, and QC

-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_id VARCHAR(50) UNIQUE NOT NULL,
    protocol_name VARCHAR(200) NOT NULL,
    version VARCHAR(20) NOT NULL,
    standard VARCHAR(100),
    category VARCHAR(50),
    description TEXT,
    protocol_json JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE INDEX idx_protocols_protocol_id ON protocols(protocol_id);

-- Samples table
CREATE TABLE IF NOT EXISTS samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id VARCHAR(100) UNIQUE NOT NULL,
    sample_type VARCHAR(100),
    technology VARCHAR(100),
    area REAL,
    manufacturer VARCHAR(200),
    batch_number VARCHAR(100),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_sample_id ON samples(sample_id);

-- Equipment table
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id VARCHAR(100) UNIQUE NOT NULL,
    equipment_name VARCHAR(200) NOT NULL,
    equipment_type VARCHAR(100),
    manufacturer VARCHAR(200),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    calibration_date TIMESTAMP,
    calibration_due_date TIMESTAMP,
    specifications JSON,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_equipment_id ON equipment(equipment_id);

-- Test executions table
CREATE TABLE IF NOT EXISTS test_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id VARCHAR(200) UNIQUE NOT NULL,
    protocol_id INTEGER NOT NULL,
    sample_id INTEGER NOT NULL,
    operator VARCHAR(100),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'initialized',
    test_parameters JSON,
    environmental_conditions JSON,
    results_summary JSON,
    qc_status VARCHAR(50),
    data_file_path VARCHAR(500),
    report_file_path VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (protocol_id) REFERENCES protocols(id),
    FOREIGN KEY (sample_id) REFERENCES samples(id)
);

CREATE INDEX idx_test_executions_test_id ON test_executions(test_id);
CREATE INDEX idx_test_executions_protocol_id ON test_executions(protocol_id);
CREATE INDEX idx_test_executions_sample_id ON test_executions(sample_id);

-- Test equipment association table
CREATE TABLE IF NOT EXISTS test_equipment (
    test_execution_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    PRIMARY KEY (test_execution_id, equipment_id),
    FOREIGN KEY (test_execution_id) REFERENCES test_executions(id),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id)
);

-- Test results table
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_execution_id INTEGER NOT NULL,
    measurement_type VARCHAR(100) NOT NULL,
    wavelength REAL,
    value REAL NOT NULL,
    unit VARCHAR(50),
    uncertainty REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (test_execution_id) REFERENCES test_executions(id)
);

CREATE INDEX idx_test_results_test_execution_id ON test_results(test_execution_id);

-- Quality control table
CREATE TABLE IF NOT EXISTS quality_control (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_execution_id INTEGER NOT NULL,
    check_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(50),
    passed BOOLEAN NOT NULL,
    measured_value REAL,
    threshold_value REAL,
    unit VARCHAR(50),
    action VARCHAR(50),
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_execution_id) REFERENCES test_executions(id)
);

CREATE INDEX idx_quality_control_test_execution_id ON quality_control(test_execution_id);

-- Insert SPEC-001 protocol
INSERT INTO protocols (protocol_id, protocol_name, version, standard, category, description, protocol_json)
VALUES (
    'SPEC-001',
    'Spectral Response Test',
    '1.0.0',
    'IEC 60904-8',
    'Performance',
    'Measures the spectral response of photovoltaic devices as a function of wavelength according to IEC 60904-8 standard',
    '{}' -- Will be populated from JSON file
);
