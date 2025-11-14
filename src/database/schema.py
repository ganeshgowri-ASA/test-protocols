"""
Database Schema

SQL schema definitions for the test protocols database.
"""

# SQLite schema for the test protocols framework
# Can be adapted for PostgreSQL, MySQL, etc.

SCHEMA_SQL = """
-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    protocol_id VARCHAR(50) PRIMARY KEY,
    protocol_name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    author VARCHAR(100),
    approved_by VARCHAR(100),
    approval_date TIMESTAMP,
    review_date TIMESTAMP,
    test_parameters JSON NOT NULL,
    measurements JSON NOT NULL,
    quality_controls JSON,
    pass_fail_criteria JSON,
    standards_reference JSON,
    tags JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(protocol_id, version)
);

-- Test sessions table
CREATE TABLE IF NOT EXISTS test_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL,
    protocol_version VARCHAR(20) NOT NULL,
    test_status VARCHAR(20) DEFAULT 'INITIATED',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    operator_id VARCHAR(100),
    operator_name VARCHAR(255),
    test_conditions JSON,
    measurements_count INTEGER DEFAULT 0,
    qc_checks_count INTEGER DEFAULT 0,
    qc_failures INTEGER DEFAULT 0,
    overall_result VARCHAR(20),
    notes TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id)
);

-- Samples table
CREATE TABLE IF NOT EXISTS samples (
    sample_id VARCHAR(100) PRIMARY KEY,
    material_type VARCHAR(50) NOT NULL,
    dimensions JSON,
    batch_code VARCHAR(100),
    lot_number VARCHAR(100),
    manufacturer VARCHAR(255),
    manufacturing_date DATE,
    baseline_measurements JSON,
    storage_conditions JSON,
    preparation_notes TEXT,
    source_batch_id VARCHAR(100),
    sample_location VARCHAR(255),
    status VARCHAR(20) DEFAULT 'AVAILABLE',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Sample batches table
CREATE TABLE IF NOT EXISTS sample_batches (
    batch_id VARCHAR(100) PRIMARY KEY,
    batch_code VARCHAR(100) NOT NULL,
    material_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(255),
    manufacturing_date DATE,
    received_date DATE,
    quantity INTEGER DEFAULT 0,
    batch_properties JSON,
    quality_certificate VARCHAR(500),
    notes TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Test session samples junction table
CREATE TABLE IF NOT EXISTS test_session_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    position INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id),
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id),
    UNIQUE(session_id, sample_id)
);

-- Measurements table
CREATE TABLE IF NOT EXISTS measurements (
    measurement_id VARCHAR(100) PRIMARY KEY,
    test_session_id VARCHAR(100) NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    measurement_type VARCHAR(50) NOT NULL,
    value REAL NOT NULL,
    unit VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_point_hours INTEGER,
    equipment_id VARCHAR(100),
    operator_id VARCHAR(100),
    environmental_conditions JSON,
    measurement_conditions JSON,
    quality_flag VARCHAR(20),
    notes TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(session_id),
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
);

-- Measurement sets table (groups measurements at same time point)
CREATE TABLE IF NOT EXISTS measurement_sets (
    measurement_set_id VARCHAR(100) PRIMARY KEY,
    test_session_id VARCHAR(100) NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    time_point_hours INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    measurements JSON NOT NULL,
    environmental_conditions JSON,
    operator_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(session_id),
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
);

-- QC checks table
CREATE TABLE IF NOT EXISTS qc_checks (
    qc_check_id VARCHAR(100) PRIMARY KEY,
    test_session_id VARCHAR(100) NOT NULL,
    qc_type VARCHAR(50) NOT NULL,
    qc_id VARCHAR(50),
    qc_name VARCHAR(255),
    status VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sample_id VARCHAR(100),
    details JSON,
    issues JSON,
    operator_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(session_id)
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
    analysis_id VARCHAR(100) PRIMARY KEY,
    test_session_id VARCHAR(100) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    sample_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results JSON NOT NULL,
    summary JSON,
    operator_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(session_id),
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
);

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    report_id VARCHAR(100) PRIMARY KEY,
    test_session_id VARCHAR(100) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(100),
    file_path VARCHAR(500),
    file_size_bytes INTEGER,
    status VARCHAR(20) DEFAULT 'GENERATED',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_session_id) REFERENCES test_sessions(session_id)
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    details JSON,
    ip_address VARCHAR(45),
    session_id VARCHAR(100)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_test_sessions_protocol ON test_sessions(protocol_id);
CREATE INDEX IF NOT EXISTS idx_test_sessions_status ON test_sessions(test_status);
CREATE INDEX IF NOT EXISTS idx_test_sessions_started ON test_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_measurements_session ON measurements(test_session_id);
CREATE INDEX IF NOT EXISTS idx_measurements_sample ON measurements(sample_id);
CREATE INDEX IF NOT EXISTS idx_measurements_type ON measurements(measurement_type);
CREATE INDEX IF NOT EXISTS idx_measurements_time_point ON measurements(time_point_hours);
CREATE INDEX IF NOT EXISTS idx_samples_batch ON samples(batch_code);
CREATE INDEX IF NOT EXISTS idx_samples_status ON samples(status);
CREATE INDEX IF NOT EXISTS idx_qc_checks_session ON qc_checks(test_session_id);
CREATE INDEX IF NOT EXISTS idx_qc_checks_status ON qc_checks(status);
CREATE INDEX IF NOT EXISTS idx_analysis_session ON analysis_results(test_session_id);
CREATE INDEX IF NOT EXISTS idx_reports_session ON reports(test_session_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
"""


def get_schema() -> str:
    """
    Get the database schema SQL.

    Returns:
        SQL schema string
    """
    return SCHEMA_SQL


def get_table_names() -> list:
    """
    Get list of table names in the schema.

    Returns:
        List of table names
    """
    return [
        'protocols',
        'test_sessions',
        'samples',
        'sample_batches',
        'test_session_samples',
        'measurements',
        'measurement_sets',
        'qc_checks',
        'analysis_results',
        'reports',
        'audit_log'
    ]
