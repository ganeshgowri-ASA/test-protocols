-- SOLDER-001: Solder Bond Degradation Testing Database Schema
-- Database tables for storing test data, results, and traceability

-- Main test sessions table
CREATE TABLE IF NOT EXISTS solder_test_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    protocol_id VARCHAR(20) NOT NULL DEFAULT 'SOLDER-001',
    module_id VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    manufacturing_date DATE,
    solder_type VARCHAR(50),
    solder_composition VARCHAR(100),
    cell_type VARCHAR(50),
    test_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    test_end_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'in_progress',
    overall_result VARCHAR(20),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Initial characterization data
CREATE TABLE IF NOT EXISTS solder_initial_characterization (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    module_id VARCHAR(50) NOT NULL,
    pmax_w DECIMAL(10, 2),
    voc_v DECIMAL(10, 2),
    isc_a DECIMAL(10, 2),
    fill_factor DECIMAL(5, 4),
    series_resistance_ohm DECIMAL(10, 4),
    avg_cell_resistance_mohm DECIMAL(10, 2),
    max_cell_resistance_mohm DECIMAL(10, 2),
    hotspot_count INT DEFAULT 0,
    avg_cell_temp_c DECIMAL(10, 2),
    visual_condition VARCHAR(50),
    measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE
);

-- Resistance mapping table
CREATE TABLE IF NOT EXISTS solder_resistance_measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    module_id VARCHAR(50) NOT NULL,
    checkpoint_cycle INT NOT NULL,
    joint_id VARCHAR(50) NOT NULL,
    joint_type VARCHAR(30),
    resistance_mohm DECIMAL(10, 3),
    measurement_1 DECIMAL(10, 3),
    measurement_2 DECIMAL(10, 3),
    measurement_3 DECIMAL(10, 3),
    measurement_avg DECIMAL(10, 3),
    measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_checkpoint (session_id, checkpoint_cycle),
    INDEX idx_joint (session_id, joint_id)
);

-- Thermal cycling checkpoints
CREATE TABLE IF NOT EXISTS solder_thermal_checkpoints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    module_id VARCHAR(50) NOT NULL,
    checkpoint_cycle INT NOT NULL,
    pmax_w DECIMAL(10, 2),
    voc_v DECIMAL(10, 2),
    isc_a DECIMAL(10, 2),
    fill_factor DECIMAL(5, 4),
    series_resistance_ohm DECIMAL(10, 4),
    power_loss_pct DECIMAL(5, 2),
    avg_resistance_mohm DECIMAL(10, 2),
    resistance_increase_pct DECIMAL(5, 2),
    hotspot_count INT,
    new_hotspots INT,
    max_delta_t_c DECIMAL(5, 2),
    visual_defects TEXT,
    checkpoint_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_checkpoint (session_id, checkpoint_cycle)
);

-- Mechanical testing data
CREATE TABLE IF NOT EXISTS solder_mechanical_testing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    module_id VARCHAR(50) NOT NULL,
    test_type VARCHAR(30),
    checkpoint_cycles INT,
    load_pa DECIMAL(10, 2),
    frequency_hz DECIMAL(5, 2),
    pmax_before_w DECIMAL(10, 2),
    pmax_after_w DECIMAL(10, 2),
    power_change_pct DECIMAL(5, 2),
    visual_defects TEXT,
    test_result VARCHAR(20),
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE
);

-- Pull test results
CREATE TABLE IF NOT EXISTS solder_pull_test_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    sample_type VARCHAR(20),
    module_id VARCHAR(50),
    joint_id VARCHAR(50),
    pull_force_n DECIMAL(10, 2),
    failure_mode VARCHAR(50),
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_sample_type (session_id, sample_type)
);

-- Thermal imaging data
CREATE TABLE IF NOT EXISTS solder_thermal_imaging (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    module_id VARCHAR(50) NOT NULL,
    checkpoint_cycle INT NOT NULL,
    avg_temp_c DECIMAL(10, 2),
    max_temp_c DECIMAL(10, 2),
    min_temp_c DECIMAL(10, 2),
    hotspot_count INT,
    max_delta_t_c DECIMAL(5, 2),
    image_path VARCHAR(255),
    image_hash VARCHAR(64),
    measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE
);

