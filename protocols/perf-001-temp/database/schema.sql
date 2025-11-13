-- PERF-001: Performance Testing at Different Temperatures
-- Database Schema for PostgreSQL/SQLite
-- Compatible with LIMS and QMS integration

-- =============================================================================
-- MAIN TEST TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS perf_001_tests (
    -- Primary identification
    test_id VARCHAR(50) PRIMARY KEY,
    protocol_id VARCHAR(20) DEFAULT 'PERF-001' NOT NULL,
    protocol_version VARCHAR(20) DEFAULT '1.0.0',

    -- Test specimen information
    module_id VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(200) NOT NULL,
    model VARCHAR(200) NOT NULL,
    technology VARCHAR(50),
    rated_power_stc DECIMAL(10,2),
    cell_count INTEGER,
    module_area DECIMAL(10,4),
    specimen_notes TEXT,

    -- Test conditions
    irradiance DECIMAL(10,2) DEFAULT 1000.0,
    spectrum VARCHAR(20) DEFAULT 'AM1.5G',
    reference_temperature DECIMAL(5,2) DEFAULT 25.0,

    -- Calculated results
    temp_coef_pmax DECIMAL(10,6),
    temp_coef_pmax_unit VARCHAR(10) DEFAULT '%/°C',
    temp_coef_pmax_r_squared DECIMAL(10,6),
    temp_coef_voc DECIMAL(10,6),
    temp_coef_voc_unit VARCHAR(10) DEFAULT '%/°C',
    temp_coef_voc_r_squared DECIMAL(10,6),
    temp_coef_isc DECIMAL(10,6),
    temp_coef_isc_unit VARCHAR(10) DEFAULT '%/°C',
    temp_coef_isc_r_squared DECIMAL(10,6),
    normalized_power_25c DECIMAL(10,2),

    -- Quality checks
    data_completeness BOOLEAN DEFAULT FALSE,
    measurement_stability BOOLEAN DEFAULT FALSE,
    linearity_check BOOLEAN DEFAULT FALSE,
    range_validation BOOLEAN DEFAULT FALSE,
    quality_warnings TEXT,
    quality_errors TEXT,

    -- Metadata
    test_date DATE NOT NULL,
    test_facility VARCHAR(200) NOT NULL,
    operator VARCHAR(200) NOT NULL,
    ambient_temperature DECIMAL(5,2),
    relative_humidity DECIMAL(5,2),
    barometric_pressure DECIMAL(6,2),

    -- Equipment
    solar_simulator VARCHAR(200),
    iv_tracer VARCHAR(200),
    temperature_control VARCHAR(200),
    calibration_date DATE,

    -- Project and traceability
    project_id VARCHAR(100),
    client VARCHAR(200),
    purchase_order VARCHAR(100),
    lims_id VARCHAR(100),
    qms_reference VARCHAR(100),
    parent_test_id VARCHAR(100),

    -- Audit trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    status VARCHAR(50) DEFAULT 'draft',
    notes TEXT,

    -- Indexes for common queries
    CONSTRAINT fk_parent_test FOREIGN KEY (parent_test_id)
        REFERENCES perf_001_tests(test_id) ON DELETE SET NULL
);

CREATE INDEX idx_perf001_module_id ON perf_001_tests(module_id);
CREATE INDEX idx_perf001_test_date ON perf_001_tests(test_date);
CREATE INDEX idx_perf001_project_id ON perf_001_tests(project_id);
CREATE INDEX idx_perf001_lims_id ON perf_001_tests(lims_id);
CREATE INDEX idx_perf001_status ON perf_001_tests(status);

-- =============================================================================
-- MEASUREMENTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS perf_001_measurements (
    measurement_id SERIAL PRIMARY KEY,
    test_id VARCHAR(50) NOT NULL,

    -- Temperature and electrical parameters
    temperature DECIMAL(6,2) NOT NULL,
    pmax DECIMAL(10,3) NOT NULL,
    voc DECIMAL(10,3) NOT NULL,
    isc DECIMAL(10,3) NOT NULL,
    vmp DECIMAL(10,3) NOT NULL,
    imp DECIMAL(10,3) NOT NULL,

    -- Derived parameters
    fill_factor DECIMAL(10,6),
    efficiency DECIMAL(10,4),

    -- Measurement metadata
    measurement_timestamp TIMESTAMP,
    measurement_duration DECIMAL(10,2),
    stabilization_time DECIMAL(10,2),

    -- Quality indicators
    stability_indicator VARCHAR(20),
    quality_flag VARCHAR(20),

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_test FOREIGN KEY (test_id)
        REFERENCES perf_001_tests(test_id) ON DELETE CASCADE
);

CREATE INDEX idx_measurements_test_id ON perf_001_measurements(test_id);
CREATE INDEX idx_measurements_temperature ON perf_001_measurements(temperature);

-- =============================================================================
-- IV CURVE DATA TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS perf_001_iv_curves (
    curve_id SERIAL PRIMARY KEY,
    measurement_id INTEGER NOT NULL,
    test_id VARCHAR(50) NOT NULL,

    -- IV curve data (stored as JSON array or separate rows)
    voltage_data TEXT NOT NULL,  -- JSON array of voltage points
    current_data TEXT NOT NULL,  -- JSON array of current points
    power_data TEXT,             -- JSON array of power points (optional)

    -- Curve metadata
    num_points INTEGER,
    sweep_rate DECIMAL(10,4),
    reverse_sweep BOOLEAN DEFAULT FALSE,

    -- Quality
    curve_quality VARCHAR(20),

    CONSTRAINT fk_measurement FOREIGN KEY (measurement_id)
        REFERENCES perf_001_measurements(measurement_id) ON DELETE CASCADE,
    CONSTRAINT fk_test_curve FOREIGN KEY (test_id)
        REFERENCES perf_001_tests(test_id) ON DELETE CASCADE
);

