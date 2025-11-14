-- ============================================================================
-- SAND-001 Sand/Dust Resistance Test Database Schema
-- IEC 60068-2-68 Implementation
-- Full traceability and real-time monitoring support
-- ============================================================================

-- ============================================================================
-- Test Session Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS test_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    protocol_id VARCHAR(20) NOT NULL DEFAULT 'SAND-001',
    protocol_version VARCHAR(10) NOT NULL DEFAULT '1.0.0',
    standard_reference VARCHAR(50) NOT NULL DEFAULT 'IEC 60068-2-68',

    -- Test timing
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Test status
    current_phase VARCHAR(50),
    test_status VARCHAR(20) CHECK (test_status IN ('initialized', 'running', 'paused', 'completed', 'failed', 'cancelled')),
    test_result VARCHAR(10) CHECK (test_result IN ('pass', 'fail', 'pending')),

    -- Operator and traceability
    operator_id VARCHAR(50) NOT NULL,
    operator_name VARCHAR(100),
    facility_id VARCHAR(50),
    laboratory_id VARCHAR(50),

    -- Configuration
    configuration_json TEXT,

    -- Metadata
    notes TEXT,
    created_by VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_protocol (protocol_id),
    INDEX idx_status (test_status),
    INDEX idx_dates (started_at, completed_at),
    INDEX idx_operator (operator_id)
);

-- ============================================================================
-- Specimen Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS specimens (
    specimen_id VARCHAR(50) PRIMARY KEY,
    specimen_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    manufacturer_id VARCHAR(50),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    batch_number VARCHAR(50),
    manufacturing_date DATE,

    -- Physical properties
    nominal_dimensions_length_mm DECIMAL(10,2),
    nominal_dimensions_width_mm DECIMAL(10,2),
    nominal_dimensions_height_mm DECIMAL(10,2),
    nominal_weight_g DECIMAL(10,3),

    -- Material information
    front_cover_material VARCHAR(50),
    back_cover_material VARCHAR(50),
    frame_material VARCHAR(50),
    seal_material VARCHAR(50),

    -- Traceability
    receiving_date DATE,
    storage_location VARCHAR(100),
    condition_on_receipt VARCHAR(50),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_type (specimen_type),
    INDEX idx_manufacturer (manufacturer),
    INDEX idx_serial (serial_number)
);

CREATE TABLE IF NOT EXISTS test_specimens (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    specimen_id VARCHAR(50) NOT NULL,

    -- Pre-test measurements
    initial_weight_g DECIMAL(10,3),
    initial_length_mm DECIMAL(10,2),
    initial_width_mm DECIMAL(10,2),
    initial_height_mm DECIMAL(10,2),
    initial_surface_roughness_um DECIMAL(8,3),

    -- Post-test measurements
    post_weight_g DECIMAL(10,3),
    post_length_mm DECIMAL(10,2),
    post_width_mm DECIMAL(10,2),
    post_height_mm DECIMAL(10,2),
    post_surface_roughness_um DECIMAL(8,3),
    deposited_dust_weight_g DECIMAL(10,3),

    -- Dust ingress assessment
    ingress_severity_level INT CHECK (ingress_severity_level BETWEEN 1 AND 5),
    ingress_description TEXT,
    ingress_locations TEXT, -- JSON array of locations

    -- Position in chamber
    chamber_position VARCHAR(50),
    chamber_coordinates_x_mm DECIMAL(10,2),
    chamber_coordinates_y_mm DECIMAL(10,2),
    chamber_coordinates_z_mm DECIMAL(10,2),

    -- Assessment
    visual_inspection_result TEXT,
    physical_integrity_pass BOOLEAN,
    functional_test_pass BOOLEAN,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (specimen_id) REFERENCES specimens(specimen_id),
    INDEX idx_session (session_id),
    INDEX idx_specimen (specimen_id)
);