-- Visual inspection data
CREATE TABLE IF NOT EXISTS solder_visual_inspection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    module_id VARCHAR(50) NOT NULL,
    checkpoint_cycle INT NOT NULL,
    inspector VARCHAR(50),
    overall_condition VARCHAR(50),
    solder_cracks INT DEFAULT 0,
    ribbon_detachment INT DEFAULT 0,
    delamination_pct DECIMAL(5, 2) DEFAULT 0,
    discoloration_pct DECIMAL(5, 2) DEFAULT 0,
    defects_description TEXT,
    image_paths TEXT,
    inspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE
);

-- Analysis results
CREATE TABLE IF NOT EXISTS solder_analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    analysis_type VARCHAR(50),
    resistance_degradation_rate_per_100cycles DECIMAL(10, 4),
    resistance_r_squared DECIMAL(5, 4),
    power_degradation_rate_per_100cycles DECIMAL(10, 4),
    power_r_squared DECIMAL(5, 4),
    correlation_resistance_power DECIMAL(5, 4),
    predicted_lifetime_years DECIMAL(10, 2),
    cycles_to_failure INT,
    limiting_factor VARCHAR(50),
    confidence_level VARCHAR(50),
    year_25_resistance_increase_pct DECIMAL(5, 2),
    year_25_power_loss_pct DECIMAL(5, 2),
    meets_25yr_target BOOLEAN,
    primary_failure_mode VARCHAR(50),
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    UNIQUE KEY unique_analysis (session_id, analysis_type)
);

-- Validation violations
CREATE TABLE IF NOT EXISTS solder_validation_violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    checkpoint_cycle INT,
    parameter VARCHAR(100),
    severity VARCHAR(20),
    message TEXT,
    measured_value DECIMAL(10, 4),
    expected_value DECIMAL(10, 4),
    unit VARCHAR(20),
    violation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_severity (session_id, severity)
);

-- Test events log
CREATE TABLE IF NOT EXISTS solder_test_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50),
    event_description TEXT,
    checkpoint_cycle INT,
    event_data JSON,
    user_id VARCHAR(50),
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_event_type (session_id, event_type),
    INDEX idx_timestamp (event_timestamp)
);

-- Equipment calibration records
CREATE TABLE IF NOT EXISTS solder_equipment_calibration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL,
    equipment_type VARCHAR(50),
    calibration_date DATE NOT NULL,
    next_calibration_date DATE,
    calibration_certificate VARCHAR(255),
    calibrated_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'valid',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_equipment (equipment_id),
    INDEX idx_calibration_date (calibration_date)
);

-- Reports generated
CREATE TABLE IF NOT EXISTS solder_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    report_type VARCHAR(50),
    report_format VARCHAR(20),
    file_path VARCHAR(255),
    file_hash VARCHAR(64),
    generated_by VARCHAR(50),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_report_type (session_id, report_type)
);

-- Traceability records
CREATE TABLE IF NOT EXISTS solder_traceability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    artifact_type VARCHAR(50),
    artifact_path VARCHAR(255),
    data_hash VARCHAR(64),
    parent_hash VARCHAR(64),
    blockchain_hash VARCHAR(64),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_artifact_type (artifact_type),
    INDEX idx_data_hash (data_hash)
);

-- Statistical summary cache
CREATE TABLE IF NOT EXISTS solder_statistics_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    checkpoint_cycle INT NOT NULL,
    statistic_type VARCHAR(50),
    statistic_name VARCHAR(100),
    value DECIMAL(15, 6),
    unit VARCHAR(20),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES solder_test_sessions(session_id) ON DELETE CASCADE,
    UNIQUE KEY unique_statistic (session_id, checkpoint_cycle, statistic_type, statistic_name)
);

-- Create views for common queries

-- View: Latest checkpoint data per module
CREATE OR REPLACE VIEW solder_latest_checkpoint AS
SELECT
    s.session_id,
    s.module_id,
    s.manufacturer,
    s.status,
    tc.checkpoint_cycle,
    tc.pmax_w,
    tc.power_loss_pct,
    tc.avg_resistance_mohm,
    tc.resistance_increase_pct,
    tc.hotspot_count,
    tc.checkpoint_date
