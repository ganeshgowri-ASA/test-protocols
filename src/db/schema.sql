-- Fire Resistance Testing Protocol - Database Schema
-- LIMS-QMS Integration for FIRE-001
-- IEC 61730-2 MST 23

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    protocol_id VARCHAR(50) PRIMARY KEY,
    protocol_name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    category VARCHAR(100),
    standard_name VARCHAR(100),
    standard_section VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    protocol_json JSON,
    INDEX idx_protocol_status (status),
    INDEX idx_protocol_category (category)
);

-- Samples table
CREATE TABLE IF NOT EXISTS samples (
    sample_id VARCHAR(100) PRIMARY KEY,
    manufacturer VARCHAR(255) NOT NULL,
    model_number VARCHAR(255) NOT NULL,
    serial_number VARCHAR(255) NOT NULL UNIQUE,
    date_of_manufacture DATE,
    batch_number VARCHAR(100),
    receipt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visual_condition TEXT,
    dimensions JSON,
    weight_kg DECIMAL(10, 3),
    status VARCHAR(50) DEFAULT 'Received',
    project_id VARCHAR(100),
    customer_id VARCHAR(100),
    test_due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sample_status (status),
    INDEX idx_sample_manufacturer (manufacturer),
    INDEX idx_sample_receipt_date (receipt_date),
    INDEX idx_sample_project (project_id)
);

-- Equipment table
CREATE TABLE IF NOT EXISTS equipment (
    equipment_id VARCHAR(50) PRIMARY KEY,
    equipment_name VARCHAR(255) NOT NULL,
    equipment_type VARCHAR(100),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    calibration_required BOOLEAN DEFAULT FALSE,
    calibration_interval_days INT,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_equipment_status (status),
    INDEX idx_equipment_type (equipment_type)
);

-- Equipment calibration records
CREATE TABLE IF NOT EXISTS equipment_calibrations (
    calibration_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL,
    calibration_date DATE NOT NULL,
    calibration_due_date DATE NOT NULL,
    calibration_certificate VARCHAR(255),
    calibrated_by VARCHAR(255),
    calibration_results JSON,
    is_valid BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    INDEX idx_cal_equipment (equipment_id),
    INDEX idx_cal_due_date (calibration_due_date),
    INDEX idx_cal_validity (is_valid)
);

-- Personnel table
CREATE TABLE IF NOT EXISTS personnel (
    personnel_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    role VARCHAR(100),
    department VARCHAR(100),
    certifications JSON,
    training_records JSON,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_personnel_role (role),
    INDEX idx_personnel_active (active)
);

-- ============================================================================
-- TEST EXECUTION TABLES
-- ============================================================================

-- Test sessions
CREATE TABLE IF NOT EXISTS test_sessions (
    test_id VARCHAR(100) PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    test_date TIMESTAMP NOT NULL,
    test_status VARCHAR(50) DEFAULT 'Pending',
    overall_result VARCHAR(50),
    test_duration_minutes DECIMAL(10, 2),
    environmental_conditions JSON,
    test_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id),
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id),
    INDEX idx_test_protocol (protocol_id),
    INDEX idx_test_sample (sample_id),
    INDEX idx_test_date (test_date),
    INDEX idx_test_status (test_status),
    INDEX idx_test_result (overall_result)
);

-- Test personnel (many-to-many relationship)
CREATE TABLE IF NOT EXISTS test_personnel (
    test_id VARCHAR(100) NOT NULL,
    personnel_id VARCHAR(50) NOT NULL,
    role_in_test VARCHAR(100),
    PRIMARY KEY (test_id, personnel_id),
    FOREIGN KEY (test_id) REFERENCES test_sessions(test_id) ON DELETE CASCADE,
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id),
    INDEX idx_tp_test (test_id),
    INDEX idx_tp_personnel (personnel_id)
);

-- Test equipment usage
CREATE TABLE IF NOT EXISTS test_equipment_usage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    test_id VARCHAR(100) NOT NULL,
    equipment_id VARCHAR(50) NOT NULL,
    calibration_id INT,
    usage_notes TEXT,
    FOREIGN KEY (test_id) REFERENCES test_sessions(test_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (calibration_id) REFERENCES equipment_calibrations(calibration_id),
    INDEX idx_usage_test (test_id),
    INDEX idx_usage_equipment (equipment_id)
);

