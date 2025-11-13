-- Migration: 001_create_stc_test_tables.sql
-- Description: Create tables for STC-001 protocol test data and traceability
-- Created: 2025-01-13
-- Protocol: STC-001

-- ========================================
-- Table: samples
-- Description: Stores PV module sample information
-- ========================================
CREATE TABLE IF NOT EXISTS samples (
    id SERIAL PRIMARY KEY,
    serial_number VARCHAR(50) UNIQUE NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    technology VARCHAR(50) NOT NULL,
    rated_power DECIMAL(7,2),
    rated_voc DECIMAL(6,3),
    rated_isc DECIMAL(6,3),
    rated_vmp DECIMAL(6,3),
    rated_imp DECIMAL(6,3),
    rated_efficiency DECIMAL(5,3),
    module_area DECIMAL(6,4),  -- m²
    number_of_cells INTEGER,
    bifaciality_factor DECIMAL(4,3),
    manufacturing_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_samples_serial_number ON samples(serial_number);
CREATE INDEX idx_samples_manufacturer ON samples(manufacturer);
CREATE INDEX idx_samples_technology ON samples(technology);

-- ========================================
-- Table: equipment
-- Description: Stores equipment information
-- ========================================
CREATE TABLE IF NOT EXISTS equipment (
    id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL,  -- solar_simulator, iv_tracer, temperature_sensor, pyranometer
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    calibration_date DATE,
    calibration_due_date DATE,
    calibration_certificate VARCHAR(100),
    accuracy_specification JSONB,
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, maintenance
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_equipment_calibration_due ON equipment(calibration_due_date);

-- ========================================
-- Table: users
-- Description: Stores user information
-- ========================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    full_name VARCHAR(200),
    email VARCHAR(200),
    role VARCHAR(50),  -- operator, reviewer, admin
    department VARCHAR(100),
    certification_level VARCHAR(50),
    digital_signature TEXT,  -- Encrypted signature
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- ========================================
-- Table: stc_test_executions
-- Description: Stores STC test execution data and results
-- ========================================
CREATE TABLE IF NOT EXISTS stc_test_executions (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(50) UNIQUE NOT NULL,
    protocol_version VARCHAR(10) DEFAULT '2.0',

    -- Sample reference
    sample_id INTEGER REFERENCES samples(id) ON DELETE CASCADE,

    -- Test conditions
    irradiance DECIMAL(6,2) NOT NULL,  -- W/m²
    cell_temperature DECIMAL(4,2) NOT NULL,  -- °C
    ambient_temperature DECIMAL(4,2),  -- °C
    spectrum VARCHAR(20) DEFAULT 'AM 1.5G',
    wind_speed DECIMAL(4,2),  -- m/s
    humidity DECIMAL(5,2),  -- %

    -- Equipment used
    solar_simulator_id INTEGER REFERENCES equipment(id),
    iv_tracer_id INTEGER REFERENCES equipment(id),
    temp_sensor_id INTEGER REFERENCES equipment(id),
    pyranometer_id INTEGER REFERENCES equipment(id),

    -- Measured results (at actual conditions)
    voc_measured DECIMAL(6,3),  -- V
    isc_measured DECIMAL(6,3),  -- A
    vmp_measured DECIMAL(6,3),  -- V
    imp_measured DECIMAL(6,3),  -- A
    pmax_measured DECIMAL(7,2),  -- W
    fill_factor_measured DECIMAL(5,4),
    efficiency_measured DECIMAL(5,3),  -- %

    -- Corrected results (at STC)
    voc DECIMAL(6,3),  -- V
    isc DECIMAL(6,3),  -- A
    vmp DECIMAL(6,3),  -- V
    imp DECIMAL(6,3),  -- A
    pmax DECIMAL(7,2),  -- W
    fill_factor DECIMAL(5,4),
    efficiency DECIMAL(5,3),  -- %

    -- Resistance parameters
    series_resistance DECIMAL(6,4),  -- Ω
    shunt_resistance DECIMAL(8,2),  -- Ω

    -- Corrections applied
    temperature_correction_applied BOOLEAN DEFAULT FALSE,
    irradiance_correction_applied BOOLEAN DEFAULT FALSE,
    correction_factors JSONB,  -- JSON with correction details

    -- Data quality
    iv_data_points INTEGER,
    curve_quality_score DECIMAL(5,2),
    curve_quality_rating VARCHAR(20),
    data_quality_issues JSONB,

    -- Uncertainty
    uncertainty_voc DECIMAL(6,4),  -- V
    uncertainty_isc DECIMAL(6,4),  -- A
    uncertainty_pmax DECIMAL(6,3),  -- W
    uncertainty_budget JSONB,  -- Complete uncertainty analysis

    -- Validation results
    power_tolerance_pass BOOLEAN,
    power_deviation_percent DECIMAL(5,2),
    voc_deviation_pass BOOLEAN,
    voc_deviation_percent DECIMAL(5,2),
    isc_deviation_pass BOOLEAN,
    isc_deviation_percent DECIMAL(5,2),
    ff_minimum_pass BOOLEAN,
    repeatability_pass BOOLEAN,

    -- Overall status
    test_status VARCHAR(20) NOT NULL,  -- in_progress, completed, failed, cancelled
    pass_fail VARCHAR(10),  -- PASS, FAIL
    failed_criteria JSONB,  -- Array of failed criteria
    recommendations TEXT,

    -- File references
    raw_data_file_id INTEGER REFERENCES files(id),
    raw_data_file_path VARCHAR(500),
    raw_data_file_hash VARCHAR(64),  -- SHA-256 hash for integrity
    report_file_id INTEGER REFERENCES files(id),
    report_file_path VARCHAR(500),

    -- Traceability
    operator_id INTEGER REFERENCES users(id),
    reviewer_id INTEGER REFERENCES users(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    approved_at TIMESTAMP,

    -- Review and approval
    review_status VARCHAR(20),  -- pending, approved, rejected
    review_comments TEXT,

    -- Audit trail
    audit_trail JSONB,  -- Complete audit trail in JSON format

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_irradiance CHECK (irradiance >= 800 AND irradiance <= 1200),
    CONSTRAINT chk_cell_temperature CHECK (cell_temperature >= 15 AND cell_temperature <= 35),
    CONSTRAINT chk_fill_factor CHECK (fill_factor >= 0 AND fill_factor <= 1),
    CONSTRAINT chk_test_status CHECK (test_status IN ('in_progress', 'completed', 'failed', 'cancelled')),
    CONSTRAINT chk_pass_fail CHECK (pass_fail IN ('PASS', 'FAIL') OR pass_fail IS NULL)
);

-- Indexes for performance
CREATE INDEX idx_stc_test_id ON stc_test_executions(test_id);
CREATE INDEX idx_stc_sample_id ON stc_test_executions(sample_id);
CREATE INDEX idx_stc_test_status ON stc_test_executions(test_status);
CREATE INDEX idx_stc_pass_fail ON stc_test_executions(pass_fail);
CREATE INDEX idx_stc_started_at ON stc_test_executions(started_at);
CREATE INDEX idx_stc_operator_id ON stc_test_executions(operator_id);
CREATE INDEX idx_stc_reviewer_id ON stc_test_executions(reviewer_id);

-- ========================================
-- Table: iv_curve_data
-- Description: Stores raw I-V curve data points
-- ========================================
CREATE TABLE IF NOT EXISTS iv_curve_data (
    id SERIAL PRIMARY KEY,
    test_execution_id INTEGER REFERENCES stc_test_executions(id) ON DELETE CASCADE,
    point_number INTEGER NOT NULL,
    voltage DECIMAL(8,4) NOT NULL,  -- V
    current DECIMAL(8,4) NOT NULL,  -- A
    power DECIMAL(10,4),  -- W (calculated)
    timestamp_offset_ms INTEGER,  -- Offset from test start in milliseconds

    UNIQUE(test_execution_id, point_number)
);

CREATE INDEX idx_iv_curve_test_id ON iv_curve_data(test_execution_id);

-- ========================================
-- Table: files
-- Description: Stores file metadata
-- ========================================
CREATE TABLE IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(50) UNIQUE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64),  -- SHA-256
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER REFERENCES users(id),
    description TEXT,
    metadata JSONB
);

CREATE INDEX idx_files_file_id ON files(file_id);
CREATE INDEX idx_files_file_type ON files(file_type);

-- ========================================
-- Table: test_repeatability
-- Description: Stores repeat measurements for repeatability analysis
-- ========================================
CREATE TABLE IF NOT EXISTS test_repeatability (
    id SERIAL PRIMARY KEY,
    sample_id INTEGER REFERENCES samples(id),
    test_date DATE NOT NULL,
    measurement_number INTEGER NOT NULL,
    test_execution_id INTEGER REFERENCES stc_test_executions(id),
    pmax DECIMAL(7,2),
    voc DECIMAL(6,3),
    isc DECIMAL(6,3),
    fill_factor DECIMAL(5,4),

    UNIQUE(sample_id, test_date, measurement_number)
);

CREATE INDEX idx_repeatability_sample ON test_repeatability(sample_id);
CREATE INDEX idx_repeatability_date ON test_repeatability(test_date);

-- ========================================
-- Table: audit_log
-- Description: System-wide audit log
-- ========================================
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL,  -- create, read, update, delete, approve, reject
    table_name VARCHAR(100),
    record_id INTEGER,
    action_description TEXT,
    ip_address VARCHAR(45),
    session_id VARCHAR(100),
    data_before JSONB,
    data_after JSONB,
    metadata JSONB
);

CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_action_type ON audit_log(action_type);
CREATE INDEX idx_audit_table_name ON audit_log(table_name);

-- ========================================
-- Views
-- ========================================

-- View: Latest test results for each sample
CREATE OR REPLACE VIEW vw_latest_stc_results AS
SELECT DISTINCT ON (s.id)
    s.id as sample_id,
    s.serial_number,
    s.manufacturer,
    s.model,
    s.technology,
    s.rated_power,
    t.test_id,
    t.pmax,
    t.voc,
    t.isc,
    t.fill_factor,
    t.efficiency,
    t.pass_fail,
    t.completed_at,
    t.operator_id,
    u.full_name as operator_name
FROM samples s
LEFT JOIN stc_test_executions t ON s.id = t.sample_id
LEFT JOIN users u ON t.operator_id = u.id
WHERE t.test_status = 'completed'
ORDER BY s.id, t.completed_at DESC;

-- View: Equipment calibration status
CREATE OR REPLACE VIEW vw_equipment_calibration_status AS
SELECT
    equipment_id,
    name,
    equipment_type,
    calibration_date,
    calibration_due_date,
    CASE
        WHEN calibration_due_date < CURRENT_DATE THEN 'EXPIRED'
        WHEN calibration_due_date < CURRENT_DATE + INTERVAL '30 days' THEN 'DUE_SOON'
        ELSE 'VALID'
    END as calibration_status,
    CURRENT_DATE - calibration_due_date as days_overdue,
    status