-- ============================================================================
-- Electrical Measurements Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS electrical_measurements (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    specimen_id VARCHAR(50) NOT NULL,
    measurement_phase VARCHAR(20) NOT NULL CHECK (measurement_phase IN ('pre_test', 'post_test')),
    measurement_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Standard PV parameters
    open_circuit_voltage_v DECIMAL(10,4),
    short_circuit_current_a DECIMAL(10,4),
    max_power_w DECIMAL(10,4),
    max_power_voltage_v DECIMAL(10,4),
    max_power_current_a DECIMAL(10,4),
    fill_factor DECIMAL(6,4),
    efficiency_percent DECIMAL(6,3),

    -- Resistance measurements
    insulation_resistance_mohm DECIMAL(12,3),
    series_resistance_ohm DECIMAL(10,6),
    shunt_resistance_ohm DECIMAL(12,3),

    -- Test conditions
    irradiance_w_m2 DECIMAL(8,2),
    cell_temperature_c DECIMAL(6,2),
    ambient_temperature_c DECIMAL(6,2),

    -- Equipment
    measurement_equipment_id VARCHAR(50),
    calibration_date DATE,

    -- Metadata
    measured_by VARCHAR(50),
    notes TEXT,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (specimen_id) REFERENCES specimens(specimen_id),
    INDEX idx_session_phase (session_id, measurement_phase),
    INDEX idx_specimen (specimen_id)
);

-- ============================================================================
-- Test Configuration Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS test_configurations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL UNIQUE,

    -- Dust characteristics
    dust_type VARCHAR(100) NOT NULL,
    dust_lot_number VARCHAR(50),
    dust_certification_date DATE,
    particle_size_min_um DECIMAL(8,3),
    particle_size_max_um DECIMAL(8,3),
    particle_size_median_um DECIMAL(8,3),
    dust_concentration_kg_m3 DECIMAL(10,6),

    -- Particle composition
    sio2_percent DECIMAL(5,2),
    al2o3_percent DECIMAL(5,2),
    fe2o3_percent DECIMAL(5,2),
    other_composition_percent DECIMAL(5,2),

    -- Environmental targets
    target_temperature_c DECIMAL(6,2),
    temperature_tolerance_c DECIMAL(4,2),
    target_humidity_percent DECIMAL(5,2),
    humidity_tolerance_percent DECIMAL(4,2),
    target_air_velocity_m_s DECIMAL(6,3),
    air_velocity_tolerance_m_s DECIMAL(5,3),
    atmospheric_pressure_kpa DECIMAL(7,3),

    -- Test duration
    exposure_time_hours DECIMAL(8,2),
    number_of_cycles INT,
    settling_time_hours DECIMAL(6,2),

    -- Chamber information
    chamber_id VARCHAR(50),
    chamber_type VARCHAR(50),
    chamber_volume_m3 DECIMAL(8,3),

    -- Tracking configuration
    tracking_enabled BOOLEAN DEFAULT TRUE,
    sampling_interval_seconds INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session (session_id)
);

-- ============================================================================
-- Environmental Monitoring Tables (Time-Series Data)
-- ============================================================================

CREATE TABLE IF NOT EXISTS environmental_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Environmental parameters
    temperature_c DECIMAL(6,2),
    humidity_percent DECIMAL(5,2),
    air_velocity_m_s DECIMAL(6,3),
    atmospheric_pressure_kpa DECIMAL(7,3),
    dust_concentration_kg_m3 DECIMAL(10,6),

    -- Status flags
    in_tolerance BOOLEAN,
    temperature_in_range BOOLEAN,
    humidity_in_range BOOLEAN,
    velocity_in_range BOOLEAN,
    concentration_in_range BOOLEAN,

    -- Sensor information
    temperature_sensor_id VARCHAR(50),
    humidity_sensor_id VARCHAR(50),
    velocity_sensor_id VARCHAR(50),
    concentration_sensor_id VARCHAR(50),

    -- Quality indicators
    data_quality VARCHAR(20) CHECK (data_quality IN ('good', 'fair', 'poor', 'invalid')),

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- ============================================================================
-- Particle Tracking Tables (High-Frequency Data)
-- ============================================================================

