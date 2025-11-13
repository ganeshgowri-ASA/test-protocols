-- PV Testing LIMS-QMS Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- USERS AND AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'manager', 'technician', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- PROTOCOLS
-- ============================================================================

CREATE TABLE protocols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    protocol_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('performance', 'degradation', 'environmental', 'mechanical', 'safety')),
    version VARCHAR(20) NOT NULL,
    standard_reference VARCHAR(255),
    description TEXT,
    test_conditions JSONB,
    input_parameters JSONB,
    measurement_points JSONB,
    calculations JSONB,
    acceptance_criteria JSONB,
    equipment_required JSONB,
    estimated_duration INTEGER,  -- in minutes
    safety_precautions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_protocols_protocol_id ON protocols(protocol_id);
CREATE INDEX idx_protocols_category ON protocols(category);
CREATE INDEX idx_protocols_is_active ON protocols(is_active);

-- ============================================================================
-- SERVICE REQUESTS
-- ============================================================================

CREATE TABLE service_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255),
    customer_phone VARCHAR(50),
    customer_company VARCHAR(255),
    customer_address TEXT,
    request_date DATE NOT NULL DEFAULT CURRENT_DATE,
    required_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'quoted', 'approved', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    total_quote DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    notes TEXT,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_service_requests_request_number ON service_requests(request_number);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_customer_name ON service_requests(customer_name);
CREATE INDEX idx_service_requests_request_date ON service_requests(request_date);

-- ============================================================================
-- SAMPLES
-- ============================================================================

CREATE TABLE samples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id VARCHAR(50) UNIQUE NOT NULL,
    service_request_id UUID REFERENCES service_requests(id),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    technology VARCHAR(100),  -- mono-Si, poly-Si, thin-film, etc.
    rated_power DECIMAL(10, 2),  -- Watts
    dimensions_length DECIMAL(10, 2),  -- mm
    dimensions_width DECIMAL(10, 2),  -- mm
    dimensions_height DECIMAL(10, 2),  -- mm
    weight DECIMAL(10, 3),  -- kg
    manufacturing_date DATE,
    reception_date DATE NOT NULL DEFAULT CURRENT_DATE,
    condition VARCHAR(50) CHECK (condition IN ('excellent', 'good', 'fair', 'damaged')),
    storage_location VARCHAR(100),
    barcode VARCHAR(100),
    qr_code TEXT,
    photos JSONB,  -- Array of photo URLs
    inspection_notes TEXT,
    inspected_by UUID REFERENCES users(id),
    inspected_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_sample_id ON samples(sample_id);
CREATE INDEX idx_samples_service_request_id ON samples(service_request_id);
CREATE INDEX idx_samples_manufacturer ON samples(manufacturer);
CREATE INDEX idx_samples_model ON samples(model);

-- ============================================================================
-- EQUIPMENT
-- ============================================================================

CREATE TABLE equipment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,  -- solar simulator, environmental chamber, etc.
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    location VARCHAR(100),
    status VARCHAR(50) DEFAULT 'available' CHECK (status IN ('available', 'in_use', 'maintenance', 'calibration', 'out_of_service')),
    calibration_due_date DATE,
    last_calibration_date DATE,
    calibration_interval INTEGER,  -- days
    maintenance_schedule VARCHAR(50),
    specifications JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_equipment_id ON equipment(equipment_id);
CREATE INDEX idx_equipment_type ON equipment(type);
CREATE INDEX idx_equipment_status ON equipment(status);

-- ============================================================================
-- EQUIPMENT BOOKINGS
-- ============================================================================

CREATE TABLE equipment_bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id UUID REFERENCES equipment(id),
    test_execution_id UUID,  -- Will reference test_executions
    booked_by UUID REFERENCES users(id),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    purpose TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT booking_time_check CHECK (end_time > start_time)
);

CREATE INDEX idx_equipment_bookings_equipment_id ON equipment_bookings(equipment_id);
CREATE INDEX idx_equipment_bookings_start_time ON equipment_bookings(start_time);
CREATE INDEX idx_equipment_bookings_status ON equipment_bookings(status);

-- ============================================================================
-- TEST EXECUTIONS
-- ============================================================================

CREATE TABLE test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_number VARCHAR(50) UNIQUE NOT NULL,
    service_request_id UUID REFERENCES service_requests(id),
    sample_id UUID REFERENCES samples(id),
    protocol_id UUID REFERENCES protocols(id),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'setup', 'running', 'paused', 'completed', 'failed', 'cancelled')),
    scheduled_start TIMESTAMP WITH TIME ZONE,
    actual_start TIMESTAMP WITH TIME ZONE,
    actual_end TIMESTAMP WITH TIME ZONE,
    test_conditions JSONB,  -- Actual conditions during test
    input_parameters JSONB,  -- Input values for this execution
    progress_percentage INTEGER DEFAULT 0,
    current_step VARCHAR(255),
    technician_id UUID REFERENCES users(id),
    reviewer_id UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_executions_execution_number ON test_executions(execution_number);
