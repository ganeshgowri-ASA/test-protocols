-- ============================================================================
-- Migration: 002_sample_management_UP.sql
-- Description: Create tables for comprehensive Sample Management & Tracking System
-- Date: 2024
-- ============================================================================

-- ============================================================================
-- NEW ENUM TYPES (for PostgreSQL - SQLite will use VARCHAR)
-- ============================================================================

-- Sample Status Enum
-- Status workflow: RECEIVED → INSPECTED → ALLOCATED → ASSIGNED → IN_TEST → COMPLETED → ANALYZED → REPORTED
CREATE TYPE sample_status AS ENUM (
    'received',
    'inspected',
    'allocated',
    'assigned',
    'in_test',
    'completed',
    'analyzed',
    'reported',
    'rejected',
    'on_hold'
);

-- Document Category Enum
CREATE TYPE document_category AS ENUM (
    'procedure',
    'work_instruction',
    'form',
    'record',
    'specification',
    'drawing',
    'certificate',
    'report',
    'manual',
    'policy',
    'other'
);

-- Training Status Enum
CREATE TYPE training_status AS ENUM (
    'scheduled',
    'in_progress',
    'completed',
    'expired',
    'cancelled'
);

-- BOM Item Type Enum
CREATE TYPE bom_item_type AS ENUM (
    'material',
    'consumable',
    'equipment',
    'service',
    'labor'
);