CREATE TABLE IF NOT EXISTS measurement_points (
    point_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    point_name VARCHAR(100),

    -- Location in chamber
    x_coordinate_mm DECIMAL(10,2),
    y_coordinate_mm DECIMAL(10,2),
    z_coordinate_mm DECIMAL(10,2),
    location_description TEXT,

    -- Measurement equipment
    counter_id VARCHAR(50),
    counter_type VARCHAR(50),
    counter_serial_number VARCHAR(50),
    calibration_date DATE,

    -- Configuration
    active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session (session_id)
);

CREATE TABLE IF NOT EXISTS particle_measurements (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    point_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Particle data
    particle_size_microns DECIMAL(8,3),
    particle_count INT,
    concentration_kg_m3 DECIMAL(10,6),

    -- Velocity vector
    velocity_x_m_s DECIMAL(8,4),
    velocity_y_m_s DECIMAL(8,4),
    velocity_z_m_s DECIMAL(8,4),
    velocity_magnitude_m_s DECIMAL(8,4),

    -- Environmental at measurement point
    local_temperature_c DECIMAL(6,2),
    local_humidity_percent DECIMAL(5,2),

    -- Data quality
    measurement_quality VARCHAR(20) CHECK (measurement_quality IN ('good', 'fair', 'poor', 'invalid')),

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (point_id) REFERENCES measurement_points(point_id),
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_point_timestamp (point_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- Particle size distribution table
CREATE TABLE IF NOT EXISTS particle_size_distribution (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    point_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Size bins (cumulative)
    size_0_5_um_count INT,
    size_1_um_count INT,
    size_2_um_count INT,
    size_5_um_count INT,
    size_10_um_count INT,
    size_25_um_count INT,
    size_50_um_count INT,
    size_100_um_count INT,
    size_200_um_count INT,
    size_above_200_um_count INT,

    total_count INT,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (point_id) REFERENCES measurement_points(point_id),
    INDEX idx_session_timestamp (session_id, timestamp),
    INDEX idx_point_timestamp (point_id, timestamp)
);

-- ============================================================================
-- Test Equipment and Calibration Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS test_equipment (
    equipment_id VARCHAR(50) PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),

    -- Calibration
    last_calibration_date DATE,
    next_calibration_date DATE,
    calibration_frequency_months INT,
    calibration_certificate_number VARCHAR(50),

    -- Status
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'maintenance', 'retired')),
    location VARCHAR(100),

    -- Specifications
    measurement_range VARCHAR(100),
    accuracy VARCHAR(100),
    resolution VARCHAR(100),

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_type (equipment_type),
    INDEX idx_calibration (next_calibration_date)
);

CREATE TABLE IF NOT EXISTS equipment_usage (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    equipment_id VARCHAR(50) NOT NULL,
    usage_purpose VARCHAR(100),

    -- Usage period
    used_from TIMESTAMP,
    used_until TIMESTAMP,

    -- Verification
    pre_use_check_pass BOOLEAN,
    post_use_check_pass BOOLEAN,

    notes TEXT,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES test_equipment(equipment_id),
    INDEX idx_session (session_id),
    INDEX idx_equipment (equipment_id)
);

-- ============================================================================
-- Image and Document Storage
-- ============================================================================

