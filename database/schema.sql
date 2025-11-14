-- Database schema for PV Test Protocol Framework
-- PostgreSQL compatible

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Test protocols table
CREATE TABLE IF NOT EXISTS test_protocols (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    standard VARCHAR(100),
    category VARCHAR(50) NOT NULL,
    test_type VARCHAR(100),
    protocol_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id, version)
);

CREATE INDEX idx_protocols_category ON test_protocols(category);
CREATE INDEX idx_protocols_test_type ON test_protocols(test_type);

-- Samples/specimens table
CREATE TABLE IF NOT EXISTS samples (
    sample_id VARCHAR(100) PRIMARY KEY,
    sample_type VARCHAR(50),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_manufacturer ON samples(manufacturer);
CREATE INDEX idx_samples_model ON samples(model);

-- Test sessions table
CREATE TABLE IF NOT EXISTS test_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    protocol_id VARCHAR(50) NOT NULL REFERENCES test_protocols(id),
    protocol_version VARCHAR(20) NOT NULL,
    operator_id VARCHAR(100),
    operator_name VARCHAR(255),
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    parameters JSONB,
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_protocol FOREIGN KEY (protocol_id) REFERENCES test_protocols(id) ON DELETE RESTRICT
);

CREATE INDEX idx_sessions_protocol ON test_sessions(protocol_id);
CREATE INDEX idx_sessions_operator ON test_sessions(operator_id);
CREATE INDEX idx_sessions_status ON test_sessions(status);
CREATE INDEX idx_sessions_start_time ON test_sessions(start_time);

-- Session samples junction table
CREATE TABLE IF NOT EXISTS session_samples (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    sample_id VARCHAR(100) NOT NULL REFERENCES samples(sample_id) ON DELETE RESTRICT,
    sample_position INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, sample_id)
);

CREATE INDEX idx_session_samples_session ON session_samples(session_id);
CREATE INDEX idx_session_samples_sample ON session_samples(sample_id);