CREATE INDEX idx_iv_curves_measurement ON perf_001_iv_curves(measurement_id);

-- =============================================================================
-- RELATED TESTS TABLE (for traceability)
-- =============================================================================

CREATE TABLE IF NOT EXISTS perf_001_related_tests (
    relation_id SERIAL PRIMARY KEY,
    test_id VARCHAR(50) NOT NULL,
    related_test_id VARCHAR(50) NOT NULL,
    relation_type VARCHAR(50),  -- e.g., 'prerequisite', 'follow-up', 'comparison'
    notes TEXT,

    CONSTRAINT fk_main_test FOREIGN KEY (test_id)
        REFERENCES perf_001_tests(test_id) ON DELETE CASCADE
);

CREATE INDEX idx_related_tests ON perf_001_related_tests(test_id);

-- =============================================================================
-- REVISION HISTORY TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS perf_001_revisions (
    revision_id SERIAL PRIMARY KEY,
    test_id VARCHAR(50) NOT NULL,
    revision_number VARCHAR(20) NOT NULL,
    revision_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author VARCHAR(100) NOT NULL,
    changes TEXT NOT NULL,
    previous_data TEXT,  -- JSON snapshot of previous state

    CONSTRAINT fk_test_revision FOREIGN KEY (test_id)
        REFERENCES perf_001_tests(test_id) ON DELETE CASCADE
);

CREATE INDEX idx_revisions_test ON perf_001_revisions(test_id);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View: Complete test results with all measurements
CREATE VIEW IF NOT EXISTS v_perf_001_complete AS
SELECT
    t.*,
    COUNT(m.measurement_id) as num_measurements,
    MIN(m.temperature) as min_temperature,
    MAX(m.temperature) as max_temperature,
    AVG(m.pmax) as avg_pmax,
    AVG(m.fill_factor) as avg_fill_factor
FROM perf_001_tests t
LEFT JOIN perf_001_measurements m ON t.test_id = m.test_id
GROUP BY t.test_id;

-- View: Test summary for dashboards
CREATE VIEW IF NOT EXISTS v_perf_001_summary AS
SELECT
    test_id,
    module_id,
    manufacturer,
    model,
    test_date,
    operator,
    temp_coef_pmax,
    temp_coef_pmax_r_squared,
    status,
    data_completeness,
    linearity_check
FROM perf_001_tests
ORDER BY test_date DESC;

-- View: Quality control dashboard
CREATE VIEW IF NOT EXISTS v_perf_001_qc AS
SELECT
    test_id,
    module_id,
    test_date,
    data_completeness,
    measurement_stability,
    linearity_check,
    range_validation,
    temp_coef_pmax_r_squared,
    quality_warnings,
    quality_errors,
    status
FROM perf_001_tests
WHERE status IN ('completed', 'under_review')
ORDER BY test_date DESC;

-- =============================================================================
-- STORED PROCEDURES / FUNCTIONS
-- =============================================================================

-- Function to calculate fill factor
CREATE OR REPLACE FUNCTION calculate_fill_factor(
    p_pmax DECIMAL,
    p_voc DECIMAL,
    p_isc DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    IF p_voc > 0 AND p_isc > 0 THEN
        RETURN p_pmax / (p_voc * p_isc);
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to validate measurement count
CREATE OR REPLACE FUNCTION validate_measurement_count()
RETURNS TRIGGER AS $$
DECLARE
    measurement_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO measurement_count
    FROM perf_001_measurements
    WHERE test_id = NEW.test_id;

    IF measurement_count < 4 THEN
        RAISE NOTICE 'Warning: Test % has fewer than 4 measurements (IEC 61853 requires minimum 4)', NEW.test_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update fill factor on insert/update
CREATE OR REPLACE FUNCTION update_fill_factor()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fill_factor := calculate_fill_factor(NEW.pmax, NEW.voc, NEW.isc);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_fill_factor
    BEFORE INSERT OR UPDATE ON perf_001_measurements
    FOR EACH ROW
    EXECUTE FUNCTION update_fill_factor();

-- Trigger to update timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_timestamp
    BEFORE UPDATE ON perf_001_tests
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- =============================================================================
-- SAMPLE DATA QUERIES
-- =============================================================================

-- Query: Find all tests with poor linearity (R² < 0.95)
-- SELECT test_id, module_id, temp_coef_pmax_r_squared
-- FROM perf_001_tests
-- WHERE temp_coef_pmax_r_squared < 0.95;

-- Query: Temperature coefficient statistics by technology
-- SELECT
--     technology,
--     COUNT(*) as test_count,
--     AVG(temp_coef_pmax) as avg_pmax_coef,
--     STDDEV(temp_coef_pmax) as std_pmax_coef
-- FROM perf_001_tests
-- WHERE status = 'completed'
-- GROUP BY technology;

-- Query: Recent tests with quality issues
-- SELECT test_id, module_id, test_date, quality_warnings, quality_errors
-- FROM perf_001_tests
-- WHERE (quality_warnings IS NOT NULL OR quality_errors IS NOT NULL)
--   AND test_date >= CURRENT_DATE - INTERVAL '30 days'
-- ORDER BY test_date DESC;

-- =============================================================================
-- PERMISSIONS (adjust as needed for your deployment)
-- =============================================================================

-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO test_operator;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO test_viewer;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_admin;
