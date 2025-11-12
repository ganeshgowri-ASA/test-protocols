-- ============================================
-- PV Testing Protocol System - Database Schema
-- ============================================
-- Complete schema for managing PV testing workflow, protocols, and traceability
-- Supports PostgreSQL and SQLite

-- ============================================
-- CORE SYSTEM TABLES
-- ============================================

-- Users and Authentication
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) CHECK(role IN ('admin', 'engineer', 'technician', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- WORKFLOW TABLES
-- ============================================

-- Service Requests
CREATE TABLE IF NOT EXISTS service_requests (
    request_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(100),
    customer_phone VARCHAR(20),
    project_name VARCHAR(200),
    sample_description TEXT,
    requested_protocols TEXT, -- JSON array of protocol IDs
    priority VARCHAR(20) CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(20) CHECK(status IN ('pending', 'approved', 'in_progress', 'completed', 'cancelled')) DEFAULT 'pending',
    requested_by INTEGER REFERENCES users(user_id),
    requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INTEGER REFERENCES users(user_id),
    approved_date TIMESTAMP,
    due_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Incoming Inspections
CREATE TABLE IF NOT EXISTS incoming_inspections (
    inspection_id VARCHAR(50) PRIMARY KEY,
    request_id VARCHAR(50) REFERENCES service_requests(request_id),
    sample_id VARCHAR(50) UNIQUE NOT NULL,
    sample_type VARCHAR(50),
    manufacturer VARCHAR(100),
    model_number VARCHAR(100),
    serial_number VARCHAR(100),
    quantity INTEGER,
    condition VARCHAR(20) CHECK(condition IN ('excellent', 'good', 'fair', 'poor', 'damaged')),
    visual_inspection_notes TEXT,
    dimensions TEXT, -- JSON object
    weight_kg DECIMAL(10, 3),
    photos TEXT, -- JSON array of file paths
    inspected_by INTEGER REFERENCES users(user_id),
    inspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK(status IN ('pending', 'approved', 'rejected', 'on_hold')) DEFAULT 'pending',
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Equipment Planning
CREATE TABLE IF NOT EXISTS equipment_planning (
    planning_id VARCHAR(50) PRIMARY KEY,
    inspection_id VARCHAR(50) REFERENCES incoming_inspections(inspection_id),
    equipment_id VARCHAR(50),
    equipment_name VARCHAR(200),
    equipment_type VARCHAR(50),
    location VARCHAR(100),
    availability_status VARCHAR(20) CHECK(availability_status IN ('available', 'in_use', 'maintenance', 'unavailable')),
    scheduled_start_date TIMESTAMP,
    scheduled_end_date TIMESTAMP,
    actual_start_date TIMESTAMP,
    actual_end_date TIMESTAMP,
    operator_id INTEGER REFERENCES users(user_id),
    calibration_due_date DATE,
    calibration_status VARCHAR(20) CHECK(calibration_status IN ('valid', 'due_soon', 'overdue')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PROTOCOL EXECUTION TABLES
-- ============================================

-- Protocol Executions
CREATE TABLE IF NOT EXISTS protocol_executions (
    execution_id VARCHAR(50) PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL, -- e.g., PVTP-001
    protocol_name VARCHAR(200) NOT NULL,
    protocol_version VARCHAR(20),
    request_id VARCHAR(50) REFERENCES service_requests(request_id),
    inspection_id VARCHAR(50) REFERENCES incoming_inspections(inspection_id),
    equipment_id VARCHAR(50),
    sample_id VARCHAR(50),
    status VARCHAR(20) CHECK(status IN ('not_started', 'in_progress', 'paused', 'completed', 'failed', 'cancelled')) DEFAULT 'not_started',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    duration_hours DECIMAL(10, 2),
    operator_id INTEGER REFERENCES users(user_id),
    reviewer_id INTEGER REFERENCES users(user_id),
    test_result VARCHAR(20) CHECK(test_result IN ('pass', 'fail', 'conditional', 'na')),
    overall_grade VARCHAR(10),
    general_data TEXT, -- JSON object
    protocol_inputs TEXT, -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Measurements (Live Readings)
CREATE TABLE IF NOT EXISTS measurements (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id VARCHAR(50) REFERENCES protocol_executions(execution_id),
    measurement_type VARCHAR(50), -- e.g., 'iv_curve', 'temperature', 'irradiance'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sequence_number INTEGER,
    data TEXT NOT NULL, -- JSON object with measurement data
    unit VARCHAR(20),
    equipment_used VARCHAR(100),
    conditions TEXT, -- JSON object with environmental conditions
    operator_id INTEGER REFERENCES users(user_id),
    qc_status VARCHAR(20) CHECK(qc_status IN ('pending', 'approved', 'rejected')),
    qc_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis Results
CREATE TABLE IF NOT EXISTS analysis_results (
    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id VARCHAR(50) REFERENCES protocol_executions(execution_id),
    analysis_type VARCHAR(50),
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results TEXT NOT NULL, -- JSON object with analysis results
    charts TEXT, -- JSON array of chart configurations
    pass_fail_criteria TEXT, -- JSON object
    result_status VARCHAR(20) CHECK(result_status IN ('pass', 'fail', 'conditional')),
    calculated_by INTEGER REFERENCES users(user_id),
    reviewed_by INTEGER REFERENCES users(user_id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- REPORTING TABLES
-- ============================================

-- Reports
CREATE TABLE IF NOT EXISTS reports (
    report_id VARCHAR(50) PRIMARY KEY,
    execution_id VARCHAR(50) REFERENCES protocol_executions(execution_id),
    report_type VARCHAR(50), -- e.g., 'test_report', 'summary', 'certificate'
    report_title VARCHAR(200),
    report_format VARCHAR(20) CHECK(report_format IN ('pdf', 'excel', 'word', 'html')),
    file_path VARCHAR(500),
    generated_by INTEGER REFERENCES users(user_id),
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INTEGER REFERENCES users(user_id),
    approved_date TIMESTAMP,
    status VARCHAR(20) CHECK(status IN ('draft', 'pending_review', 'approved', 'rejected')) DEFAULT 'draft',
    version VARCHAR(20),
    template_used VARCHAR(100),
    metadata TEXT, -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- QUALITY CONTROL TABLES
-- ============================================

-- QC Records
CREATE TABLE IF NOT EXISTS qc_records (
    qc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id VARCHAR(50) REFERENCES protocol_executions(execution_id),
    checkpoint_id VARCHAR(50),
    checkpoint_name VARCHAR(200),
    checkpoint_type VARCHAR(50), -- e.g., 'before_test', 'during_test', 'after_test'
    status VARCHAR(20) CHECK(status IN ('pass', 'fail', 'na')),
    checked_by INTEGER REFERENCES users(user_id),
    checked_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    findings TEXT,
    corrective_actions TEXT,
    verification_status VARCHAR(20),
    verified_by INTEGER REFERENCES users(user_id),
    verified_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MAINTENANCE & PROJECT MANAGEMENT TABLES
-- ============================================

-- Maintenance Logs
CREATE TABLE IF NOT EXISTS maintenance_logs (
    maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id VARCHAR(50),
    equipment_name VARCHAR(200),
    maintenance_type VARCHAR(50) CHECK(maintenance_type IN ('preventive', 'corrective', 'calibration', 'inspection')),
    scheduled_date DATE,
    completed_date TIMESTAMP,
    performed_by INTEGER REFERENCES users(user_id),
    duration_hours DECIMAL(10, 2),
    description TEXT,
    parts_replaced TEXT, -- JSON array
    cost DECIMAL(10, 2),
    status VARCHAR(20) CHECK(status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    next_maintenance_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Non-Conformance Register
CREATE TABLE IF NOT EXISTS nc_register (
    nc_id VARCHAR(50) PRIMARY KEY,
    execution_id VARCHAR(50) REFERENCES protocol_executions(execution_id),
    nc_type VARCHAR(50) CHECK(nc_type IN ('product', 'process', 'documentation', 'equipment')),
    severity VARCHAR(20) CHECK(severity IN ('minor', 'major', 'critical')),
    description TEXT NOT NULL,
    detected_by INTEGER REFERENCES users(user_id),
    detected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    root_cause TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    assigned_to INTEGER REFERENCES users(user_id),
    due_date DATE,
    status VARCHAR(20) CHECK(status IN ('open', 'in_progress', 'resolved', 'closed', 'cancelled')) DEFAULT 'open',
    resolution_date TIMESTAMP,
    verified_by INTEGER REFERENCES users(user_id),
    verification_date TIMESTAMP,
    effectiveness_check TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project Management Tasks
CREATE TABLE IF NOT EXISTS pm_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    execution_id VARCHAR(50) REFERENCES protocol_executions(execution_id),
    task_name VARCHAR(200) NOT NULL,
    task_type VARCHAR(50),
    description TEXT,
    priority VARCHAR(20) CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(20) CHECK(status IN ('not_started', 'in_progress', 'completed', 'on_hold', 'cancelled')) DEFAULT 'not_started',
    assigned_to INTEGER REFERENCES users(user_id),
    created_by INTEGER REFERENCES users(user_id),
    start_date DATE,
    due_date DATE,
    completion_date TIMESTAMP,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    dependencies TEXT, -- JSON array of task_ids
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TRACEABILITY & AUDIT TABLES
-- ============================================

-- Audit Trail
CREATE TABLE IF NOT EXISTS audit_trail (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    record_id VARCHAR(50) NOT NULL,
    action VARCHAR(20) CHECK(action IN ('create', 'update', 'delete', 'view')) NOT NULL,
    user_id INTEGER REFERENCES users(user_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_values TEXT, -- JSON object
    new_values TEXT, -- JSON object
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(100)
);

-- Document Versions
CREATE TABLE IF NOT EXISTS document_versions (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_type VARCHAR(50), -- e.g., 'protocol', 'report', 'template'
    document_id VARCHAR(50),
    version_number VARCHAR(20),
    file_path VARCHAR(500),
    created_by INTEGER REFERENCES users(user_id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_summary TEXT,
    status VARCHAR(20) CHECK(status IN ('draft', 'active', 'superseded', 'archived')),
    approved_by INTEGER REFERENCES users(user_id),
    approved_date TIMESTAMP
);

-- ============================================
-- CONFIGURATION TABLES
-- ============================================

-- System Configuration
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT,
    config_type VARCHAR(20), -- e.g., 'string', 'number', 'boolean', 'json'
    description TEXT,
    is_editable BOOLEAN DEFAULT TRUE,
    updated_by INTEGER REFERENCES users(user_id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notification Settings
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id),
    notification_type VARCHAR(50),
    title VARCHAR(200),
    message TEXT,
    priority VARCHAR(20) CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    action_url VARCHAR(500),
    related_entity_type VARCHAR(50),
    related_entity_id VARCHAR(50)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_service_requests_status ON service_requests(status);
CREATE INDEX IF NOT EXISTS idx_service_requests_date ON service_requests(requested_date);
CREATE INDEX IF NOT EXISTS idx_inspections_request ON incoming_inspections(request_id);
CREATE INDEX IF NOT EXISTS idx_inspections_sample ON incoming_inspections(sample_id);
CREATE INDEX IF NOT EXISTS idx_equipment_inspection ON equipment_planning(inspection_id);
CREATE INDEX IF NOT EXISTS idx_executions_protocol ON protocol_executions(protocol_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON protocol_executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_request ON protocol_executions(request_id);
CREATE INDEX IF NOT EXISTS idx_measurements_execution ON measurements(execution_id);
CREATE INDEX IF NOT EXISTS idx_analysis_execution ON analysis_results(execution_id);
CREATE INDEX IF NOT EXISTS idx_reports_execution ON reports(execution_id);
CREATE INDEX IF NOT EXISTS idx_qc_execution ON qc_records(execution_id);
CREATE INDEX IF NOT EXISTS idx_nc_execution ON nc_register(execution_id);
CREATE INDEX IF NOT EXISTS idx_nc_status ON nc_register(status);
CREATE INDEX IF NOT EXISTS idx_audit_table_record ON audit_trail(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_trail(timestamp);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);

-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert default admin user
INSERT OR IGNORE INTO users (user_id, username, email, full_name, role)
VALUES (1, 'admin', 'admin@pvtest.com', 'System Administrator', 'admin');

-- Insert default system configuration
INSERT OR IGNORE INTO system_config (config_key, config_value, config_type, description) VALUES
('app_name', 'PV Testing Protocol System', 'string', 'Application name'),
('app_version', '1.0.0', 'string', 'Application version'),
('default_language', 'en', 'string', 'Default language'),
('date_format', 'YYYY-MM-DD', 'string', 'Date format'),
('timezone', 'UTC', 'string', 'Default timezone'),
('auto_save_interval', '60', 'number', 'Auto-save interval in seconds'),
('max_upload_size_mb', '100', 'number', 'Maximum file upload size in MB'),
('enable_notifications', 'true', 'boolean', 'Enable system notifications'),
('data_retention_days', '365', 'number', 'Data retention period in days');