CREATE TABLE IF NOT EXISTS test_images (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    specimen_id VARCHAR(50),

    -- Image information
    image_filename VARCHAR(255) NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    image_type VARCHAR(50),
    capture_timestamp TIMESTAMP NOT NULL,

    -- Test phase
    test_phase VARCHAR(50),
    image_category VARCHAR(50) CHECK (image_category IN ('pre_test', 'during_test', 'post_test', 'damage', 'ingress', 'deposition')),

    -- Image metadata
    resolution VARCHAR(20),
    file_size_kb INT,
    camera_id VARCHAR(50),

    -- Description
    description TEXT,
    annotations TEXT,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (specimen_id) REFERENCES specimens(specimen_id),
    INDEX idx_session (session_id),
    INDEX idx_specimen (specimen_id),
    INDEX idx_phase_category (test_phase, image_category)
);

CREATE TABLE IF NOT EXISTS test_documents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,

    -- Document information
    document_type VARCHAR(50) NOT NULL,
    document_filename VARCHAR(255) NOT NULL,
    document_path VARCHAR(500) NOT NULL,

    -- Document metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version VARCHAR(20),

    -- Content description
    description TEXT,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_type (document_type)
);

-- ============================================================================
-- Deviations and Observations
-- ============================================================================

CREATE TABLE IF NOT EXISTS test_deviations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    deviation_timestamp TIMESTAMP NOT NULL,

    -- Deviation details
    deviation_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('minor', 'major', 'critical')),
    description TEXT NOT NULL,

    -- Parameters involved
    parameter_name VARCHAR(50),
    expected_value VARCHAR(100),
    actual_value VARCHAR(100),

    -- Response
    corrective_action TEXT,
    action_taken_by VARCHAR(50),
    action_timestamp TIMESTAMP,

    -- Impact assessment
    impact_on_test TEXT,
    test_validity_affected BOOLEAN,

    -- Resolution
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved)
);

CREATE TABLE IF NOT EXISTS test_observations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    observation_timestamp TIMESTAMP NOT NULL,

    -- Observation details
    observer_id VARCHAR(50),
    observer_name VARCHAR(100),
    observation_type VARCHAR(50),
    observation_text TEXT NOT NULL,

    -- Associated data
    related_image_id BIGINT,
    related_measurement_id BIGINT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_timestamp (observation_timestamp)
);

-- ============================================================================
-- Acceptance Criteria and Results
-- ============================================================================

CREATE TABLE IF NOT EXISTS acceptance_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL UNIQUE,

    -- Dust ingress evaluation
    dust_ingress_pass BOOLEAN,
    ingress_severity_level INT,
    ingress_details TEXT,

    -- Electrical performance
    electrical_performance_pass BOOLEAN,
    power_degradation_percent DECIMAL(6,3),
    isc_change_percent DECIMAL(6,3),
    voc_change_percent DECIMAL(6,3),
    ff_change_percent DECIMAL(6,3),
    insulation_resistance_pass BOOLEAN,

    -- Physical integrity
    physical_integrity_pass BOOLEAN,
    cracks_detected BOOLEAN,
    delamination_detected BOOLEAN,
    corrosion_detected BOOLEAN,
    seal_integrity_pass BOOLEAN,

    -- Surface degradation
    surface_degradation_pass BOOLEAN,
    roughness_increase_um DECIMAL(8,3),
    transmittance_loss_percent DECIMAL(6,3),

    -- Overall result
    overall_pass BOOLEAN,

    -- Evaluation
    evaluated_by VARCHAR(50),
    evaluated_at TIMESTAMP,
    evaluation_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_overall (overall_pass)
);

-- ============================================================================
-- Audit Trail
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Action details
    action_type VARCHAR(50) NOT NULL,
    action_description TEXT,
    table_name VARCHAR(50),
    record_id VARCHAR(50),

    -- User information
    user_id VARCHAR(50),
    user_name VARCHAR(100),
    user_role VARCHAR(50),

    -- Changes
    old_value TEXT,
    new_value TEXT,

    -- System information
    ip_address VARCHAR(45),
    user_agent TEXT,

    INDEX idx_session (session_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user (user_id),
    INDEX idx_action (action_type)
);

-- ============================================================================
-- Views for Reporting and Analysis
-- ============================================================================

