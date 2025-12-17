-- =================================================================
-- Migration 010: QR Code Scanning - UP Migration
-- Description: Add QR scan logging and tracking
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Create qr_codes table if not exists
CREATE TABLE IF NOT EXISTS qr_codes (
    id SERIAL PRIMARY KEY,
    qr_code VARCHAR(100) UNIQUE NOT NULL,

    -- What does this QR code point to?
    entity_type VARCHAR(50), -- sample, equipment, service_request, document, etc.
    entity_id INTEGER,

    -- QR code data
    data JSONB,
    qr_image_path VARCHAR(200),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by_id INTEGER,

    -- Usage tracking
    first_scanned_at TIMESTAMP,
    last_scanned_at TIMESTAMP,
    scan_count INTEGER DEFAULT 0
);

-- Create qr_scan_log table if not exists
CREATE TABLE IF NOT EXISTS qr_scan_log (
    id SERIAL PRIMARY KEY,

    -- QR code data
    qr_code VARCHAR(200) NOT NULL,
    decoded_data JSONB,

    -- Entity reference
    entity_type VARCHAR(50),
    entity_id INTEGER,

    -- Scan details
    scanned_by_id INTEGER,
    scanned_by_name VARCHAR(100),
    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Location at scan
    scan_location VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,

    -- Device info
    device_type VARCHAR(50),
    device_info VARCHAR(200),

    -- Action taken
    action_type VARCHAR(50), -- check_in, check_out, status_update, inventory, transfer
    action_result VARCHAR(50), -- success, failed, partial

    -- Status update triggered
    status_changed BOOLEAN DEFAULT FALSE,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),

    -- Notes
    notes TEXT
);

