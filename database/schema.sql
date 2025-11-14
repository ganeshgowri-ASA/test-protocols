-- Test Protocol Framework Database Schema
-- Version: 1.0.0
-- Date: 2025-11-14

-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_id VARCHAR(50) UNIQUE NOT NULL,
    version VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    standard VARCHAR(255),
    description TEXT,
    json_definition TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

-- Test sessions table
CREATE TABLE IF NOT EXISTS test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id VARCHAR(100) UNIQUE NOT NULL,
    protocol_id VARCHAR(50) NOT NULL,
    protocol_version VARCHAR(20) NOT NULL,
    operator VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    chamber_id VARCHAR(50),
    solar_simulator_id VARCHAR(50),
    data_logger_id VARCHAR(50),
    chamber_calibration_date DATE,
    simulator_calibration_date DATE,
    pass_fail VARCHAR(10),
    final_report_path VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id)
);

-- Modules table
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    module_type VARCHAR(50) NOT NULL,
    rated_power REAL NOT NULL,
    technology VARCHAR(100),
    manufacture_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test session modules (many-to-many relationship)
CREATE TABLE IF NOT EXISTS test_session_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_session_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    position INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    UNIQUE(test_session_id, module_id)
);

-- Electrical measurements table
CREATE TABLE IF NOT EXISTS electrical_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_session_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    phase VARCHAR(20) NOT NULL, -- pre_test, in_test, post_test
    pmax REAL NOT NULL,
    voc REAL NOT NULL,
    isc REAL NOT NULL,
    vmpp REAL NOT NULL,
    impp REAL NOT NULL,
    fill_factor REAL NOT NULL,
    irradiance REAL DEFAULT 1000.0,
    temperature REAL DEFAULT 25.0,
    spectrum VARCHAR(20) DEFAULT 'AM 1.5',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

-- Environmental measurements table
CREATE TABLE IF NOT EXISTS environmental_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_session_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    step INTEGER NOT NULL,
    cycle INTEGER NOT NULL,
    temperature REAL NOT NULL,
    relative_humidity REAL NOT NULL,
    sensor_id VARCHAR(50) NOT NULL,
    target_temperature REAL,
    target_humidity REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(id) ON DELETE CASCADE
);

-- Visual inspections table
CREATE TABLE IF NOT EXISTS visual_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_session_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    phase VARCHAR(20) NOT NULL,
    inspector VARCHAR(100) NOT NULL,
    delamination BOOLEAN DEFAULT 0,
    corrosion BOOLEAN DEFAULT 0,
    broken_cells BOOLEAN DEFAULT 0,
    bubbles BOOLEAN DEFAULT 0,
    discoloration BOOLEAN DEFAULT 0,
    mechanical_damage BOOLEAN DEFAULT 0,
    major_defects INTEGER DEFAULT 0,
    minor_defects INTEGER DEFAULT 0,
    observations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

-- Visual inspection photos table
CREATE TABLE IF NOT EXISTS inspection_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visual_inspection_id INTEGER NOT NULL,
    photo_path VARCHAR(500) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visual_inspection_id) REFERENCES visual_inspections(id) ON DELETE CASCADE
);

-- Insulation tests table
CREATE TABLE IF NOT EXISTS insulation_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_session_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    phase VARCHAR(20) NOT NULL,
    test_voltage REAL NOT NULL,
    resistance REAL NOT NULL,
    duration INTEGER NOT NULL,
    temperature REAL,
    humidity REAL,
    passed BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_session_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    severity VARCHAR(20) NOT NULL, -- INFO, WARNING, ERROR, CRITICAL
    message TEXT NOT NULL,
    parameter VARCHAR(100),
    value REAL,
    step INTEGER,
    cycle INTEGER,
    acknowledged BOOLEAN DEFAULT 0,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(id) ON DELETE CASCADE
);

-- Deviations table
CREATE TABLE IF NOT EXISTS deviations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_session_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL, -- MINOR, MAJOR, CRITICAL
    corrective_action TEXT NOT NULL,
    step INTEGER,
    cycle INTEGER,
    reviewed BOOLEAN DEFAULT 0,
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(id) ON DELETE CASCADE
);

-- Test results summary table
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_session_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    initial_power REAL NOT NULL,
    final_power REAL NOT NULL,
    power_degradation REAL NOT NULL,
    visual_pass BOOLEAN NOT NULL,
    electrical_pass BOOLEAN NOT NULL,
    insulation_pass BOOLEAN NOT NULL,
    overall_pass BOOLEAN NOT NULL,
    test_duration REAL,
    total_cycles INTEGER,
    deviations_count INTEGER DEFAULT 0,
    alerts_count INTEGER DEFAULT 0,
    completion_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    UNIQUE(test_session_id, module_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_test_sessions_protocol ON test_sessions(protocol_id);
CREATE INDEX IF NOT EXISTS idx_test_sessions_status ON test_sessions(status);
CREATE INDEX IF NOT EXISTS idx_test_sessions_start_time ON test_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_electrical_measurements_test ON electrical_measurements(test_session_id);
CREATE INDEX IF NOT EXISTS idx_electrical_measurements_module ON electrical_measurements(module_id);
CREATE INDEX IF NOT EXISTS idx_environmental_measurements_test ON environmental_measurements(test_session_id);
CREATE INDEX IF NOT EXISTS idx_environmental_measurements_time ON environmental_measurements(timestamp);
CREATE INDEX IF NOT EXISTS idx_visual_inspections_test ON visual_inspections(test_session_id);
CREATE INDEX IF NOT EXISTS idx_alerts_test ON alerts(test_session_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_deviations_test ON deviations(test_session_id);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values TEXT,
    new_values TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System configuration table
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Insert default configuration
INSERT OR IGNORE INTO system_config (config_key, config_value, description) VALUES
('db_version', '1.0.0', 'Database schema version'),
('lims_enabled', 'false', 'LIMS integration enabled'),
('qms_enabled', 'false', 'QMS integration enabled'),
('data_retention_days', '365', 'Days to retain test data'),
('auto_archive', 'true', 'Automatically archive old tests');