FROM solder_test_sessions s
LEFT JOIN solder_thermal_checkpoints tc ON s.session_id = tc.session_id
WHERE tc.checkpoint_cycle = (
    SELECT MAX(checkpoint_cycle)
    FROM solder_thermal_checkpoints
    WHERE session_id = s.session_id
);

-- View: Test summary with violations
CREATE OR REPLACE VIEW solder_test_summary AS
SELECT
    s.session_id,
    s.module_id,
    s.manufacturer,
    s.model,
    s.status,
    s.overall_result,
    COUNT(DISTINCT tc.checkpoint_cycle) as checkpoints_completed,
    MAX(tc.checkpoint_cycle) as last_checkpoint,
    SUM(CASE WHEN vv.severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical_violations,
    SUM(CASE WHEN vv.severity = 'MAJOR' THEN 1 ELSE 0 END) as major_violations,
    SUM(CASE WHEN vv.severity = 'MINOR' THEN 1 ELSE 0 END) as minor_violations,
    ar.predicted_lifetime_years,
    ar.meets_25yr_target,
    s.test_start_date,
    s.test_end_date
FROM solder_test_sessions s
LEFT JOIN solder_thermal_checkpoints tc ON s.session_id = tc.session_id
LEFT JOIN solder_validation_violations vv ON s.session_id = vv.session_id
LEFT JOIN solder_analysis_results ar ON s.session_id = ar.session_id AND ar.analysis_type = 'lifetime_prediction'
GROUP BY s.session_id;

-- View: Resistance trending
CREATE OR REPLACE VIEW solder_resistance_trending AS
SELECT
    s.session_id,
    s.module_id,
    tc.checkpoint_cycle,
    tc.avg_resistance_mohm,
    tc.resistance_increase_pct,
    ic.avg_cell_resistance_mohm as baseline_resistance,
    tc.checkpoint_date
FROM solder_test_sessions s
JOIN solder_thermal_checkpoints tc ON s.session_id = tc.session_id
LEFT JOIN solder_initial_characterization ic ON s.session_id = ic.session_id
ORDER BY s.session_id, tc.checkpoint_cycle;

-- View: Power degradation trending
CREATE OR REPLACE VIEW solder_power_trending AS
SELECT
    s.session_id,
    s.module_id,
    tc.checkpoint_cycle,
    tc.pmax_w,
    tc.power_loss_pct,
    ic.pmax_w as baseline_power,
    tc.checkpoint_date
FROM solder_test_sessions s
JOIN solder_thermal_checkpoints tc ON s.session_id = tc.session_id
LEFT JOIN solder_initial_characterization ic ON s.session_id = ic.session_id
ORDER BY s.session_id, tc.checkpoint_cycle;

-- Indexes for performance optimization
CREATE INDEX idx_session_status ON solder_test_sessions(status);
CREATE INDEX idx_session_result ON solder_test_sessions(overall_result);
CREATE INDEX idx_session_manufacturer ON solder_test_sessions(manufacturer);
CREATE INDEX idx_checkpoint_cycle ON solder_thermal_checkpoints(checkpoint_cycle);
CREATE INDEX idx_violation_severity ON solder_validation_violations(severity);
CREATE INDEX idx_analysis_type ON solder_analysis_results(analysis_type);

-- Triggers for automatic updates
DELIMITER //

CREATE TRIGGER solder_update_timestamp
BEFORE UPDATE ON solder_test_sessions
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

CREATE TRIGGER solder_calculate_resistance_avg
BEFORE INSERT ON solder_resistance_measurements
FOR EACH ROW
BEGIN
    SET NEW.measurement_avg = (NEW.measurement_1 + NEW.measurement_2 + NEW.measurement_3) / 3;
END//

DELIMITER ;

-- Sample data insertion example (commented out)
/*
INSERT INTO solder_test_sessions (session_id, module_id, manufacturer, model, solder_type, status)
VALUES ('TEST-20250114-SOLDER-001', 'MOD-001', 'Test Manufacturer', 'TEST-400W', 'SAC305', 'in_progress');
*/
