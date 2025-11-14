-- Database Schema for Test Protocols Framework
-- PostgreSQL Compatible

-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    protocol_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    definition_json JSONB NOT NULL,
    metadata_json JSONB,
    status VARCHAR(20) DEFAULT 'active',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    approval_status VARCHAR(20) DEFAULT 'draft',
    approved_by VARCHAR(100),
    approved_at TIMESTAMP
);

CREATE INDEX idx_protocols_status ON protocols(status);
CREATE INDEX idx_protocols_category ON protocols(category);
CREATE INDEX idx_protocols_is_active ON protocols(is_active);

-- Test executions table
CREATE TABLE IF NOT EXISTS test_executions (
    id SERIAL PRIMARY KEY,
    test_execution_id VARCHAR(100) UNIQUE NOT NULL,
    protocol_id VARCHAR(50) NOT NULL REFERENCES protocols(protocol_id),
    protocol_version VARCHAR(20) NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    sample_info_json JSONB NOT NULL,
    test_conditions_json JSONB NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operator_id VARCHAR(100) NOT NULL,
    operator_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'in_progress'
);

CREATE INDEX idx_test_executions_id ON test_executions(test_execution_id);
CREATE INDEX idx_test_executions_sample ON test_executions(sample_id);
CREATE INDEX idx_test_executions_protocol ON test_executions(protocol_id);
CREATE INDEX idx_test_executions_status ON test_executions(status);
CREATE INDEX idx_test_executions_started ON test_executions(started_at);

-- Measurements table
CREATE TABLE IF NOT EXISTS measurements (
    id SERIAL PRIMARY KEY,
    test_execution_id VARCHAR(100) NOT NULL REFERENCES test_executions(test_execution_id) ON DELETE CASCADE,
    location_id VARCHAR(50) NOT NULL,
    measurement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    measurement_data_json JSONB NOT NULL,
    chalking_rating DOUBLE PRECISION,
    location_x DOUBLE PRECISION,
    location_y DOUBLE PRECISION,
    visual_observations TEXT,
    photo_reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurements_test_execution ON measurements(test_execution_id);
CREATE INDEX idx_measurements_location ON measurements(location_id);
CREATE INDEX idx_measurements_timestamp ON measurements(measurement_timestamp);

-- Test results table
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    test_execution_id VARCHAR(100) UNIQUE NOT NULL REFERENCES test_executions(test_execution_id) ON DELETE CASCADE,
    calculated_results_json JSONB NOT NULL,
    pass_fail_assessment_json JSONB NOT NULL,
    overall_result VARCHAR(20) NOT NULL,
    average_chalking_rating DOUBLE PRECISION,
    max_chalking_rating DOUBLE PRECISION,
    chalking_std_dev DOUBLE PRECISION,
    chalking_uniformity_index DOUBLE PRECISION,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_results_test_execution ON test_results(test_execution_id);
CREATE INDEX idx_test_results_overall ON test_results(overall_result);
CREATE INDEX idx_test_results_calculated ON test_results(calculated_at);

-- QC reviews table
CREATE TABLE IF NOT EXISTS qc_reviews (
    id SERIAL PRIMARY KEY,
    test_execution_id VARCHAR(100) NOT NULL REFERENCES test_executions(test_execution_id) ON DELETE CASCADE,
    reviewer_id VARCHAR(100) NOT NULL,
    reviewer_name VARCHAR(255),
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calibration_verified BOOLEAN DEFAULT false,
    reference_scale_verified BOOLEAN DEFAULT false,
    tape_lot_verified BOOLEAN DEFAULT false,
    data_verified BOOLEAN DEFAULT false,
    documentation_verified BOOLEAN DEFAULT false,
    all_verifications_passed BOOLEAN DEFAULT false,
    qc_decision VARCHAR(50) NOT NULL,
    qc_notes TEXT,
    verification_data_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP
);

CREATE INDEX idx_qc_reviews_test_execution ON qc_reviews(test_execution_id);
CREATE INDEX idx_qc_reviews_reviewer ON qc_reviews(reviewer_id);
CREATE INDEX idx_qc_reviews_decision ON qc_reviews(qc_decision);
CREATE INDEX idx_qc_reviews_date ON qc_reviews(review_date);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(255),
    user_role VARCHAR(50),
    action_description TEXT NOT NULL,
    old_values JSONB,
    new_values JSONB,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    session_id VARCHAR(100)
);

CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Views for common queries

-- Active protocols view
CREATE OR REPLACE VIEW v_active_protocols AS
SELECT
    protocol_id,
    name,
    version,
    category,
    description,
    created_at,
    updated_at
FROM protocols
WHERE is_active = true AND status = 'active';

-- Test execution summary view
CREATE OR REPLACE VIEW v_test_execution_summary AS
SELECT
    te.test_execution_id,
    te.protocol_id,
    te.sample_id,
    te.started_at,
    te.completed_at,
    te.operator_id,
    te.status,
    tr.overall_result,
    tr.average_chalking_rating,
    COUNT(m.id) as measurement_count,
    COUNT(qc.id) as qc_review_count
FROM test_executions te
LEFT JOIN test_results tr ON te.test_execution_id = tr.test_execution_id
LEFT JOIN measurements m ON te.test_execution_id = m.test_execution_id
LEFT JOIN qc_reviews qc ON te.test_execution_id = qc.test_execution_id
GROUP BY te.test_execution_id, tr.overall_result, tr.average_chalking_rating;

-- Comments
COMMENT ON TABLE protocols IS 'Protocol definitions and metadata';
COMMENT ON TABLE test_executions IS 'Individual test execution records';
COMMENT ON TABLE measurements IS 'Individual measurement data points';
COMMENT ON TABLE test_results IS 'Calculated test results and pass/fail assessments';
COMMENT ON TABLE qc_reviews IS 'Quality control reviews and approvals';
COMMENT ON TABLE audit_logs IS 'Complete audit trail of system activities';
