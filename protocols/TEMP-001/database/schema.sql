-- TEMP-001 Temperature Coefficient Testing Protocol
-- Database Schema for IEC 60891 Test Data
-- Author: ASA PV Testing
-- Date: 2025-11-14

-- ============================================================================
-- BASE TABLES (Shared across protocols)
-- ============================================================================

-- Protocols registry
CREATE TABLE IF NOT EXISTS protocols (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(50) UNIQUE NOT NULL,
    protocol_name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    category VARCHAR(100),
    standard_reference VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on protocol_id for fast lookups
CREATE INDEX idx_protocols_protocol_id ON protocols(protocol_id);

-- Test sessions
CREATE TABLE IF NOT EXISTS tests (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL,
    test_number VARCHAR(100) UNIQUE NOT NULL,
    test_date TIMESTAMP NOT NULL,
    operator VARCHAR(100),
    laboratory VARCHAR(255),
    module_id VARCHAR(100),
    module_manufacturer VARCHAR(255),
    module_model VARCHAR(255),
    module_serial_number VARCHAR(100),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed', 'failed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id) ON DELETE RESTRICT
);

-- Create indexes for common queries
CREATE INDEX idx_tests_protocol_id ON tests(protocol_id);
CREATE INDEX idx_tests_test_number ON tests(test_number);
CREATE INDEX idx_tests_test_date ON tests(test_date);
CREATE INDEX idx_tests_module_id ON tests(module_id);
CREATE INDEX idx_tests_status ON tests(status);

-- ============================================================================
-- TEMP-001 SPECIFIC TABLES
-- ============================================================================

-- Temperature coefficient measurements
CREATE TABLE IF NOT EXISTS temp_001_measurements (
    id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    measurement_number INT NOT NULL,
    measurement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Temperature measurements
    module_temperature DECIMAL(6, 2) NOT NULL,  -- °C
    ambient_temperature DECIMAL(6, 2),           -- °C

    -- Irradiance
    irradiance DECIMAL(8, 2) NOT NULL,           -- W/m²

    -- I-V curve parameters
    voc DECIMAL(8, 4) NOT NULL,                  -- V (Open Circuit Voltage)
    isc DECIMAL(8, 4) NOT NULL,                  -- A (Short Circuit Current)
    vmp DECIMAL(8, 4) NOT NULL,                  -- V (Voltage at Max Power)
    imp DECIMAL(8, 4) NOT NULL,                  -- A (Current at Max Power)
    pmax DECIMAL(10, 3) NOT NULL,                -- W (Maximum Power)

    -- Derived parameters
    fill_factor DECIMAL(6, 3),                   -- % (Fill Factor)
    series_resistance DECIMAL(8, 5),             -- Ω (Series Resistance)
    shunt_resistance DECIMAL(10, 3),             -- Ω (Shunt Resistance)

    -- Quality indicators
    measurement_quality VARCHAR(50) DEFAULT 'good' CHECK (measurement_quality IN ('good', 'warning', 'poor')),
    notes TEXT,

    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
    CONSTRAINT unique_test_measurement UNIQUE (test_id, measurement_number)
);

-- Create indexes for performance
CREATE INDEX idx_temp001_meas_test_id ON temp_001_measurements(test_id);
CREATE INDEX idx_temp001_meas_timestamp ON temp_001_measurements(measurement_timestamp);
CREATE INDEX idx_temp001_meas_temp ON temp_001_measurements(module_temperature);