-- Real-time measurements
CREATE TABLE IF NOT EXISTS measurements (
    measurement_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    test_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP(3) NOT NULL,
    elapsed_time_seconds DECIMAL(10, 3) NOT NULL,
    surface_temperature_c DECIMAL(6, 2),
    flame_spread_mm DECIMAL(8, 2),
    observations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES test_sessions(test_id) ON DELETE CASCADE,
    INDEX idx_meas_test (test_id),
    INDEX idx_meas_time (elapsed_time_seconds)
);

-- Test observations
CREATE TABLE IF NOT EXISTS test_observations (
    observation_id INT AUTO_INCREMENT PRIMARY KEY,
    test_id VARCHAR(100) NOT NULL UNIQUE,
    ignition_occurred BOOLEAN DEFAULT FALSE,
    time_to_ignition_seconds DECIMAL(10, 2),
    self_extinguishing BOOLEAN DEFAULT FALSE,
    self_extinguishing_time_seconds DECIMAL(10, 2),
    dripping_materials BOOLEAN DEFAULT FALSE,
    flaming_drips BOOLEAN DEFAULT FALSE,
    smoke_generation VARCHAR(50),
    material_integrity VARCHAR(50),
    max_flame_spread_mm DECIMAL(8, 2) DEFAULT 0,
    burning_duration_seconds DECIMAL(10, 2) DEFAULT 0,
    continued_smoldering BOOLEAN DEFAULT FALSE,
    notes TEXT,
    FOREIGN KEY (test_id) REFERENCES test_sessions(test_id) ON DELETE CASCADE,
    INDEX idx_obs_test (test_id)
);

-- Acceptance criteria results
CREATE TABLE IF NOT EXISTS acceptance_criteria_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    test_id VARCHAR(100) NOT NULL,
    criterion_name VARCHAR(255) NOT NULL,
    requirement TEXT,
    measured_value VARCHAR(255),
    pass_condition VARCHAR(255),
    result VARCHAR(50),
    severity VARCHAR(50),
    notes TEXT,
    FOREIGN KEY (test_id) REFERENCES test_sessions(test_id) ON DELETE CASCADE,
    INDEX idx_acr_test (test_id),
    INDEX idx_acr_result (result)
);

-- ============================================================================
-- DOCUMENTATION AND REPORTING
-- ============================================================================

-- Test reports
CREATE TABLE IF NOT EXISTS test_reports (
    report_id VARCHAR(100) PRIMARY KEY,
    test_id VARCHAR(100) NOT NULL,
    protocol_id VARCHAR(50) NOT NULL,
    protocol_version VARCHAR(20),
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executive_summary TEXT,
    analysis TEXT,
    conclusion TEXT,
    recommendations JSON,
    prepared_by VARCHAR(100),
    reviewed_by VARCHAR(100),
    approved_by VARCHAR(100),
    report_status VARCHAR(50) DEFAULT 'Draft',
    report_file_path VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES test_sessions(test_id),
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id),
    INDEX idx_report_test (test_id),
    INDEX idx_report_status (report_status),
    INDEX idx_report_date (report_date)
);

-- Report signatures
CREATE TABLE IF NOT EXISTS report_signatures (
    signature_id INT AUTO_INCREMENT PRIMARY KEY,
    report_id VARCHAR(100) NOT NULL,
    personnel_id VARCHAR(50) NOT NULL,
    signature_role VARCHAR(100),
    signature_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signature_data TEXT,
    FOREIGN KEY (report_id) REFERENCES test_reports(report_id) ON DELETE CASCADE,
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id),
    INDEX idx_sig_report (report_id)
);

-- File attachments (photos, documents)
CREATE TABLE IF NOT EXISTS attachments (
    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,  -- 'sample', 'test', 'report', etc.
    entity_id VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_type VARCHAR(100),
    file_size_bytes BIGINT,
    description TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),
    INDEX idx_attach_entity (entity_type, entity_id),
    INDEX idx_attach_type (file_type)
);

-- ============================================================================
-- QMS INTEGRATION TABLES
-- ============================================================================

