-- Test Results Schema
-- Database schema for storing test execution results and measurements

-- Test Executions Table
-- Main table for tracking test execution instances
CREATE TABLE IF NOT EXISTS test_executions (
    execution_id SERIAL PRIMARY KEY,
    execution_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    protocol_id VARCHAR(50) NOT NULL REFERENCES test_protocols(protocol_id) ON DELETE RESTRICT,
    specimen_id INTEGER REFERENCES test_specimens(specimen_id) ON DELETE RESTRICT,
    module_id VARCHAR(100) NOT NULL,

    -- Test metadata
    test_date DATE NOT NULL,
    test_start_time TIMESTAMP WITH TIME ZONE,
    test_end_time TIMESTAMP WITH TIME ZONE,
    operator_name VARCHAR(100) NOT NULL,
    supervisor_name VARCHAR(100),

    -- Test status
    status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'aborted', 'invalid')),
    result VARCHAR(20) CHECK (result IN ('pass', 'fail', 'inconclusive', 'not_applicable')),

    -- Environmental conditions
    ambient_temperature_c NUMERIC(5, 2),
    relative_humidity_pct NUMERIC(5, 2),
    atmospheric_pressure_kpa NUMERIC(6, 2),

    -- Data storage
    test_data JSONB,
    calculated_values JSONB,

    -- Quality and compliance
    qc_status VARCHAR(20) CHECK (qc_status IN ('pending', 'in_review', 'approved', 'rejected')),
    compliance_status VARCHAR(20) CHECK (compliance_status IN ('compliant', 'non_compliant', 'pending_review')),

    -- Notes and documentation
    notes TEXT,
    failure_reason TEXT,
    corrective_action TEXT,

    -- Audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),

    -- Approval workflow
    approved_by VARCHAR(100),
    approved_at TIMESTAMP WITH TIME ZONE,
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for common queries
CREATE INDEX idx_test_executions_protocol ON test_executions(protocol_id);
CREATE INDEX idx_test_executions_specimen ON test_executions(specimen_id);
CREATE INDEX idx_test_executions_module ON test_executions(module_id);
CREATE INDEX idx_test_executions_date ON test_executions(test_date);
CREATE INDEX idx_test_executions_operator ON test_executions(operator_name);
CREATE INDEX idx_test_executions_status ON test_executions(status);
CREATE INDEX idx_test_executions_result ON test_executions(result);
CREATE INDEX idx_test_executions_qc_status ON test_executions(qc_status);
CREATE INDEX idx_test_executions_test_data ON test_executions USING GIN (test_data);

-- Measurements Table
-- Stores individual measurements taken during tests
CREATE TABLE IF NOT EXISTS measurements (
    measurement_id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES test_executions(execution_id) ON DELETE CASCADE,

    -- Measurement identification
    measurement_name VARCHAR(100) NOT NULL,
    measurement_type VARCHAR(50),
    measurement_order INTEGER,

    -- Measurement values
    measured_value NUMERIC(20, 6),
    unit VARCHAR(20),
    uncertainty NUMERIC(20, 6),

    -- Measurement metadata
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    equipment_id VARCHAR(50) REFERENCES equipment(equipment_id),
    operator_notes TEXT,

    -- Data quality
    is_valid BOOLEAN DEFAULT TRUE,
    validation_status VARCHAR(20) CHECK (validation_status IN ('valid', 'questionable', 'invalid', 'pending_review')),

    -- Additional data
    metadata JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for measurements
CREATE INDEX idx_measurements_execution ON measurements(execution_id);
CREATE INDEX idx_measurements_name ON measurements(measurement_name);
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp);
CREATE INDEX idx_measurements_equipment ON measurements(equipment_id);
CREATE INDEX idx_measurements_metadata ON measurements USING GIN (metadata);