FROM equipment;

-- View: Test statistics by technology
CREATE OR REPLACE VIEW vw_test_stats_by_technology AS
SELECT
    s.technology,
    COUNT(t.id) as total_tests,
    COUNT(CASE WHEN t.pass_fail = 'PASS' THEN 1 END) as passed_tests,
    COUNT(CASE WHEN t.pass_fail = 'FAIL' THEN 1 END) as failed_tests,
    ROUND(AVG(t.pmax), 2) as avg_pmax,
    ROUND(AVG(t.fill_factor), 4) as avg_fill_factor,
    ROUND(AVG(t.efficiency), 2) as avg_efficiency,
    MIN(t.completed_at) as first_test_date,
    MAX(t.completed_at) as last_test_date
FROM samples s
JOIN stc_test_executions t ON s.id = t.sample_id
WHERE t.test_status = 'completed'
GROUP BY s.technology;

-- ========================================
-- Functions
-- ========================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_samples_updated_at
    BEFORE UPDATE ON samples
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equipment_updated_at
    BEFORE UPDATE ON equipment
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stc_test_executions_updated_at
    BEFORE UPDATE ON stc_test_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Generate test ID
CREATE OR REPLACE FUNCTION generate_test_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.test_id IS NULL OR NEW.test_id = '' THEN
        NEW.test_id := 'STC-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' ||
                       LPAD(NEXTVAL('stc_test_id_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Sequence for test ID
CREATE SEQUENCE IF NOT EXISTS stc_test_id_seq START 1;

-- Trigger for test ID generation
CREATE TRIGGER generate_stc_test_id
    BEFORE INSERT ON stc_test_executions
    FOR EACH ROW
    EXECUTE FUNCTION generate_test_id();

-- ========================================
-- Sample data for development/testing
-- ========================================

-- Insert sample users
INSERT INTO users (user_id, username, full_name, email, role, status)
VALUES
    ('USR001', 'operator1', 'John Doe', 'john.doe@example.com', 'operator', 'active'),
    ('USR002', 'reviewer1', 'Jane Smith', 'jane.smith@example.com', 'reviewer', 'active'),
    ('USR003', 'admin1', 'Bob Johnson', 'bob.johnson@example.com', 'admin', 'active')
ON CONFLICT (user_id) DO NOTHING;

-- Insert sample equipment
INSERT INTO equipment (equipment_id, name, equipment_type, manufacturer, model, calibration_date, calibration_due_date, status)
VALUES
    ('SS-001', 'Solar Simulator A', 'solar_simulator', 'PASAN', 'HighLIGHT CLD', '2024-06-01', '2025-06-01', 'active'),
    ('IV-001', 'I-V Tracer A', 'iv_tracer', 'Keysight', 'B2900A', '2024-06-10', '2025-06-10', 'active'),
    ('TS-001', 'Thermocouple A', 'temperature_sensor', 'Omega', 'Type K', '2024-06-15', '2025-06-15', 'active'),
    ('PY-001', 'Pyranometer A', 'pyranometer', 'Kipp & Zonen', 'CMP11', '2024-06-20', '2025-06-20', 'active')
ON CONFLICT (equipment_id) DO NOTHING;

-- Comments
COMMENT ON TABLE samples IS 'PV module samples under test';
COMMENT ON TABLE equipment IS 'Test equipment inventory and calibration tracking';
COMMENT ON TABLE users IS 'System users including operators, reviewers, and administrators';
COMMENT ON TABLE stc_test_executions IS 'STC-001 protocol test executions and results';
COMMENT ON TABLE iv_curve_data IS 'Raw I-V curve measurement points';
COMMENT ON TABLE files IS 'File storage metadata for data files and reports';
COMMENT ON TABLE test_repeatability IS 'Repeat measurements for statistical analysis';
COMMENT ON TABLE audit_log IS 'System-wide audit trail for compliance';

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO test_operator;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO test_reviewer;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_admin;

-- End of migration