-- Nonconformance reports
CREATE TABLE IF NOT EXISTS nonconformance_reports (
    ncr_id VARCHAR(100) PRIMARY KEY,
    test_id VARCHAR(100),
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reported_by VARCHAR(100),
    ncr_type VARCHAR(100),
    description TEXT NOT NULL,
    root_cause TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    status VARCHAR(50) DEFAULT 'Open',
    closed_date TIMESTAMP NULL,
    closed_by VARCHAR(100),
    FOREIGN KEY (test_id) REFERENCES test_sessions(test_id),
    INDEX idx_ncr_test (test_id),
    INDEX idx_ncr_status (status),
    INDEX idx_ncr_date (report_date)
);

-- Change control records
CREATE TABLE IF NOT EXISTS change_control (
    change_id VARCHAR(100) PRIMARY KEY,
    change_type VARCHAR(100),
    affected_document VARCHAR(255),
    change_description TEXT NOT NULL,
    change_reason TEXT,
    requested_by VARCHAR(100),
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by VARCHAR(100),
    review_date TIMESTAMP NULL,
    approved_by VARCHAR(100),
    approval_date TIMESTAMP NULL,
    implementation_date TIMESTAMP NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    INDEX idx_change_document (affected_document),
    INDEX idx_change_status (status),
    INDEX idx_change_date (request_date)
);

-- Training records
CREATE TABLE IF NOT EXISTS training_records (
    training_id INT AUTO_INCREMENT PRIMARY KEY,
    personnel_id VARCHAR(50) NOT NULL,
    protocol_id VARCHAR(50),
    training_type VARCHAR(100),
    training_date DATE NOT NULL,
    trainer VARCHAR(100),
    competency_assessed BOOLEAN DEFAULT FALSE,
    assessment_result VARCHAR(50),
    expiration_date DATE,
    notes TEXT,
    FOREIGN KEY (personnel_id) REFERENCES personnel(personnel_id),
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id),
    INDEX idx_train_personnel (personnel_id),
    INDEX idx_train_protocol (protocol_id),
    INDEX idx_train_expiry (expiration_date)
);

-- ============================================================================
-- AUDIT AND COMPLIANCE
-- ============================================================================

-- Audit trail
CREATE TABLE IF NOT EXISTS audit_trail (
    audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSON,
    new_values JSON,
    changed_by VARCHAR(100),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT,
    INDEX idx_audit_table (table_name),
    INDEX idx_audit_record (record_id),
    INDEX idx_audit_timestamp (change_timestamp),
    INDEX idx_audit_user (changed_by)
);

-- System notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    notification_type VARCHAR(100),
    priority VARCHAR(50),
    subject VARCHAR(255),
    message TEXT,
    recipient_id VARCHAR(100),
    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_date TIMESTAMP NULL,
    related_entity_type VARCHAR(50),
    related_entity_id VARCHAR(100),
    INDEX idx_notif_recipient (recipient_id),
    INDEX idx_notif_read (read_date),
    INDEX idx_notif_type (notification_type)
);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Active calibrations
CREATE OR REPLACE VIEW v_active_calibrations AS
SELECT
    e.equipment_id,
    e.equipment_name,
    e.equipment_type,
    ec.calibration_date,
    ec.calibration_due_date,
    ec.calibrated_by,
    DATEDIFF(ec.calibration_due_date, CURDATE()) AS days_until_due,
    CASE
        WHEN CURDATE() > ec.calibration_due_date THEN 'Overdue'
        WHEN DATEDIFF(ec.calibration_due_date, CURDATE()) <= 30 THEN 'Due Soon'
        ELSE 'Current'
    END AS calibration_status
FROM equipment e
LEFT JOIN equipment_calibrations ec ON e.equipment_id = ec.equipment_id
    AND ec.calibration_id = (
        SELECT MAX(calibration_id)
        FROM equipment_calibrations
        WHERE equipment_id = e.equipment_id
    )
WHERE e.status = 'active';

-- View: Test summary
CREATE OR REPLACE VIEW v_test_summary AS
SELECT
    ts.test_id,
    ts.test_date,
    ts.test_status,
    ts.overall_result,
    p.protocol_name,
    s.manufacturer,
    s.model_number,
    s.serial_number,
    GROUP_CONCAT(DISTINCT CONCAT(pers.first_name, ' ', pers.last_name) SEPARATOR ', ') AS personnel,
    ts.test_duration_minutes