CREATE INDEX idx_test_executions_service_request_id ON test_executions(service_request_id);
CREATE INDEX idx_test_executions_sample_id ON test_executions(sample_id);
CREATE INDEX idx_test_executions_protocol_id ON test_executions(protocol_id);
CREATE INDEX idx_test_executions_status ON test_executions(status);

-- ============================================================================
-- RAW DATA FILES
-- ============================================================================

CREATE TABLE raw_data_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_execution_id UUID REFERENCES test_executions(id),
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    checksum VARCHAR(64),  -- SHA-256
    upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id),
    equipment_id UUID REFERENCES equipment(id),
    measurement_timestamp TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

CREATE INDEX idx_raw_data_files_test_execution_id ON raw_data_files(test_execution_id);
CREATE INDEX idx_raw_data_files_equipment_id ON raw_data_files(equipment_id);

-- ============================================================================
-- MEASUREMENT DATA
-- ============================================================================

CREATE TABLE measurement_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_execution_id UUID REFERENCES test_executions(id),
    raw_data_file_id UUID REFERENCES raw_data_files(id),
    measurement_point VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    data JSONB NOT NULL,  -- Flexible storage for any measurement type
    units JSONB,  -- Units for each measurement
    environmental_conditions JSONB,  -- Temperature, humidity, etc. at time of measurement
    is_valid BOOLEAN DEFAULT TRUE,
    validation_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurement_data_test_execution_id ON measurement_data(test_execution_id);
CREATE INDEX idx_measurement_data_timestamp ON measurement_data(timestamp);

-- ============================================================================
-- ANALYSIS RESULTS
-- ============================================================================

CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_execution_id UUID REFERENCES test_executions(id),
    result_type VARCHAR(100),  -- efficiency, fill_factor, temperature_coefficient, etc.
    calculated_value DECIMAL(15, 6),
    unit VARCHAR(50),
    uncertainty DECIMAL(15, 6),
    pass_fail VARCHAR(20) CHECK (pass_fail IN ('pass', 'fail', 'conditional', 'n/a')),
    acceptance_criteria JSONB,
    calculation_method TEXT,
    intermediate_results JSONB,
    analyzed_by UUID REFERENCES users(id),
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analysis_results_test_execution_id ON analysis_results(test_execution_id);
CREATE INDEX idx_analysis_results_result_type ON analysis_results(result_type);
CREATE INDEX idx_analysis_results_pass_fail ON analysis_results(pass_fail);

-- ============================================================================
-- REPORTS
-- ============================================================================

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_number VARCHAR(50) UNIQUE NOT NULL,
    test_execution_id UUID REFERENCES test_executions(id),
    report_type VARCHAR(50) DEFAULT 'test_report',
    template_version VARCHAR(20),
    file_path TEXT,
    file_format VARCHAR(10) DEFAULT 'pdf',
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'issued')),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    generated_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    issued_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_report_number ON reports(report_number);
CREATE INDEX idx_reports_test_execution_id ON reports(test_execution_id);
CREATE INDEX idx_reports_status ON reports(status);

-- ============================================================================
-- AUDIT TRAIL
-- ============================================================================

CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'approve', 'reject', 'complete')),
    user_id UUID REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    notes TEXT
);

CREATE INDEX idx_audit_trail_table_name ON audit_trail(table_name);
CREATE INDEX idx_audit_trail_record_id ON audit_trail(record_id);
CREATE INDEX idx_audit_trail_user_id ON audit_trail(user_id);
CREATE INDEX idx_audit_trail_timestamp ON audit_trail(timestamp);
CREATE INDEX idx_audit_trail_action ON audit_trail(action);

-- ============================================================================
-- NOTIFICATIONS
-- ============================================================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50) NOT NULL,  -- email, in_app, sms
    category VARCHAR(50),  -- test_complete, calibration_due, approval_needed, etc.
    subject VARCHAR(255),
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high')),
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    related_table VARCHAR(100),
    related_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_protocols_updated_at BEFORE UPDATE ON protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_requests_updated_at BEFORE UPDATE ON service_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_samples_updated_at BEFORE UPDATE ON samples
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equipment_updated_at BEFORE UPDATE ON equipment
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equipment_bookings_updated_at BEFORE UPDATE ON equipment_bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_executions_updated_at BEFORE UPDATE ON test_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create default admin user (password: admin123 - CHANGE IN PRODUCTION!)
INSERT INTO users (username, email, password_hash, first_name, last_name, role)
VALUES (
    'admin',
    'admin@pvlims.com',
    crypt('admin123', gen_salt('bf')),
    'System',
    'Administrator',
    'admin'
);

-- Add more seed data as needed