-- Create qr_code_templates table for generating QR codes
CREATE TABLE IF NOT EXISTS qr_code_templates (
    id SERIAL PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,

    -- Template configuration
    prefix VARCHAR(20),
    sequence_format VARCHAR(50) DEFAULT '{PREFIX}-{YYYY}-{SEQ:5}',
    current_sequence INTEGER DEFAULT 0,

    -- QR code settings
    qr_size INTEGER DEFAULT 200,
    error_correction VARCHAR(10) DEFAULT 'M', -- L, M, Q, H
    include_logo BOOLEAN DEFAULT FALSE,
    logo_path VARCHAR(200),

    -- Data to encode
    data_fields JSONB DEFAULT '[]',

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create qr_batch_generation table for bulk QR code generation
CREATE TABLE IF NOT EXISTS qr_batch_generation (
    id SERIAL PRIMARY KEY,
    batch_number VARCHAR(50) UNIQUE NOT NULL,
    template_id INTEGER REFERENCES qr_code_templates(id),

    -- Batch details
    quantity INTEGER NOT NULL,
    generated_count INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed, failed

    -- Output
    output_path VARCHAR(255),
    zip_file_path VARCHAR(255),

    -- User
    requested_by_id INTEGER,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    -- Notes
    notes TEXT
);

-- Create qr_scan_actions table for configurable scan actions
CREATE TABLE IF NOT EXISTS qr_scan_actions (
    id SERIAL PRIMARY KEY,
    action_code VARCHAR(50) UNIQUE NOT NULL,
    action_name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,

    -- Action configuration
    action_type VARCHAR(50) NOT NULL, -- status_change, location_update, check_in, check_out, custom
    status_transition JSONB, -- {from: [], to: 'new_status'}
    required_fields JSONB DEFAULT '[]',
    validation_rules JSONB,

    -- UI configuration
    confirmation_required BOOLEAN DEFAULT FALSE,
    confirmation_message TEXT,
    success_message TEXT,

    -- Permissions
    allowed_roles JSONB DEFAULT '[]',

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create qr_scan_workflows table for multi-step scan workflows
CREATE TABLE IF NOT EXISTS qr_scan_workflows (
    id SERIAL PRIMARY KEY,
    workflow_code VARCHAR(50) UNIQUE NOT NULL,
    workflow_name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Workflow configuration
    entity_type VARCHAR(50) NOT NULL,
    steps JSONB NOT NULL DEFAULT '[]', -- Array of step definitions
    current_step INTEGER DEFAULT 1,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_qr_codes_code ON qr_codes(qr_code);
CREATE INDEX IF NOT EXISTS idx_qr_codes_entity ON qr_codes(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_active ON qr_codes(is_active);
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_qr_code ON qr_scan_log(qr_code);
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_entity ON qr_scan_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_timestamp ON qr_scan_log(scan_timestamp);
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_action ON qr_scan_log(action_type);
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_user ON qr_scan_log(scanned_by_id);
CREATE INDEX IF NOT EXISTS idx_qr_code_templates_code ON qr_code_templates(template_code);
CREATE INDEX IF NOT EXISTS idx_qr_code_templates_entity ON qr_code_templates(entity_type);
CREATE INDEX IF NOT EXISTS idx_qr_batch_generation_batch ON qr_batch_generation(batch_number);
CREATE INDEX IF NOT EXISTS idx_qr_batch_generation_status ON qr_batch_generation(status);
CREATE INDEX IF NOT EXISTS idx_qr_scan_actions_code ON qr_scan_actions(action_code);
CREATE INDEX IF NOT EXISTS idx_qr_scan_actions_entity ON qr_scan_actions(entity_type);
CREATE INDEX IF NOT EXISTS idx_qr_scan_workflows_code ON qr_scan_workflows(workflow_code);

-- Create trigger to update QR code scan statistics
CREATE OR REPLACE FUNCTION update_qr_code_scan_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE qr_codes
    SET last_scanned_at = NEW.scan_timestamp,
        scan_count = scan_count + 1,
        first_scanned_at = COALESCE(first_scanned_at, NEW.scan_timestamp)
    WHERE qr_code = NEW.qr_code;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS qr_scan_log_update_stats ON qr_scan_log;
CREATE TRIGGER qr_scan_log_update_stats
AFTER INSERT ON qr_scan_log
FOR EACH ROW
EXECUTE FUNCTION update_qr_code_scan_stats();

-- Create function to generate next QR code sequence
CREATE OR REPLACE FUNCTION get_next_qr_sequence(p_template_code VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    v_template qr_code_templates%ROWTYPE;
    v_new_sequence INTEGER;
    v_qr_code VARCHAR;
BEGIN
    SELECT * INTO v_template FROM qr_code_templates WHERE template_code = p_template_code;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Template not found: %', p_template_code;
    END IF;

    v_new_sequence := v_template.current_sequence + 1;

    UPDATE qr_code_templates
    SET current_sequence = v_new_sequence
    WHERE template_code = p_template_code;

    v_qr_code := REPLACE(v_template.sequence_format, '{PREFIX}', COALESCE(v_template.prefix, ''));
    v_qr_code := REPLACE(v_qr_code, '{YYYY}', TO_CHAR(CURRENT_DATE, 'YYYY'));
    v_qr_code := REPLACE(v_qr_code, '{SEQ:5}', LPAD(v_new_sequence::TEXT, 5, '0'));

    RETURN v_qr_code;
END;
$$ LANGUAGE plpgsql;

-- Insert default QR code templates
INSERT INTO qr_code_templates (template_code, template_name, entity_type, prefix, sequence_format)
VALUES
    ('QR-SAMPLE', 'Sample QR Code', 'sample', 'SPL', '{PREFIX}-{YYYY}-{SEQ:5}'),
    ('QR-EQUIPMENT', 'Equipment QR Code', 'equipment', 'EQP', '{PREFIX}-{YYYY}-{SEQ:5}'),
    ('QR-DOCUMENT', 'Document QR Code', 'document', 'DOC', '{PREFIX}-{YYYY}-{SEQ:5}'),
    ('QR-LOCATION', 'Location QR Code', 'location', 'LOC', '{PREFIX}-{YYYY}-{SEQ:5}')
ON CONFLICT (template_code) DO NOTHING;

-- Insert default scan actions
INSERT INTO qr_scan_actions (action_code, action_name, entity_type, action_type, status_transition)
VALUES
    ('SAMPLE_CHECK_IN', 'Sample Check-In', 'sample', 'status_change', '{"from": ["received", "in_test"], "to": "inspected"}'),
    ('SAMPLE_CHECK_OUT', 'Sample Check-Out', 'sample', 'status_change', '{"from": ["inspected", "allocated"], "to": "in_test"}'),
    ('EQUIPMENT_START', 'Start Equipment Use', 'equipment', 'status_change', '{"from": ["available"], "to": "in_use"}'),
    ('EQUIPMENT_END', 'End Equipment Use', 'equipment', 'status_change', '{"from": ["in_use"], "to": "available"}')
ON CONFLICT (action_code) DO NOTHING;

COMMIT;