FROM test_sessions ts
JOIN protocols p ON ts.protocol_id = p.protocol_id
JOIN samples s ON ts.sample_id = s.sample_id
LEFT JOIN test_personnel tp ON ts.test_id = tp.test_id
LEFT JOIN personnel pers ON tp.personnel_id = pers.personnel_id
GROUP BY ts.test_id;

-- View: Sample status tracking
CREATE OR REPLACE VIEW v_sample_tracking AS
SELECT
    s.sample_id,
    s.manufacturer,
    s.model_number,
    s.serial_number,
    s.status,
    s.receipt_date,
    s.test_due_date,
    DATEDIFF(s.test_due_date, CURDATE()) AS days_until_due,
    COUNT(DISTINCT ts.test_id) AS test_count,
    MAX(ts.test_date) AS last_test_date
FROM samples s
LEFT JOIN test_sessions ts ON s.sample_id = ts.sample_id
GROUP BY s.sample_id;

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

DELIMITER $$

-- Procedure: Create new test session
CREATE PROCEDURE sp_create_test_session(
    IN p_test_id VARCHAR(100),
    IN p_protocol_id VARCHAR(50),
    IN p_sample_id VARCHAR(100),
    IN p_test_date TIMESTAMP
)
BEGIN
    -- Insert test session
    INSERT INTO test_sessions (test_id, protocol_id, sample_id, test_date, test_status)
    VALUES (p_test_id, p_protocol_id, p_sample_id, p_test_date, 'Testing in Progress');

    -- Update sample status
    UPDATE samples SET status = 'Testing in Progress' WHERE sample_id = p_sample_id;

    -- Log audit trail
    INSERT INTO audit_trail (table_name, record_id, action, new_values, changed_by)
    VALUES ('test_sessions', p_test_id, 'INSERT', JSON_OBJECT('status', 'Testing in Progress'), CURRENT_USER());
END$$

-- Procedure: Check calibration status
CREATE PROCEDURE sp_check_calibration_alerts()
BEGIN
    SELECT
        equipment_id,
        equipment_name,
        calibration_due_date,
        DATEDIFF(calibration_due_date, CURDATE()) AS days_remaining
    FROM v_active_calibrations
    WHERE calibration_status IN ('Overdue', 'Due Soon')
    ORDER BY days_remaining;
END$$

-- Procedure: Complete test session
CREATE PROCEDURE sp_complete_test_session(
    IN p_test_id VARCHAR(100),
    IN p_overall_result VARCHAR(50),
    IN p_test_duration DECIMAL(10,2)
)
BEGIN
    -- Update test session
    UPDATE test_sessions
    SET test_status = 'Test Complete',
        overall_result = p_overall_result,
        test_duration_minutes = p_test_duration,
        completed_at = CURRENT_TIMESTAMP
    WHERE test_id = p_test_id;

    -- Update sample status
    UPDATE samples
    SET status = 'Test Complete'
    WHERE sample_id = (SELECT sample_id FROM test_sessions WHERE test_id = p_test_id);

    -- Send notification if failed
    IF p_overall_result = 'Fail' THEN
        INSERT INTO notifications (notification_type, priority, subject, message, related_entity_type, related_entity_id)
        VALUES ('Test Failure', 'High',
                CONCAT('Test Failed: ', p_test_id),
                CONCAT('Fire resistance test ', p_test_id, ' has failed. Immediate review required.'),
                'test_session', p_test_id);
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_test_protocol_date ON test_sessions(protocol_id, test_date);
CREATE INDEX idx_sample_manufacturer_model ON samples(manufacturer, model_number);
CREATE INDEX idx_measurements_test_time ON measurements(test_id, elapsed_time_seconds);

-- Full-text search indexes
ALTER TABLE samples ADD FULLTEXT INDEX ft_sample_search (manufacturer, model_number, serial_number);
ALTER TABLE test_sessions ADD FULLTEXT INDEX ft_test_notes (test_notes);

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert FIRE-001 protocol
INSERT INTO protocols (protocol_id, protocol_name, version, category, standard_name, standard_section, status)
VALUES ('FIRE-001', 'Fire Resistance Testing Protocol', '1.0.0', 'Safety', 'IEC 61730-2', 'MST 23', 'active')
ON DUPLICATE KEY UPDATE last_modified = CURRENT_TIMESTAMP;