-- View for complete test summary
CREATE OR REPLACE VIEW v_test_summary AS
SELECT
    ts.session_id,
    ts.protocol_id,
    ts.standard_reference,
    ts.started_at,
    ts.completed_at,
    TIMESTAMPDIFF(HOUR, ts.started_at, ts.completed_at) as duration_hours,
    ts.current_phase,
    ts.test_status,
    ts.test_result,
    ts.operator_name,
    ts.facility_id,
    COUNT(DISTINCT tsp.specimen_id) as specimen_count,
    ar.overall_pass,
    ar.dust_ingress_pass,
    ar.electrical_performance_pass,
    ar.physical_integrity_pass,
    ar.surface_degradation_pass,
    COUNT(DISTINCT td.id) as deviation_count,
    COUNT(DISTINCT td.id) FILTER (WHERE td.severity = 'critical') as critical_deviations
FROM test_sessions ts
LEFT JOIN test_specimens tsp ON ts.session_id = tsp.session_id
LEFT JOIN acceptance_results ar ON ts.session_id = ar.session_id
LEFT JOIN test_deviations td ON ts.session_id = td.session_id
GROUP BY ts.session_id;

-- View for real-time monitoring dashboard
CREATE OR REPLACE VIEW v_realtime_monitoring AS
SELECT
    ed.session_id,
    ed.timestamp,
    ed.temperature_c,
    ed.humidity_percent,
    ed.air_velocity_m_s,
    ed.dust_concentration_kg_m3,
    ed.in_tolerance,
    tc.target_temperature_c,
    tc.target_humidity_percent,
    tc.target_air_velocity_m_s,
    tc.dust_concentration_kg_m3 as target_dust_concentration,
    ABS(ed.temperature_c - tc.target_temperature_c) as temp_deviation,
    ABS(ed.humidity_percent - tc.target_humidity_percent) as humidity_deviation,
    ts.current_phase,
    ts.test_status
FROM environmental_data ed
INNER JOIN test_configurations tc ON ed.session_id = tc.session_id
INNER JOIN test_sessions ts ON ed.session_id = ts.session_id
WHERE ed.timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR);

-- View for particle tracking analysis
CREATE OR REPLACE VIEW v_particle_analysis AS
SELECT
    pm.session_id,
    pm.point_id,
    mp.point_name,
    mp.x_coordinate_mm,
    mp.y_coordinate_mm,
    mp.z_coordinate_mm,
    COUNT(*) as measurement_count,
    AVG(pm.concentration_kg_m3) as avg_concentration,
    STDDEV(pm.concentration_kg_m3) as concentration_stddev,
    AVG(pm.velocity_magnitude_m_s) as avg_velocity,
    AVG(pm.particle_size_microns) as avg_particle_size,
    MIN(pm.timestamp) as first_measurement,
    MAX(pm.timestamp) as last_measurement
FROM particle_measurements pm
INNER JOIN measurement_points mp ON pm.point_id = mp.point_id
GROUP BY pm.session_id, pm.point_id;

-- ============================================================================
-- Indexes for Performance Optimization
-- ============================================================================

-- Add additional composite indexes for common queries
CREATE INDEX idx_env_data_session_time ON environmental_data(session_id, timestamp DESC);
CREATE INDEX idx_particle_session_point_time ON particle_measurements(session_id, point_id, timestamp DESC);
CREATE INDEX idx_images_session_category ON test_images(session_id, image_category);

-- ============================================================================
-- Stored Procedures for Common Operations
-- ============================================================================

DELIMITER //