-- Test measurements table
CREATE TABLE IF NOT EXISTS test_measurements (
    measurement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    sample_id VARCHAR(100) REFERENCES samples(sample_id) ON DELETE RESTRICT,
    measurement_def_id VARCHAR(100) NOT NULL,
    measurement_name VARCHAR(255) NOT NULL,
    measurement_type VARCHAR(50) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    unit VARCHAR(50),
    operator VARCHAR(255),
    notes TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurements_session ON test_measurements(session_id);
CREATE INDEX idx_measurements_sample ON test_measurements(sample_id);
CREATE INDEX idx_measurements_def_id ON test_measurements(measurement_def_id);
CREATE INDEX idx_measurements_stage ON test_measurements(stage);
CREATE INDEX idx_measurements_timestamp ON test_measurements(timestamp);

-- Quality control checks table
CREATE TABLE IF NOT EXISTS qc_checks (
    qc_check_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    check_id VARCHAR(100) NOT NULL,
    check_name VARCHAR(255) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    result VARCHAR(50) NOT NULL,
    details JSONB,
    performed_by VARCHAR(255),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_qc_checks_session ON qc_checks(session_id);
CREATE INDEX idx_qc_checks_check_id ON qc_checks(check_id);
CREATE INDEX idx_qc_checks_result ON qc_checks(result);

-- Test results table
CREATE TABLE IF NOT EXISTS test_results (
    result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL UNIQUE REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    overall_status VARCHAR(50) NOT NULL,
    summary TEXT,
    evaluated_at TIMESTAMP,
    evaluated_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_results_session ON test_results(session_id);
CREATE INDEX idx_results_overall_status ON test_results(overall_status);

-- Criterion evaluations table
CREATE TABLE IF NOT EXISTS criterion_evaluations (
    evaluation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    result_id UUID NOT NULL REFERENCES test_results(result_id) ON DELETE CASCADE,
    criterion_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    measured_value NUMERIC,
    limit_value NUMERIC,
    unit VARCHAR(50),
    description TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evaluations_result ON criterion_evaluations(result_id);
CREATE INDEX idx_evaluations_criterion ON criterion_evaluations(criterion_name);
CREATE INDEX idx_evaluations_status ON criterion_evaluations(status);

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    result_id UUID REFERENCES test_results(result_id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    generated_by VARCHAR(255),
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_session ON reports(session_id);
CREATE INDEX idx_reports_result ON reports(result_id);
CREATE INDEX idx_reports_type ON reports(report_type);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id VARCHAR(100),
    changes JSONB,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_record ON audit_log(record_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);

-- Views

-- View for session summary
CREATE OR REPLACE VIEW v_session_summary AS
SELECT
    ts.session_id,
    ts.protocol_id,
    ts.protocol_version,
    tp.name AS protocol_name,
    tp.category,
    ts.operator_name,
    ts.start_time,
    ts.end_time,
    ts.status,
    EXTRACT(EPOCH FROM (COALESCE(ts.end_time, CURRENT_TIMESTAMP) - ts.start_time)) / 60 AS duration_minutes,
    COUNT(DISTINCT ss.sample_id) AS sample_count,
    COUNT(DISTINCT tm.measurement_id) AS measurement_count,
    COUNT(DISTINCT qc.qc_check_id) AS qc_check_count,
    tr.overall_status
FROM test_sessions ts
LEFT JOIN test_protocols tp ON ts.protocol_id = tp.id
LEFT JOIN session_samples ss ON ts.session_id = ss.session_id
LEFT JOIN test_measurements tm ON ts.session_id = tm.session_id
LEFT JOIN qc_checks qc ON ts.session_id = qc.session_id
LEFT JOIN test_results tr ON ts.session_id = tr.session_id
GROUP BY
    ts.session_id, ts.protocol_id, ts.protocol_version, tp.name, tp.category,
    ts.operator_name, ts.start_time, ts.end_time, ts.status, tr.overall_status;

-- View for protocol usage statistics
CREATE OR REPLACE VIEW v_protocol_statistics AS
SELECT
    tp.id AS protocol_id,
    tp.name AS protocol_name,
    tp.category,
    tp.version,
    COUNT(DISTINCT ts.session_id) AS total_sessions,
    COUNT(DISTINCT CASE WHEN tr.overall_status = 'pass' THEN ts.session_id END) AS passed_sessions,
    COUNT(DISTINCT CASE WHEN tr.overall_status = 'fail' THEN ts.session_id END) AS failed_sessions,
    ROUND(
        COUNT(DISTINCT CASE WHEN tr.overall_status = 'pass' THEN ts.session_id END)::NUMERIC /
        NULLIF(COUNT(DISTINCT ts.session_id), 0) * 100, 2
    ) AS pass_rate_percent,
    AVG(EXTRACT(EPOCH FROM (ts.end_time - ts.start_time)) / 3600) AS avg_duration_hours,
    MAX(ts.start_time) AS last_used
FROM test_protocols tp
LEFT JOIN test_sessions ts ON tp.id = ts.protocol_id
LEFT JOIN test_results tr ON ts.session_id = tr.session_id
GROUP BY tp.id, tp.name, tp.category, tp.version;

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_test_protocols_updated_at
    BEFORE UPDATE ON test_protocols
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_samples_updated_at
    BEFORE UPDATE ON samples
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_sessions_updated_at
    BEFORE UPDATE ON test_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_results_updated_at
    BEFORE UPDATE ON test_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments on tables
COMMENT ON TABLE test_protocols IS 'Stores test protocol definitions';
COMMENT ON TABLE samples IS 'Stores sample/specimen information';
COMMENT ON TABLE test_sessions IS 'Stores test session information';
COMMENT ON TABLE test_measurements IS 'Stores measurement data from test sessions';
COMMENT ON TABLE qc_checks IS 'Stores quality control check results';
COMMENT ON TABLE test_results IS 'Stores evaluated test results';
COMMENT ON TABLE criterion_evaluations IS 'Stores individual pass/fail criterion evaluations';
COMMENT ON TABLE reports IS 'Stores generated report metadata';
COMMENT ON TABLE audit_log IS 'Audit trail for data changes';
