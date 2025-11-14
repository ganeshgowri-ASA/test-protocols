-- Test Protocols Database Schema
-- SQLite/PostgreSQL compatible schema

-- Protocols table - stores protocol definitions
CREATE TABLE IF NOT EXISTS protocols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    config JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    CONSTRAINT unique_protocol_version UNIQUE (protocol_id, version)
);

-- Test runs table - stores individual test executions
CREATE TABLE IF NOT EXISTS test_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id VARCHAR(100) UNIQUE NOT NULL,
    protocol_id VARCHAR(50) NOT NULL,
    protocol_version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    operator VARCHAR(100),
    sample_id VARCHAR(100),
    device_id VARCHAR(100),
    location VARCHAR(100),
    environmental_conditions JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id)
);

-- Measurements table - stores raw measurement data
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit VARCHAR(20),
    quality_flag VARCHAR(20) DEFAULT 'good',
    sensor_id VARCHAR(50),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES test_runs(run_id),
    INDEX idx_run_metric (run_id, metric_name),
    INDEX idx_timestamp (timestamp)
);

-- Results table - stores analyzed results
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id VARCHAR(100) NOT NULL,
    result_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100),
    calculated_value REAL,
    unit VARCHAR(20),
    pass_fail VARCHAR(10),
    threshold REAL,
    deviation REAL,
    calculation_method VARCHAR(100),
    result_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES test_runs(run_id),
    INDEX idx_run_result (run_id, result_type)
);

-- QA flags table - stores quality assurance flags
CREATE TABLE IF NOT EXISTS qa_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id VARCHAR(100) NOT NULL,
    measurement_id INTEGER,
    flag_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flagged_by VARCHAR(100),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    resolution_notes TEXT,
    FOREIGN KEY (run_id) REFERENCES test_runs(run_id),
    FOREIGN KEY (measurement_id) REFERENCES measurements(id),
    INDEX idx_run_flags (run_id)
);

-- Reports table - stores generated reports
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id VARCHAR(100) UNIQUE NOT NULL,
    run_id VARCHAR(100) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(100),
    report_data JSON,
    FOREIGN KEY (run_id) REFERENCES test_runs(run_id)
);

-- Audit log table - tracks all system activities
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    details JSON,
    ip_address VARCHAR(45)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_protocols_status ON protocols(status);
CREATE INDEX IF NOT EXISTS idx_test_runs_status ON test_runs(status);
CREATE INDEX IF NOT EXISTS idx_test_runs_protocol ON test_runs(protocol_id);
CREATE INDEX IF NOT EXISTS idx_qa_flags_unresolved ON qa_flags(resolved) WHERE resolved = FALSE;

-- Create views for common queries
CREATE VIEW IF NOT EXISTS v_active_protocols AS
SELECT
    protocol_id,
    name,
    version,
    category,
    description,
    created_at,
    updated_at
FROM protocols
WHERE status = 'active'
ORDER BY protocol_id, version DESC;

CREATE VIEW IF NOT EXISTS v_test_run_summary AS
SELECT
    tr.run_id,
    tr.protocol_id,
    p.name AS protocol_name,
    tr.status,
    tr.start_time,
    tr.end_time,
    tr.duration_seconds,
    tr.operator,
    tr.sample_id,
    COUNT(DISTINCT m.id) AS measurement_count,
    COUNT(DISTINCT CASE WHEN qf.resolved = FALSE THEN qf.id END) AS open_flags,
    COUNT(DISTINCT r.id) AS result_count
FROM test_runs tr
LEFT JOIN protocols p ON tr.protocol_id = p.protocol_id
LEFT JOIN measurements m ON tr.run_id = m.run_id
LEFT JOIN qa_flags qf ON tr.run_id = qf.run_id
LEFT JOIN results r ON tr.run_id = r.run_id
GROUP BY tr.run_id, tr.protocol_id, p.name, tr.status, tr.start_time,
         tr.end_time, tr.duration_seconds, tr.operator, tr.sample_id;