-- Procedure to initialize a new test session
CREATE PROCEDURE sp_initialize_test_session(
    IN p_session_id VARCHAR(50),
    IN p_operator_id VARCHAR(50),
    IN p_operator_name VARCHAR(100),
    IN p_facility_id VARCHAR(50),
    IN p_config_json TEXT
)
BEGIN
    INSERT INTO test_sessions (
        session_id, operator_id, operator_name, facility_id,
        current_phase, test_status, test_result, configuration_json
    ) VALUES (
        p_session_id, p_operator_id, p_operator_name, p_facility_id,
        'initialization', 'initialized', 'pending', p_config_json
    );

    -- Log the action
    INSERT INTO audit_log (session_id, action_type, action_description, user_id, user_name)
    VALUES (p_session_id, 'session_created', 'New test session initialized', p_operator_id, p_operator_name);
END //

-- Procedure to record environmental data with tolerance checking
CREATE PROCEDURE sp_record_environmental_data(
    IN p_session_id VARCHAR(50),
    IN p_temperature DECIMAL(6,2),
    IN p_humidity DECIMAL(5,2),
    IN p_air_velocity DECIMAL(6,3),
    IN p_pressure DECIMAL(7,3),
    IN p_concentration DECIMAL(10,6)
)
BEGIN
    DECLARE v_in_tolerance BOOLEAN DEFAULT TRUE;
    DECLARE v_target_temp DECIMAL(6,2);
    DECLARE v_target_humid DECIMAL(5,2);
    DECLARE v_target_velocity DECIMAL(6,3);
    DECLARE v_temp_tol DECIMAL(4,2);
    DECLARE v_humid_tol DECIMAL(4,2);
    DECLARE v_velocity_tol DECIMAL(5,3);

    -- Get target values and tolerances
    SELECT target_temperature_c, target_humidity_percent, target_air_velocity_m_s,
           temperature_tolerance_c, humidity_tolerance_percent, air_velocity_tolerance_m_s
    INTO v_target_temp, v_target_humid, v_target_velocity,
         v_temp_tol, v_humid_tol, v_velocity_tol
    FROM test_configurations
    WHERE session_id = p_session_id;

    -- Check tolerances
    IF ABS(p_temperature - v_target_temp) > v_temp_tol OR
       ABS(p_humidity - v_target_humid) > v_humid_tol OR
       ABS(p_air_velocity - v_target_velocity) > v_velocity_tol THEN
        SET v_in_tolerance = FALSE;
    END IF;

    -- Insert data
    INSERT INTO environmental_data (
        session_id, timestamp, temperature_c, humidity_percent,
        air_velocity_m_s, atmospheric_pressure_kpa, dust_concentration_kg_m3,
        in_tolerance, temperature_in_range, humidity_in_range, velocity_in_range,
        data_quality
    ) VALUES (
        p_session_id, NOW(), p_temperature, p_humidity,
        p_air_velocity, p_pressure, p_concentration,
        v_in_tolerance,
        ABS(p_temperature - v_target_temp) <= v_temp_tol,
        ABS(p_humidity - v_target_humid) <= v_humid_tol,
        ABS(p_air_velocity - v_target_velocity) <= v_velocity_tol,
        'good'
    );

    -- If out of tolerance, create deviation record
    IF NOT v_in_tolerance THEN
        INSERT INTO test_deviations (
            session_id, deviation_timestamp, deviation_type, severity,
            description, test_validity_affected
        ) VALUES (
            p_session_id, NOW(), 'environmental_out_of_tolerance', 'major',
            'Environmental conditions exceeded tolerance limits', FALSE
        );
    END IF;
END //

DELIMITER ;

-- ============================================================================
-- Comments and Documentation
-- ============================================================================

-- Add table comments
ALTER TABLE test_sessions COMMENT = 'Main test session records with full traceability';
ALTER TABLE specimens COMMENT = 'Specimen master data with manufacturing information';
ALTER TABLE particle_measurements COMMENT = 'High-frequency particle tracking data for real-time monitoring';
ALTER TABLE environmental_data COMMENT = 'Time-series environmental conditions during test';
ALTER TABLE acceptance_results COMMENT = 'Final test results and acceptance criteria evaluation';

-- ============================================================================
-- End of Schema
-- ============================================================================