-- Temperature coefficient calculation results
CREATE TABLE IF NOT EXISTS temp_001_calculations (
    id SERIAL PRIMARY KEY,
    test_id INT NOT NULL UNIQUE,

    -- Power temperature coefficients
    alpha_pmp_relative DECIMAL(10, 6) NOT NULL,  -- %/°C (relative)
    alpha_pmp_absolute DECIMAL(10, 6) NOT NULL,  -- W/°C (absolute)
    pmp_slope DECIMAL(12, 6),                    -- Linear regression slope
    pmp_intercept DECIMAL(12, 6),                -- Linear regression intercept
    r_squared_pmp DECIMAL(8, 6),                 -- R² for power regression

    -- Voltage temperature coefficients
    beta_voc_relative DECIMAL(10, 6) NOT NULL,   -- %/°C (relative)
    beta_voc_absolute DECIMAL(10, 7) NOT NULL,   -- V/°C (absolute)
    voc_slope DECIMAL(12, 7),                    -- Linear regression slope
    voc_intercept DECIMAL(12, 6),                -- Linear regression intercept
    r_squared_voc DECIMAL(8, 6),                 -- R² for voltage regression

    -- Current temperature coefficients
    alpha_isc_relative DECIMAL(10, 6) NOT NULL,  -- %/°C (relative)
    alpha_isc_absolute DECIMAL(10, 7) NOT NULL,  -- A/°C (absolute)
    isc_slope DECIMAL(12, 7),                    -- Linear regression slope
    isc_intercept DECIMAL(12, 6),                -- Linear regression intercept
    r_squared_isc DECIMAL(8, 6),                 -- R² for current regression

    -- STC-corrected values (25°C, 1000 W/m²)
    pmp_at_stc DECIMAL(10, 3),                   -- W
    voc_at_stc DECIMAL(8, 4),                    -- V
    isc_at_stc DECIMAL(8, 4),                    -- A

    -- Reference conditions
    reference_temperature DECIMAL(5, 2) DEFAULT 25.0,  -- °C
    reference_irradiance DECIMAL(8, 2) DEFAULT 1000.0, -- W/m²

    -- Data quality metrics
    num_points INT,                              -- Number of data points used
    temperature_range DECIMAL(6, 2),             -- °C (temperature span)

    -- Calculation metadata
    calculation_method VARCHAR(100) DEFAULT 'IEC 60891 Linear Regression',
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculated_by VARCHAR(100),

    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

-- Create index on test_id for lookups
CREATE INDEX idx_temp001_calc_test_id ON temp_001_calculations(test_id);

-- Quality check results
CREATE TABLE IF NOT EXISTS temp_001_quality_checks (
    id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    check_id VARCHAR(100) NOT NULL,
    check_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pass', 'warning', 'fail', 'info')),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'warning', 'info')),
    message TEXT,
    details JSONB,  -- Store additional check details in JSON format
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_temp001_qc_test_id ON temp_001_quality_checks(test_id);
CREATE INDEX idx_temp001_qc_status ON temp_001_quality_checks(status);
CREATE INDEX idx_temp001_qc_severity ON temp_001_quality_checks(severity);

-- Equipment calibration tracking
CREATE TABLE IF NOT EXISTS temp_001_equipment (
    id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    equipment_id VARCHAR(100) NOT NULL,
    equipment_name VARCHAR(255) NOT NULL,
    equipment_type VARCHAR(100),
    manufacturer VARCHAR(255),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    calibration_date DATE,
    calibration_due_date DATE,
    calibration_status VARCHAR(50) CHECK (calibration_status IN ('valid', 'expired', 'unknown')),
    calibration_certificate VARCHAR(255),
    notes TEXT,

    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

CREATE INDEX idx_temp001_equip_test_id ON temp_001_equipment(test_id);
CREATE INDEX idx_temp001_equip_cal_status ON temp_001_equipment(calibration_status);

-- Test reports
CREATE TABLE IF NOT EXISTS temp_001_reports (
    id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('pdf', 'html', 'json', 'excel')),
    report_title VARCHAR(255),
    file_path VARCHAR(500),
    file_size_kb INT,
    content_hash VARCHAR(64),  -- SHA-256 hash for integrity verification
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(100),

    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

CREATE INDEX idx_temp001_reports_test_id ON temp_001_reports(test_id);
CREATE INDEX idx_temp001_reports_type ON temp_001_reports(report_type);

-- ============================================================================
-- I-V CURVE DATA (Optional - for detailed analysis)
-- ============================================================================

-- Full I-V curve data points
CREATE TABLE IF NOT EXISTS temp_001_iv_curves (
    id SERIAL PRIMARY KEY,
    measurement_id INT NOT NULL,
    point_number INT NOT NULL,
    voltage DECIMAL(8, 4) NOT NULL,  -- V
    current DECIMAL(8, 4) NOT NULL,  -- A
    power DECIMAL(10, 3),            -- W

    FOREIGN KEY (measurement_id) REFERENCES temp_001_measurements(id) ON DELETE CASCADE,
    CONSTRAINT unique_measurement_point UNIQUE (measurement_id, point_number)
);

CREATE INDEX idx_temp001_iv_meas_id ON temp_001_iv_curves(measurement_id);

-- ============================================================================
-- VIEWS FOR CONVENIENT DATA ACCESS
-- ============================================================================

-- Complete test results view
CREATE OR REPLACE VIEW temp_001_test_results AS
SELECT
    t.id AS test_id,
    t.test_number,
    t.test_date,
    t.operator,
    t.laboratory,
    t.module_id,
    t.module_manufacturer,
    t.module_model,
    t.status,
    c.alpha_pmp_relative,
    c.alpha_pmp_absolute,
    c.beta_voc_relative,
    c.beta_voc_absolute,
    c.alpha_isc_relative,
    c.alpha_isc_absolute,
    c.pmp_at_stc,
    c.voc_at_stc,
    c.isc_at_stc,
    c.r_squared_pmp,
    c.r_squared_voc,
    c.r_squared_isc,
    c.num_points,
    c.temperature_range,
    c.calculated_at,
    COUNT(DISTINCT m.id) AS num_measurements,
    MIN(m.module_temperature) AS min_temperature,
    MAX(m.module_temperature) AS max_temperature
FROM tests t
LEFT JOIN temp_001_calculations c ON t.id = c.test_id
LEFT JOIN temp_001_measurements m ON t.id = m.test_id
WHERE t.protocol_id = 'TEMP-001'
GROUP BY t.id, c.id;

-- Quality check summary view
CREATE OR REPLACE VIEW temp_001_quality_summary AS
SELECT
    test_id,
    COUNT(*) AS total_checks,
    SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) AS passed,
    SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) AS warnings,
    SUM(CASE WHEN status = 'fail' THEN 1 ELSE 0 END) AS failures,
    SUM(CASE WHEN severity = 'critical' AND status = 'fail' THEN 1 ELSE 0 END) AS critical_failures
FROM temp_001_quality_checks
GROUP BY test_id;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to relevant tables
CREATE TRIGGER update_protocols_updated_at BEFORE UPDATE ON protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tests_updated_at BEFORE UPDATE ON tests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_temp001_measurements_updated_at BEFORE UPDATE ON temp_001_measurements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_temp001_calculations_updated_at BEFORE UPDATE ON temp_001_calculations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE DATA / SEED DATA (for testing)
-- ============================================================================

-- Insert TEMP-001 protocol
INSERT INTO protocols (protocol_id, protocol_name, version, category, standard_reference, description)
VALUES (
    'TEMP-001',
    'Temperature Coefficient Testing',
    '1.0.0',
    'Performance',
    'IEC 60891:2021',
    'Measures temperature coefficients of photovoltaic modules according to IEC 60891 procedures'
)
ON CONFLICT (protocol_id) DO NOTHING;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE protocols IS 'Registry of all testing protocols in the system';
COMMENT ON TABLE tests IS 'Individual test sessions across all protocols';
COMMENT ON TABLE temp_001_measurements IS 'Raw measurement data for TEMP-001 temperature coefficient tests';
COMMENT ON TABLE temp_001_calculations IS 'Calculated temperature coefficients and regression results';
COMMENT ON TABLE temp_001_quality_checks IS 'Quality check results for data validation';
COMMENT ON TABLE temp_001_equipment IS 'Equipment used in tests with calibration tracking';
COMMENT ON TABLE temp_001_reports IS 'Generated test reports in various formats';
COMMENT ON TABLE temp_001_iv_curves IS 'Detailed I-V curve data points for analysis';

COMMENT ON COLUMN temp_001_calculations.alpha_pmp_relative IS 'Power temperature coefficient in %/°C (IEC 60891)';
COMMENT ON COLUMN temp_001_calculations.beta_voc_relative IS 'Voltage temperature coefficient in %/°C (IEC 60891)';
COMMENT ON COLUMN temp_001_calculations.alpha_isc_relative IS 'Current temperature coefficient in %/°C (IEC 60891)';
COMMENT ON COLUMN temp_001_calculations.pmp_at_stc IS 'Maximum power corrected to STC (25°C, 1000 W/m²)';