-- ============================================================================
-- SAMPLE RECEIPTS TABLE
-- Tracks physical receipt of samples
-- ============================================================================
CREATE TABLE IF NOT EXISTS sample_receipts (
    id SERIAL PRIMARY KEY,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,

    -- Link to service request
    service_request_id INTEGER REFERENCES service_requests(id),

    -- Receipt details
    received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    received_by_id INTEGER REFERENCES users(id),

    -- Client/Source information
    client_name VARCHAR(100),
    client_reference VARCHAR(100),
    courier_name VARCHAR(100),
    tracking_number VARCHAR(100),

    -- Package details
    package_count INTEGER DEFAULT 1,
    package_condition VARCHAR(50), -- good, damaged, sealed, opened
    package_photos JSON, -- List of photo paths

    -- Sample counts
    expected_sample_count INTEGER,
    actual_sample_count INTEGER,
    quantity_mismatch BOOLEAN DEFAULT FALSE,
    mismatch_notes TEXT,

    -- Approval workflow
    requires_supervisor_approval BOOLEAN DEFAULT FALSE,
    supervisor_approved BOOLEAN,
    supervisor_id INTEGER REFERENCES users(id),
    approval_date TIMESTAMP,
    approval_notes TEXT,

    -- Status and notes
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, processed
    remarks TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sample_receipts_service_request ON sample_receipts(service_request_id);
CREATE INDEX idx_sample_receipts_received_date ON sample_receipts(received_date);
CREATE INDEX idx_sample_receipts_status ON sample_receipts(status);

-- ============================================================================
-- SAMPLES TABLE
-- Core sample tracking with auto-generated IDs
-- ============================================================================
CREATE TABLE IF NOT EXISTS samples (
    id SERIAL PRIMARY KEY,

    -- Auto-generated identifiers
    sample_id VARCHAR(50) UNIQUE NOT NULL, -- SAMPLE-YYYY-XXXXX format
    project_id VARCHAR(50), -- PROJECT-YYYY-XXXXX format

    -- Links
    service_request_id INTEGER REFERENCES service_requests(id),
    receipt_id INTEGER REFERENCES sample_receipts(id),
    inspection_id INTEGER REFERENCES incoming_inspections(id),

    -- Sample details
    sample_type VARCHAR(50), -- module, cell, array, component
    manufacturer VARCHAR(100),
    model_number VARCHAR(100),
    serial_number VARCHAR(100),
    batch_number VARCHAR(100),

    -- Physical properties
    length_mm FLOAT,
    width_mm FLOAT,
    thickness_mm FLOAT,
    weight_kg FLOAT,

    -- QR Code
    qr_code VARCHAR(200) UNIQUE,
    qr_code_image_path VARCHAR(200),
    qr_data JSON, -- Encoded QR data

    -- Current status and location
    status VARCHAR(20) DEFAULT 'received',
    current_location VARCHAR(100),
    storage_location VARCHAR(100),

    -- Workflow tracking
    allocation_date TIMESTAMP,
    allocated_by_id INTEGER REFERENCES users(id),

    -- Test assignment tracking
    assigned_protocol_ids JSON, -- List of assigned protocol IDs
    current_test_id INTEGER,
    tests_completed INTEGER DEFAULT 0,
    tests_total INTEGER DEFAULT 0,

    -- Results summary
    overall_result VARCHAR(20), -- pass, fail, conditional
    result_summary TEXT,

    -- Metadata
    specifications JSON, -- Additional specs
    notes TEXT,
    photos JSON, -- List of photo paths

    -- Chain of custody
    custody_history JSON, -- List of custody transfers

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    disposed_at TIMESTAMP
);

CREATE INDEX idx_samples_sample_id ON samples(sample_id);
CREATE INDEX idx_samples_project_id ON samples(project_id);
CREATE INDEX idx_samples_service_request ON samples(service_request_id);
CREATE INDEX idx_samples_status ON samples(status);
CREATE INDEX idx_samples_qr_code ON samples(qr_code);
CREATE INDEX idx_samples_current_location ON samples(current_location);

-- ============================================================================
-- SAMPLE STATUS HISTORY TABLE
-- Complete audit trail of sample status changes
-- ============================================================================
CREATE TABLE IF NOT EXISTS sample_status_history (
    id SERIAL PRIMARY KEY,

    -- Sample reference
    sample_id INTEGER REFERENCES samples(id) NOT NULL,

    -- Status change details
    previous_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,

    -- Location change
    previous_location VARCHAR(100),
    new_location VARCHAR(100),

    -- Who made the change
    changed_by_id INTEGER REFERENCES users(id),
    changed_by_name VARCHAR(100),

    -- How it was changed
    change_source VARCHAR(50), -- manual, qr_scan, system, workflow
    qr_scan_id INTEGER, -- Reference to scan event if applicable

    -- Additional info
    reason TEXT,
    notes TEXT,
    metadata JSON, -- Additional context data

    -- Timestamp
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sample_status_history_sample ON sample_status_history(sample_id);
CREATE INDEX idx_sample_status_history_changed_at ON sample_status_history(changed_at);
CREATE INDEX idx_sample_status_history_status ON sample_status_history(new_status);

-- ============================================================================
-- ROUTE CARDS TABLE
-- Workflow documentation for samples
-- ============================================================================
CREATE TABLE IF NOT EXISTS route_cards (
    id SERIAL PRIMARY KEY,
    route_card_number VARCHAR(50) UNIQUE NOT NULL,

    -- Sample reference
    sample_id INTEGER REFERENCES samples(id),
    project_id VARCHAR(50),

    -- Service request link
    service_request_id INTEGER REFERENCES service_requests(id),

    -- Route card details
    title VARCHAR(200),
    description TEXT,

    -- Workflow steps
    workflow_steps JSON, -- List of steps with status
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER,

    -- Assigned protocols
    assigned_protocols JSON, -- List of protocol assignments

    -- Timeline
    planned_start_date TIMESTAMP,
    planned_end_date TIMESTAMP,
    actual_start_date TIMESTAMP,
    actual_end_date TIMESTAMP,

    -- PDF generation
    pdf_path VARCHAR(200),
    pdf_generated_at TIMESTAMP,

    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- draft, active, completed, cancelled

    -- Personnel
    created_by_id INTEGER REFERENCES users(id),
    assigned_to_id INTEGER REFERENCES users(id),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_route_cards_sample ON route_cards(sample_id);
CREATE INDEX idx_route_cards_service_request ON route_cards(service_request_id);
CREATE INDEX idx_route_cards_status ON route_cards(status);

-- ============================================================================
-- SAMPLE TEST ASSIGNMENTS TABLE
-- Assignment of samples to specific tests
-- ============================================================================
CREATE TABLE IF NOT EXISTS sample_test_assignments (
    id SERIAL PRIMARY KEY,
    assignment_number VARCHAR(50) UNIQUE NOT NULL,

    -- Links
    sample_id INTEGER REFERENCES samples(id) NOT NULL,
    test_execution_id INTEGER REFERENCES test_executions(id),
    protocol_id INTEGER REFERENCES test_protocols(id) NOT NULL,
    route_card_id INTEGER REFERENCES route_cards(id),

    -- Assignment details
    sequence_number INTEGER, -- Order in testing sequence
    priority INTEGER DEFAULT 5, -- 1=highest, 10=lowest

    -- Personnel
    assigned_by_id INTEGER REFERENCES users(id),
    assigned_to_id INTEGER REFERENCES users(id),

    -- Scheduling
    scheduled_start TIMESTAMP,
    scheduled_end TIMESTAMP,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,

    -- Equipment booking
    equipment_booking_id INTEGER REFERENCES equipment_bookings(id),
    required_equipment JSON,

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed, cancelled, on_hold

    -- Results
    test_passed BOOLEAN,
    result_summary TEXT,

    -- Notes
    instructions TEXT,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sample_test_assignments_sample ON sample_test_assignments(sample_id);
CREATE INDEX idx_sample_test_assignments_protocol ON sample_test_assignments(protocol_id);
CREATE INDEX idx_sample_test_assignments_status ON sample_test_assignments(status);
CREATE INDEX idx_sample_test_assignments_scheduled ON sample_test_assignments(scheduled_start);

-- ============================================================================
-- SAMPLE INVENTORY TABLE
-- Inventory tracking and storage management
-- ============================================================================
CREATE TABLE IF NOT EXISTS sample_inventory (
    id SERIAL PRIMARY KEY,

    -- Sample reference
    sample_id INTEGER REFERENCES samples(id),
    sample_id_code VARCHAR(50), -- SAMPLE-YYYY-XXXXX

    -- Location tracking
    storage_area VARCHAR(50), -- warehouse, lab, chamber, etc.
    storage_zone VARCHAR(50), -- A, B, C, etc.
    storage_rack VARCHAR(50),
    storage_shelf VARCHAR(50),
    storage_position VARCHAR(50),
    full_location_path VARCHAR(200),

    -- Physical status
    condition VARCHAR(50), -- excellent, good, fair, poor, damaged
    condition_notes TEXT,
    photos JSON,

    -- Inventory status
    inventory_status VARCHAR(20) DEFAULT 'in_stock', -- in_stock, in_test, disposed, returned, shipped

    -- Check in/out tracking
    checked_out BOOLEAN DEFAULT FALSE,
    checked_out_by_id INTEGER REFERENCES users(id),
    checked_out_at TIMESTAMP,
    checked_out_reason TEXT,
    expected_return TIMESTAMP,

    -- Return tracking
    checked_in_by_id INTEGER REFERENCES users(id),
    checked_in_at TIMESTAMP,

    -- Disposal/Return
    disposal_date TIMESTAMP,
    disposal_method VARCHAR(50),
    disposal_notes TEXT,
    return_date TIMESTAMP,
    return_tracking_number VARCHAR(100),

    -- Last inventory count
    last_inventory_date TIMESTAMP,
    inventoried_by_id INTEGER REFERENCES users(id),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sample_inventory_sample ON sample_inventory(sample_id);
CREATE INDEX idx_sample_inventory_location ON sample_inventory(storage_area, storage_zone, storage_rack);
CREATE INDEX idx_sample_inventory_status ON sample_inventory(inventory_status);

-- ============================================================================
-- STAFF TRAINING TABLE
-- Training management and competency tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS staff_training (
    id SERIAL PRIMARY KEY,
    training_id VARCHAR(50) UNIQUE NOT NULL,

    -- Training details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- safety, equipment, protocol, qms, general
    training_type VARCHAR(50), -- initial, refresher, advanced, certification

    -- Requirements
    required_for_roles JSON, -- List of roles that require this training
    required_for_protocols JSON, -- List of protocols requiring this training
    prerequisite_trainings JSON, -- List of prerequisite training IDs

    -- Content
    materials_path VARCHAR(200),
    duration_hours FLOAT,
    assessment_required BOOLEAN DEFAULT TRUE,
    passing_score FLOAT DEFAULT 80.0,

    -- Validity
    valid_months INTEGER DEFAULT 12, -- Training validity period

    -- Metadata
    created_by_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_staff_training_category ON staff_training(category);
CREATE INDEX idx_staff_training_active ON staff_training(is_active);

-- ============================================================================
-- STAFF TRAINING RECORDS TABLE
-- Individual training completion records
-- ============================================================================
CREATE TABLE IF NOT EXISTS staff_training_records (
    id SERIAL PRIMARY KEY,
    record_number VARCHAR(50) UNIQUE NOT NULL,

    -- Links
    training_id INTEGER REFERENCES staff_training(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,

    -- Training session
    scheduled_date TIMESTAMP,
    completion_date TIMESTAMP,
    trainer_id INTEGER REFERENCES users(id),
    trainer_name VARCHAR(100),

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, expired, cancelled

    -- Assessment
    assessment_score FLOAT,
    assessment_passed BOOLEAN,
    assessment_date TIMESTAMP,
    assessment_notes TEXT,

    -- Certificate
    certificate_number VARCHAR(50),
    certificate_path VARCHAR(200),

    -- Validity tracking
    expiry_date TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,

    -- Notes
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_staff_training_records_training ON staff_training_records(training_id);
CREATE INDEX idx_staff_training_records_user ON staff_training_records(user_id);
CREATE INDEX idx_staff_training_records_status ON staff_training_records(status);
CREATE INDEX idx_staff_training_records_expiry ON staff_training_records(expiry_date);

-- ============================================================================
-- DOCUMENT MANAGEMENT TABLE
-- Document control and version management
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR(50) UNIQUE NOT NULL,

    -- Document details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- procedure, work_instruction, form, record, specification, etc.
    document_type VARCHAR(50), -- pdf, word, excel, image, etc.

    -- Classification
    department VARCHAR(50),
    process_area VARCHAR(100),
    tags JSON, -- List of tags for searching

    -- Version control
    version VARCHAR(20) DEFAULT '1.0',
    revision_number INTEGER DEFAULT 1,
    is_current_version BOOLEAN DEFAULT TRUE,
    previous_version_id INTEGER REFERENCES documents(id),

    -- File storage
    file_path VARCHAR(200),
    file_name VARCHAR(200),
    file_size_bytes INTEGER,
    file_hash VARCHAR(64), -- SHA-256 hash for integrity

    -- Review and approval
    author_id INTEGER REFERENCES users(id),
    reviewer_id INTEGER REFERENCES users(id),
    approver_id INTEGER REFERENCES users(id),

    review_date TIMESTAMP,
    approval_date TIMESTAMP,

    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- draft, in_review, approved, superseded, obsolete

    -- Effective dates
    effective_date TIMESTAMP,
    next_review_date TIMESTAMP,
    obsolete_date TIMESTAMP,

    -- Access control
    access_level VARCHAR(20) DEFAULT 'internal', -- public, internal, confidential, restricted
    allowed_roles JSON, -- List of roles with access

    -- Distribution
    distribution_list JSON, -- List of user IDs for distribution

    -- Notes
    change_summary TEXT,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_number ON documents(document_number);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_current ON documents(is_current_version);

-- ============================================================================
-- DOCUMENT ACCESS LOG TABLE
-- Track document access and downloads
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_access_log (
    id SERIAL PRIMARY KEY,

    -- Document reference
    document_id INTEGER REFERENCES documents(id) NOT NULL,

    -- User
    user_id INTEGER REFERENCES users(id),
    user_name VARCHAR(100),

    -- Access details
    access_type VARCHAR(20), -- view, download, print, edit
    access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Context
    ip_address VARCHAR(50),
    user_agent VARCHAR(200),

    -- Notes
    notes TEXT
);

CREATE INDEX idx_document_access_log_document ON document_access_log(document_id);
CREATE INDEX idx_document_access_log_user ON document_access_log(user_id);
CREATE INDEX idx_document_access_log_timestamp ON document_access_log(access_timestamp);

-- ============================================================================
-- BOM MANAGEMENT TABLE
-- Bill of Materials for testing
-- ============================================================================
CREATE TABLE IF NOT EXISTS bom_items (
    id SERIAL PRIMARY KEY,
    item_code VARCHAR(50) UNIQUE NOT NULL,

    -- Item details
    name VARCHAR(200) NOT NULL,
    description TEXT,
    item_type VARCHAR(20), -- material, consumable, equipment, service, labor
    category VARCHAR(50),

    -- Specifications
    specifications JSON,
    unit VARCHAR(20), -- each, kg, meter, hour, etc.

    -- Inventory
    current_stock FLOAT DEFAULT 0,
    minimum_stock FLOAT DEFAULT 0,
    reorder_point FLOAT DEFAULT 0,
    reorder_quantity FLOAT,

    -- Cost tracking
    unit_cost FLOAT DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    cost_center VARCHAR(50),

    -- Supplier info
    supplier_name VARCHAR(100),
    supplier_code VARCHAR(50),
    supplier_part_number VARCHAR(50),
    lead_time_days INTEGER,

    -- Shelf life
    has_expiry BOOLEAN DEFAULT FALSE,
    shelf_life_days INTEGER,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bom_items_code ON bom_items(item_code);
CREATE INDEX idx_bom_items_type ON bom_items(item_type);
CREATE INDEX idx_bom_items_category ON bom_items(category);
CREATE INDEX idx_bom_items_stock ON bom_items(current_stock);

-- ============================================================================
-- BOM PROTOCOL REQUIREMENTS TABLE
-- Link BOM items to test protocols
-- ============================================================================
CREATE TABLE IF NOT EXISTS bom_protocol_requirements (
    id SERIAL PRIMARY KEY,

    -- Links
    protocol_id INTEGER REFERENCES test_protocols(id) NOT NULL,
    bom_item_id INTEGER REFERENCES bom_items(id) NOT NULL,

    -- Requirement details
    quantity_per_test FLOAT NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint
    UNIQUE(protocol_id, bom_item_id)
);

CREATE INDEX idx_bom_protocol_req_protocol ON bom_protocol_requirements(protocol_id);
CREATE INDEX idx_bom_protocol_req_item ON bom_protocol_requirements(bom_item_id);

-- ============================================================================
-- BOM USAGE LOG TABLE
-- Track consumption of BOM items
-- ============================================================================
CREATE TABLE IF NOT EXISTS bom_usage_log (
    id SERIAL PRIMARY KEY,

    -- Item reference
    bom_item_id INTEGER REFERENCES bom_items(id) NOT NULL,

    -- Usage context
    test_execution_id INTEGER REFERENCES test_executions(id),
    sample_id INTEGER REFERENCES samples(id),
    service_request_id INTEGER REFERENCES service_requests(id),

    -- Usage details
    quantity_used FLOAT NOT NULL,
    usage_type VARCHAR(20), -- consumed, returned, wasted

    -- User
    used_by_id INTEGER REFERENCES users(id),

    -- Lot/Batch tracking
    lot_number VARCHAR(50),
    expiry_date TIMESTAMP,

    -- Notes
    notes TEXT,

    -- Timestamp
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bom_usage_log_item ON bom_usage_log(bom_item_id);
CREATE INDEX idx_bom_usage_log_test ON bom_usage_log(test_execution_id);
CREATE INDEX idx_bom_usage_log_date ON bom_usage_log(used_at);

-- ============================================================================
-- QR SCAN LOG TABLE
-- Log all QR code scans for tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS qr_scan_log (
    id SERIAL PRIMARY KEY,

    -- QR code data
    qr_code VARCHAR(200) NOT NULL,
    decoded_data JSON,

    -- Entity reference (from decoded data)
    entity_type VARCHAR(50), -- sample, equipment, document, etc.
    entity_id INTEGER,

    -- Scan details
    scanned_by_id INTEGER REFERENCES users(id),
    scanned_by_name VARCHAR(100),
    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Location at scan
    scan_location VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,

    -- Device info
    device_type VARCHAR(50), -- webcam, mobile, scanner
    device_info VARCHAR(200),

    -- Action taken
    action_type VARCHAR(50), -- check_in, check_out, location_update, test_start, etc.
    action_result VARCHAR(50), -- success, failed, error

    -- Status update triggered
    status_changed BOOLEAN DEFAULT FALSE,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),

    -- Notes
    notes TEXT
);

CREATE INDEX idx_qr_scan_log_qr_code ON qr_scan_log(qr_code);
CREATE INDEX idx_qr_scan_log_entity ON qr_scan_log(entity_type, entity_id);
CREATE INDEX idx_qr_scan_log_timestamp ON qr_scan_log(scan_timestamp);
CREATE INDEX idx_qr_scan_log_user ON qr_scan_log(scanned_by_id);

-- ============================================================================
-- CALIBRATION RECORDS TABLE (for Equipment)
-- ============================================================================
CREATE TABLE IF NOT EXISTS calibration_records (
    id SERIAL PRIMARY KEY,
    calibration_number VARCHAR(50) UNIQUE NOT NULL,

    -- Equipment reference
    equipment_id INTEGER REFERENCES equipment(id) NOT NULL,

    -- Calibration details
    calibration_date TIMESTAMP NOT NULL,
    next_calibration_date TIMESTAMP,
    calibration_type VARCHAR(50), -- initial, periodic, after_repair

    -- Provider
    performed_by VARCHAR(100), -- internal, external provider name
    provider_certificate VARCHAR(100),
    technician_name VARCHAR(100),

    -- Results
    calibration_passed BOOLEAN,
    deviation_found BOOLEAN DEFAULT FALSE,
    deviation_details TEXT,
    adjustment_made BOOLEAN DEFAULT FALSE,
    adjustment_details TEXT,

    -- Documentation
    certificate_number VARCHAR(100),
    certificate_path VARCHAR(200),
    report_path VARCHAR(200),

    -- Traceability
    reference_standards JSON, -- Standards used for calibration

    -- Notes
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id)
);

CREATE INDEX idx_calibration_records_equipment ON calibration_records(equipment_id);
CREATE INDEX idx_calibration_records_date ON calibration_records(calibration_date);
CREATE INDEX idx_calibration_records_next ON calibration_records(next_calibration_date);

-- ============================================================================
-- ALTER EXISTING TABLES
-- ============================================================================

-- Add expected_sample_quantity to service_requests
ALTER TABLE service_requests ADD COLUMN IF NOT EXISTS expected_sample_quantity INTEGER DEFAULT 1;
ALTER TABLE service_requests ADD COLUMN IF NOT EXISTS actual_sample_quantity INTEGER;
ALTER TABLE service_requests ADD COLUMN IF NOT EXISTS quantity_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE service_requests ADD COLUMN IF NOT EXISTS receipt_id INTEGER REFERENCES sample_receipts(id);

-- Add receipt linkage to incoming_inspections
ALTER TABLE incoming_inspections ADD COLUMN IF NOT EXISTS receipt_id INTEGER REFERENCES sample_receipts(id);
ALTER TABLE incoming_inspections ADD COLUMN IF NOT EXISTS allocation_triggered BOOLEAN DEFAULT FALSE;
ALTER TABLE incoming_inspections ADD COLUMN IF NOT EXISTS allocated_sample_id INTEGER;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
