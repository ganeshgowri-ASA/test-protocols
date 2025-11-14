-- Database schema for HAIL-001 Hail Impact Test
-- Compatible with PostgreSQL and SQLite (with minor modifications)

-- Main test sessions table
CREATE TABLE IF NOT EXISTS hail_test_sessions (
    session_id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL,
    protocol_version VARCHAR(20) NOT NULL,
    test_date TIMESTAMP NOT NULL,
    test_operator VARCHAR(100),
    facility VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Module information table
CREATE TABLE IF NOT EXISTS test_modules (
    module_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES hail_test_sessions(session_id) ON DELETE CASCADE,
    manufacturer VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    nameplate_power DECIMAL(10, 2),
    length_mm DECIMAL(10, 2),
    width_mm DECIMAL(10, 2),
    thickness_mm DECIMAL(10, 2),
    weight_kg DECIMAL(10, 2),
    cell_technology VARCHAR(50),
    manufacturing_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-test measurements table
CREATE TABLE IF NOT EXISTS pre_test_measurements (
    measurement_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES hail_test_sessions(session_id) ON DELETE CASCADE,
    measurement_timestamp TIMESTAMP NOT NULL,
    pmax_initial DECIMAL(10, 3) NOT NULL,
    voc DECIMAL(10, 3),
    isc DECIMAL(10, 3),
    vmp DECIMAL(10, 3),
    imp DECIMAL(10, 3),
    fill_factor DECIMAL(5, 4),
    insulation_resistance_initial DECIMAL(10, 2) NOT NULL,
    visual_defects_present BOOLEAN DEFAULT FALSE,
    visual_defects_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Impact test data table
CREATE TABLE IF NOT EXISTS impact_test_data (
    impact_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES hail_test_sessions(session_id) ON DELETE CASCADE,
    impact_number INTEGER NOT NULL,
    impact_location_id INTEGER,
    impact_location_x DECIMAL(5, 3),
    impact_location_y DECIMAL(5, 3),
    impact_location_description VARCHAR(100),
    ice_ball_diameter_mm DECIMAL(5, 2) DEFAULT 25.00,
    ice_ball_weight_g DECIMAL(5, 2),
    ice_ball_temperature_c DECIMAL(5, 2),
    ice_ball_retrieval_time TIMESTAMP,
    impact_time TIMESTAMP,
    time_delta_seconds INTEGER,
    target_velocity_kmh DECIMAL(5, 2) DEFAULT 80.00,
    actual_velocity_kmh DECIMAL(5, 2),
    velocity_deviation_kmh DECIMAL(5, 2),
    launcher_pressure_psi DECIMAL(6, 2),
    open_circuit_detected BOOLEAN DEFAULT FALSE,
    visual_damage VARCHAR(200),
    impact_video_path VARCHAR(500),
    impact_photo_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, impact_number)
);

-- Post-test measurements table
CREATE TABLE IF NOT EXISTS post_test_measurements (
    measurement_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES hail_test_sessions(session_id) ON DELETE CASCADE,
    measurement_timestamp TIMESTAMP NOT NULL,
    pmax_final DECIMAL(10, 3) NOT NULL,
    voc DECIMAL(10, 3),
    isc DECIMAL(10, 3),
    vmp DECIMAL(10, 3),
    imp DECIMAL(10, 3),
    fill_factor DECIMAL(5, 4),
    insulation_resistance_final DECIMAL(10, 2) NOT NULL,
    front_glass_cracks BOOLEAN DEFAULT FALSE,
    cell_cracks BOOLEAN DEFAULT FALSE,
    backsheet_cracks BOOLEAN DEFAULT FALSE,
    delamination BOOLEAN DEFAULT FALSE,
    junction_box_damage BOOLEAN DEFAULT FALSE,
    frame_damage BOOLEAN DEFAULT FALSE,
    visual_defects_description TEXT,
    el_image_path VARCHAR(500),
    thermal_image_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test results and analysis table
CREATE TABLE IF NOT EXISTS test_results (
    result_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES hail_test_sessions(session_id) ON DELETE CASCADE,
    pmax_initial DECIMAL(10, 3),
    pmax_final DECIMAL(10, 3),
    power_degradation_percent DECIMAL(5, 2),
    power_degradation_watts DECIMAL(10, 3),
    velocity_mean DECIMAL(5, 2),
    velocity_std DECIMAL(5, 2),
    velocity_min DECIMAL(5, 2),
    velocity_max DECIMAL(5, 2),
    time_compliance_count INTEGER,
    time_compliance_rate DECIMAL(5, 2),
    open_circuit_count INTEGER,
    insulation_initial DECIMAL(10, 2),
    insulation_final DECIMAL(10, 2),
    insulation_degradation_percent DECIMAL(5, 2),
    overall_result VARCHAR(10),
    power_criterion_pass BOOLEAN,
    visual_criterion_pass BOOLEAN,
    insulation_criterion_pass BOOLEAN,
    open_circuit_criterion_pass BOOLEAN,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Environmental conditions table
CREATE TABLE IF NOT EXISTS environmental_conditions (
    condition_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES hail_test_sessions(session_id) ON DELETE CASCADE,
    measurement_time TIMESTAMP NOT NULL,
    ambient_temperature_c DECIMAL(5, 2),
    relative_humidity_percent DECIMAL(5, 2),
    atmospheric_pressure_kpa DECIMAL(6, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Equipment usage log table
CREATE TABLE IF NOT EXISTS equipment_usage_log (
    log_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES hail_test_sessions(session_id) ON DELETE CASCADE,
    equipment_id VARCHAR(50),
    equipment_name VARCHAR(200),
    calibration_date DATE,
    calibration_due_date DATE,
    serial_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test attachments table (photos, videos, documents)
CREATE TABLE IF NOT EXISTS test_attachments (
    attachment_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES hail_test_sessions(session_id) ON DELETE CASCADE,
    attachment_type VARCHAR(50),
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sessions_protocol ON hail_test_sessions(protocol_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON hail_test_sessions(test_date);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON hail_test_sessions(status);
CREATE INDEX IF NOT EXISTS idx_modules_serial ON test_modules(serial_number);
CREATE INDEX IF NOT EXISTS idx_impacts_session ON impact_test_data(session_id);
CREATE INDEX IF NOT EXISTS idx_results_session ON test_results(session_id);
CREATE INDEX IF NOT EXISTS idx_results_overall ON test_results(overall_result);

-- Create view for complete test report
CREATE OR REPLACE VIEW vw_hail_test_report AS
SELECT
    s.session_id,
    s.protocol_id,
    s.protocol_version,
    s.test_date,
    s.test_operator,
    s.facility,
    s.status,
    m.manufacturer,
    m.model,
    m.serial_number,
    m.nameplate_power,
    pre.pmax_initial,
    post.pmax_final,
    r.power_degradation_percent,
    r.power_degradation_watts,
    r.velocity_mean,
    r.velocity_std,
    r.time_compliance_count,
    r.open_circuit_count,
    r.overall_result,
    r.power_criterion_pass,
    r.visual_criterion_pass,
    r.insulation_criterion_pass,
    r.open_circuit_criterion_pass,
    post.front_glass_cracks,
    post.cell_cracks,
    post.backsheet_cracks,
    post.delamination
FROM hail_test_sessions s
LEFT JOIN test_modules m ON s.session_id = m.session_id
LEFT JOIN pre_test_measurements pre ON s.session_id = pre.session_id
LEFT JOIN post_test_measurements post ON s.session_id = post.session_id
LEFT JOIN test_results r ON s.session_id = r.session_id;

-- Create view for impact summary
CREATE OR REPLACE VIEW vw_impact_summary AS
SELECT
    session_id,
    COUNT(*) as total_impacts,
    AVG(actual_velocity_kmh) as avg_velocity,
    STDDEV(actual_velocity_kmh) as std_velocity,
    MIN(actual_velocity_kmh) as min_velocity,
    MAX(actual_velocity_kmh) as max_velocity,
    SUM(CASE WHEN time_delta_seconds <= 60 THEN 1 ELSE 0 END) as time_compliant_count,
    SUM(CASE WHEN open_circuit_detected THEN 1 ELSE 0 END) as open_circuit_count,
    SUM(CASE WHEN ABS(actual_velocity_kmh - target_velocity_kmh) <= 2 THEN 1 ELSE 0 END) as velocity_compliant_count
FROM impact_test_data
GROUP BY session_id;
