-- UV-001 UV Preconditioning Protocol Database Schema
-- IEC 61215 MQT 10 - Complete data traceability
-- Version: 1.0
-- Date: 2025-11-14

-- =============================================================================
-- Test Sessions Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_test_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    protocol_id VARCHAR(20) NOT NULL DEFAULT 'UV-001',
    protocol_version VARCHAR(10) NOT NULL DEFAULT '1.0',

    -- Session metadata
    sample_id VARCHAR(100) NOT NULL,
    operator VARCHAR(100) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'in_progress', 'paused', 'completed', 'failed', 'aborted')),

    -- Calculated metrics
    cumulative_uv_dose DECIMAL(10, 4) DEFAULT 0.0, -- kWh/m²
    total_exposure_time DECIMAL(10, 2) DEFAULT 0.0, -- hours
    average_irradiance DECIMAL(10, 2) DEFAULT 0.0, -- W/m²

    -- Test notes and observations
    notes TEXT,
    abort_reason TEXT,

    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),

    -- Indexes
    INDEX idx_sample_id (sample_id),
    INDEX idx_start_time (start_time),
    INDEX idx_status (status)
);

-- =============================================================================
-- Irradiance Measurements Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_irradiance_measurements (
    measurement_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Irradiance data
    uv_irradiance DECIMAL(10, 2) NOT NULL, -- W/m²
    sensor_temperature DECIMAL(6, 2), -- °C

    -- Uniformity measurements (multiple sensor points)
    uniformity_point_1 DECIMAL(10, 2),
    uniformity_point_2 DECIMAL(10, 2),
    uniformity_point_3 DECIMAL(10, 2),
    uniformity_point_4 DECIMAL(10, 2),
    uniformity_deviation DECIMAL(6, 2), -- % deviation

    -- Compliance flags
    compliance_status VARCHAR(20) CHECK (compliance_status IN ('compliant', 'out_of_spec', 'warning')),

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- =============================================================================
-- Environmental Measurements Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_environmental_measurements (
    measurement_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Temperature data
    module_temperature DECIMAL(6, 2) NOT NULL, -- °C
    ambient_temperature DECIMAL(6, 2) NOT NULL, -- °C

    -- Additional environmental parameters
    relative_humidity DECIMAL(5, 2) NOT NULL, -- %
    air_velocity DECIMAL(6, 2), -- m/s
    barometric_pressure DECIMAL(7, 2), -- kPa

    -- Multi-point temperature measurements
    temp_center DECIMAL(6, 2),
    temp_corner_1 DECIMAL(6, 2),
    temp_corner_2 DECIMAL(6, 2),
    temp_corner_3 DECIMAL(6, 2),
    temp_corner_4 DECIMAL(6, 2),
    temp_uniformity DECIMAL(6, 2), -- °C deviation

    -- Compliance flags
    module_temp_compliant BOOLEAN,
    ambient_temp_compliant BOOLEAN,
    humidity_compliant BOOLEAN,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- =============================================================================
-- Spectral Measurements Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_spectral_measurements (
    measurement_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Spectral summary data
    total_uv_irradiance DECIMAL(10, 2) NOT NULL, -- W/m²
    peak_wavelength DECIMAL(6, 2) NOT NULL, -- nm
    uv_a_percentage DECIMAL(5, 2) NOT NULL, -- %
    uv_b_percentage DECIMAL(5, 2) NOT NULL, -- %

    -- Full spectral data (JSON for detailed wavelength-irradiance pairs)
    spectral_data_json TEXT, -- JSON array of {wavelength, irradiance}

    -- Compliance flags
    peak_wavelength_compliant BOOLEAN,
    uva_compliant BOOLEAN,
    uvb_compliant BOOLEAN,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- =============================================================================
-- Electrical Characterization Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_electrical_characterization (
    characterization_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    measurement_type VARCHAR(20) NOT NULL CHECK (measurement_type IN ('pre_test', 'post_test', 'intermediate')),
    timestamp TIMESTAMP NOT NULL,

    -- I-V parameters
    open_circuit_voltage DECIMAL(8, 4) NOT NULL, -- V (Voc)
    short_circuit_current DECIMAL(8, 4) NOT NULL, -- A (Isc)
    maximum_power DECIMAL(10, 4) NOT NULL, -- W (Pmax)
    voltage_at_max_power DECIMAL(8, 4), -- V (Vmp)
    current_at_max_power DECIMAL(8, 4), -- A (Imp)
    fill_factor DECIMAL(6, 4) NOT NULL, -- dimensionless (FF)

    -- Additional parameters
    efficiency DECIMAL(6, 3), -- %
    series_resistance DECIMAL(10, 6), -- Ω
    shunt_resistance DECIMAL(12, 4), -- Ω

    -- I-V curve data (JSON for full curve)
    iv_curve_json TEXT, -- JSON array of {voltage, current}

    -- Test conditions
    irradiance DECIMAL(8, 2), -- W/m²
    module_temperature DECIMAL(6, 2), -- °C
    spectrum_type VARCHAR(20), -- e.g., 'AM1.5'

    -- Insulation resistance
    insulation_resistance DECIMAL(10, 2), -- MΩ
    insulation_compliant BOOLEAN,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_type (session_id, measurement_type),
    INDEX idx_timestamp (timestamp)
);

-- =============================================================================
-- Visual Inspection Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_visual_inspections (
    inspection_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    inspection_type VARCHAR(20) NOT NULL CHECK (inspection_type IN ('pre_test', 'post_test', 'intermediate')),
    timestamp TIMESTAMP NOT NULL,
    inspector VARCHAR(100) NOT NULL,

    -- Defect observations
    discoloration BOOLEAN DEFAULT FALSE,
    discoloration_description TEXT,
    delamination BOOLEAN DEFAULT FALSE,
    delamination_description TEXT,
    bubbles_blisters BOOLEAN DEFAULT FALSE,
    bubbles_description TEXT,
    edge_seal_degradation BOOLEAN DEFAULT FALSE,
    edge_seal_description TEXT,
    cell_cracks BOOLEAN DEFAULT FALSE,
    cell_cracks_description TEXT,
    junction_box_issues BOOLEAN DEFAULT FALSE,
    junction_box_description TEXT,

    -- Overall assessment
    overall_condition VARCHAR(20) CHECK (overall_condition IN ('excellent', 'good', 'acceptable', 'poor', 'failed')),
    major_defects_found BOOLEAN DEFAULT FALSE,
    general_notes TEXT,

    -- Photo documentation
    photo_urls TEXT, -- JSON array of photo URLs/paths

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_type (session_id, inspection_type)
);

-- =============================================================================
-- Test Events and Incidents Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_test_events (
    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- 'alarm', 'warning', 'info', 'error', 'operator_action'
    severity VARCHAR(20) CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),

    -- Event details
    event_description TEXT NOT NULL,
    parameter_name VARCHAR(100),
    parameter_value VARCHAR(100),
    expected_value VARCHAR(100),

    -- Response
    action_taken TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_severity (severity),
    INDEX idx_event_type (event_type)
);

-- =============================================================================
-- Test Results and Analysis Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_test_results (
    result_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE,

    -- UV dose compliance
    final_uv_dose DECIMAL(10, 4) NOT NULL, -- kWh/m²
    target_uv_dose DECIMAL(10, 4) NOT NULL, -- kWh/m²
    dose_tolerance DECIMAL(6, 4) NOT NULL, -- ±%
    dose_compliant BOOLEAN NOT NULL,

    -- Performance degradation
    power_degradation_percentage DECIMAL(6, 3), -- %
    voc_degradation_percentage DECIMAL(6, 3), -- %
    isc_degradation_percentage DECIMAL(6, 3), -- %
    ff_degradation_percentage DECIMAL(6, 3), -- %

    -- Acceptance criteria
    max_power_degradation_limit DECIMAL(6, 3) DEFAULT 5.0, -- %
    power_degradation_pass BOOLEAN,

    min_insulation_resistance_limit DECIMAL(10, 2) DEFAULT 40.0, -- MΩ
    insulation_resistance_pass BOOLEAN,

    visual_inspection_pass BOOLEAN,

    -- Overall result
    overall_pass BOOLEAN NOT NULL,
    test_status VARCHAR(20) CHECK (test_status IN ('pass', 'fail', 'conditional_pass', 'inconclusive')),

    -- Quality metrics
    data_completeness_percentage DECIMAL(5, 2), -- %
    measurement_count_irradiance INT,
    measurement_count_environmental INT,
    measurement_count_spectral INT,

    -- Analysis notes
    analysis_notes TEXT,
    recommendations TEXT,

    -- Analyst information
    analyzed_by VARCHAR(100),
    analyzed_at TIMESTAMP,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE
);

-- =============================================================================
-- Equipment and Calibration Tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_equipment_usage (
    usage_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,

    -- Equipment details
    equipment_type VARCHAR(50) NOT NULL, -- 'uv_chamber', 'radiometer', 'temperature_sensor', etc.
    equipment_id VARCHAR(100) NOT NULL,
    equipment_name VARCHAR(200),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),

    -- Calibration status
    last_calibration_date DATE,
    calibration_due_date DATE,
    calibration_certificate_number VARCHAR(100),
    calibration_valid BOOLEAN,

    -- Usage details
    usage_start TIMESTAMP,
    usage_end TIMESTAMP,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_equipment (session_id, equipment_type),
    INDEX idx_equipment_id (equipment_id)
);

-- =============================================================================
-- Data Quality and Validation Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS uv001_data_quality (
    quality_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    check_timestamp TIMESTAMP NOT NULL,
    check_type VARCHAR(50) NOT NULL, -- 'completeness', 'consistency', 'accuracy', 'validity'

    -- Quality metrics
    parameter_name VARCHAR(100),
    expected_count INT,
    actual_count INT,
    missing_count INT,
    out_of_range_count INT,

    -- Quality score
    quality_score DECIMAL(5, 2), -- 0-100%
    quality_status VARCHAR(20) CHECK (quality_status IN ('excellent', 'good', 'acceptable', 'poor', 'failed')),

    -- Issue details
    issues_found TEXT,
    corrective_actions TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES uv001_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_check (session_id, check_timestamp)
);

-- =============================================================================
-- Triggers for automatic timestamp updates
-- =============================================================================

DELIMITER $$

CREATE TRIGGER IF NOT EXISTS update_session_timestamp
BEFORE UPDATE ON uv001_test_sessions
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER IF NOT EXISTS update_results_timestamp
BEFORE UPDATE ON uv001_test_results
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

DELIMITER ;

-- =============================================================================
-- Views for common queries and reporting
-- =============================================================================

-- Session summary view
CREATE OR REPLACE VIEW uv001_session_summary AS
SELECT
    s.session_id,
    s.sample_id,
    s.operator,
    s.start_time,
    s.end_time,
    s.status,
    s.cumulative_uv_dose,
    s.total_exposure_time,
    s.average_irradiance,
    COUNT(DISTINCT i.measurement_id) as irradiance_measurement_count,
    COUNT(DISTINCT e.measurement_id) as environmental_measurement_count,
    COUNT(DISTINCT sp.measurement_id) as spectral_measurement_count,
    r.overall_pass,
    r.test_status,
    r.power_degradation_percentage
FROM uv001_test_sessions s
LEFT JOIN uv001_irradiance_measurements i ON s.session_id = i.session_id
LEFT JOIN uv001_environmental_measurements e ON s.session_id = e.session_id
LEFT JOIN uv001_spectral_measurements sp ON s.session_id = sp.session_id
LEFT JOIN uv001_test_results r ON s.session_id = r.session_id
GROUP BY s.session_id;

-- Active compliance monitoring view
CREATE OR REPLACE VIEW uv001_compliance_monitoring AS
SELECT
    s.session_id,
    s.sample_id,
    s.status,
    s.cumulative_uv_dose,
    (s.cumulative_uv_dose / 15.0 * 100) as dose_completion_percentage,
    AVG(i.uv_irradiance) as avg_irradiance,
    AVG(e.module_temperature) as avg_module_temperature,
    AVG(e.relative_humidity) as avg_humidity,
    SUM(CASE WHEN i.compliance_status = 'out_of_spec' THEN 1 ELSE 0 END) as irradiance_violations,
    SUM(CASE WHEN NOT e.module_temp_compliant THEN 1 ELSE 0 END) as temperature_violations,
    SUM(CASE WHEN NOT e.humidity_compliant THEN 1 ELSE 0 END) as humidity_violations
FROM uv001_test_sessions s
LEFT JOIN uv001_irradiance_measurements i ON s.session_id = i.session_id
LEFT JOIN uv001_environmental_measurements e ON s.session_id = e.session_id
WHERE s.status = 'in_progress'
GROUP BY s.session_id;

-- Equipment calibration status view
CREATE OR REPLACE VIEW uv001_equipment_calibration_status AS
SELECT
    equipment_id,
    equipment_name,
    equipment_type,
    manufacturer,
    model,
    serial_number,
    last_calibration_date,
    calibration_due_date,
    calibration_valid,
    DATEDIFF(calibration_due_date, CURDATE()) as days_until_due,
    COUNT(DISTINCT session_id) as usage_count
FROM uv001_equipment_usage
GROUP BY equipment_id, equipment_name, equipment_type, manufacturer, model,
         serial_number, last_calibration_date, calibration_due_date, calibration_valid;

-- =============================================================================
-- Comments for documentation
-- =============================================================================

-- Table comments
ALTER TABLE uv001_test_sessions COMMENT = 'Main test session tracking for UV-001 protocol';
ALTER TABLE uv001_irradiance_measurements COMMENT = 'UV irradiance measurements with uniformity data';
ALTER TABLE uv001_environmental_measurements COMMENT = 'Environmental conditions (temperature, humidity, etc.)';
ALTER TABLE uv001_spectral_measurements COMMENT = 'Spectral irradiance distribution measurements';
ALTER TABLE uv001_electrical_characterization COMMENT = 'Pre/post test I-V characterization data';
ALTER TABLE uv001_visual_inspections COMMENT = 'Visual inspection findings';
ALTER TABLE uv001_test_events COMMENT = 'Test events, alarms, and operator actions';
ALTER TABLE uv001_test_results COMMENT = 'Final test results and pass/fail determination';
ALTER TABLE uv001_equipment_usage COMMENT = 'Equipment usage and calibration tracking';
ALTER TABLE uv001_data_quality COMMENT = 'Data quality validation and metrics';