-- Time Series Data Table
-- For tests that collect continuous time-series data
CREATE TABLE IF NOT EXISTS time_series_data (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES test_executions(execution_id) ON DELETE CASCADE,

    -- Time series identification
    series_name VARCHAR(100) NOT NULL,
    series_type VARCHAR(50),

    -- Time and value
    timestamp_offset_seconds NUMERIC(12, 3),
    measured_value NUMERIC(20, 6),
    unit VARCHAR(20),

    -- Data quality
    is_valid BOOLEAN DEFAULT TRUE,

    -- Additional metadata
    metadata JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for time series data
CREATE INDEX idx_time_series_execution ON time_series_data(execution_id);
CREATE INDEX idx_time_series_name ON time_series_data(series_name);
CREATE INDEX idx_time_series_timestamp ON time_series_data(timestamp_offset_seconds);

-- Equipment Usage Table
-- Tracks which equipment was used in each test execution
CREATE TABLE IF NOT EXISTS execution_equipment (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES test_executions(execution_id) ON DELETE CASCADE,
    equipment_id VARCHAR(50) NOT NULL REFERENCES equipment(equipment_id) ON DELETE RESTRICT,

    -- Calibration at time of use
    calibration_due_date DATE,
    calibration_status VARCHAR(20) CHECK (calibration_status IN ('current', 'due', 'overdue', 'not_required')),

    -- Usage notes
    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_execution_equipment UNIQUE (execution_id, equipment_id)
);

CREATE INDEX idx_execution_equipment_execution ON execution_equipment(execution_id);
CREATE INDEX idx_execution_equipment_equipment ON execution_equipment(equipment_id);

-- Test Attachments Table
-- Stores references to files associated with test executions
CREATE TABLE IF NOT EXISTS test_attachments (
    attachment_id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES test_executions(execution_id) ON DELETE CASCADE,

    -- File information
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,

    -- Attachment metadata
    attachment_type VARCHAR(50) CHECK (attachment_type IN ('photo', 'document', 'data_file', 'certificate', 'report', 'chart', 'other')),
    description TEXT,

    -- Photo-specific fields
    photo_stage VARCHAR(50) CHECK (photo_stage IN ('pre_test', 'during_test', 'post_test', 'defect', 'setup')),

    -- Timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100)
);

CREATE INDEX idx_test_attachments_execution ON test_attachments(execution_id);
CREATE INDEX idx_test_attachments_type ON test_attachments(attachment_type);
CREATE INDEX idx_test_attachments_stage ON test_attachments(photo_stage);

-- Test Comments Table
-- Stores comments and notes during test execution
CREATE TABLE IF NOT EXISTS test_comments (
    comment_id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES test_executions(execution_id) ON DELETE CASCADE,

    -- Comment content
    comment_text TEXT NOT NULL,
    comment_type VARCHAR(50) CHECK (comment_type IN ('observation', 'issue', 'question', 'resolution', 'general')),

    -- User information
    author_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Thread support (for replies)
    parent_comment_id INTEGER REFERENCES test_comments(comment_id) ON DELETE CASCADE,

    -- Status
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_test_comments_execution ON test_comments(execution_id);
CREATE INDEX idx_test_comments_author ON test_comments(author_name);
CREATE INDEX idx_test_comments_created ON test_comments(created_at);
CREATE INDEX idx_test_comments_parent ON test_comments(parent_comment_id);

-- Create trigger for test_executions updated_at
CREATE TRIGGER update_test_executions_updated_at
    BEFORE UPDATE ON test_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries

-- View: Active Tests
CREATE OR REPLACE VIEW active_tests AS
SELECT
    e.execution_id,
    e.execution_uuid,
    e.protocol_id,
    p.protocol_name,
    e.module_id,
    s.manufacturer,
    s.model,
    e.test_date,
    e.operator_name,
    e.status,
    e.result,
    e.qc_status
FROM test_executions e
LEFT JOIN test_protocols p ON e.protocol_id = p.protocol_id
LEFT JOIN test_specimens s ON e.specimen_id = s.specimen_id
WHERE e.status IN ('pending', 'in_progress');

-- View: Test Summary Statistics
CREATE OR REPLACE VIEW test_summary_stats AS
SELECT
    protocol_id,
    COUNT(*) as total_tests,
    COUNT(CASE WHEN result = 'pass' THEN 1 END) as passed,
    COUNT(CASE WHEN result = 'fail' THEN 1 END) as failed,
    COUNT(CASE WHEN result = 'inconclusive' THEN 1 END) as inconclusive,
    ROUND(100.0 * COUNT(CASE WHEN result = 'pass' THEN 1 END) / NULLIF(COUNT(*), 0), 2) as pass_rate_pct,
    MIN(test_date) as first_test_date,
    MAX(test_date) as last_test_date
FROM test_executions
WHERE status = 'completed'
GROUP BY protocol_id;

-- Comments for documentation
COMMENT ON TABLE test_executions IS 'Main table for test execution instances and results';
COMMENT ON TABLE measurements IS 'Individual measurements taken during test execution';
COMMENT ON TABLE time_series_data IS 'Continuous time-series data collected during tests';
COMMENT ON TABLE execution_equipment IS 'Tracks equipment used in each test execution';
COMMENT ON TABLE test_attachments IS 'File attachments associated with test executions';
COMMENT ON TABLE test_comments IS 'Comments and notes during test execution';

COMMENT ON COLUMN test_executions.test_data IS 'Complete test data in JSON format';
COMMENT ON COLUMN test_executions.calculated_values IS 'Calculated values and derived metrics';
COMMENT ON COLUMN measurements.uncertainty IS 'Measurement uncertainty value';
COMMENT ON COLUMN time_series_data.timestamp_offset_seconds IS 'Time offset from test start in seconds';
