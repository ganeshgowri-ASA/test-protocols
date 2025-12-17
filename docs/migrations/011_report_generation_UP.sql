-- =================================================================
-- Migration 011: Report Generation - UP Migration
-- Description: Add report templates and generation history
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Create report_templates table if not exists
CREATE TABLE IF NOT EXISTS report_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    template_type VARCHAR(100), -- IEC 61215, IEC 61730, NABL, Custom
    version VARCHAR(20),

    -- Template structure
    header_content JSONB,
    body_sections JSONB,
    footer_content JSONB,

    -- Branding
    logo_path VARCHAR(255),
    color_scheme JSONB,

    -- Status and metadata
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,

    -- Audit fields
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Create generated_reports table if not exists
CREATE TABLE IF NOT EXISTS generated_reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) UNIQUE NOT NULL,
    report_number VARCHAR(100) UNIQUE NOT NULL,
    report_title VARCHAR(255) NOT NULL,
    template_id VARCHAR(50),

    -- Associated data
    sample_ids JSONB,
    test_ids JSONB,

    -- File details
    file_path VARCHAR(255),
    file_size INTEGER,
    language VARCHAR(50) DEFAULT 'English',

    -- Status tracking
    status VARCHAR(50) DEFAULT 'Draft',

    -- Signatures
    signatures JSONB,

    -- Distribution tracking
    distributed_to JSONB,
    distribution_date TIMESTAMP,

    -- Metadata
    generated_by VARCHAR(100),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scheduled_reports table if not exists
CREATE TABLE IF NOT EXISTS scheduled_reports (
    id SERIAL PRIMARY KEY,
    schedule_id VARCHAR(50) UNIQUE NOT NULL,
    schedule_name VARCHAR(200) NOT NULL,
    template_id VARCHAR(50),

    -- Schedule parameters
    frequency VARCHAR(50), -- Daily, Weekly, Monthly, On Test Completion
    trigger_time VARCHAR(10),

    -- Filters for report data
    filters JSONB,

    -- Distribution configuration
    recipients JSONB,

    -- Status and execution tracking
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    last_status VARCHAR(50),

    -- Audit fields
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Create report_sections table for reusable report components
CREATE TABLE IF NOT EXISTS report_sections (
    id SERIAL PRIMARY KEY,
    section_code VARCHAR(50) UNIQUE NOT NULL,
    section_name VARCHAR(200) NOT NULL,
    section_type VARCHAR(50), -- header, body, footer, table, chart, signature

    -- Content
    content_template TEXT,
    placeholders JSONB DEFAULT '[]',
    styling JSONB,

    -- Usage
    applicable_report_types JSONB DEFAULT '[]',

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create report_distribution_log table
CREATE TABLE IF NOT EXISTS report_distribution_log (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES generated_reports(id) ON DELETE CASCADE,
    recipient_email VARCHAR(100),
    recipient_name VARCHAR(100),
    distribution_method VARCHAR(50), -- email, portal, print, download
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered BOOLEAN DEFAULT FALSE,
    delivered_at TIMESTAMP,
    opened BOOLEAN DEFAULT FALSE,
    opened_at TIMESTAMP,
    download_count INTEGER DEFAULT 0,
    notes TEXT
);

-- Create report_signatures table for digital signature tracking
CREATE TABLE IF NOT EXISTS report_signatures (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES generated_reports(id) ON DELETE CASCADE,
    signer_id INTEGER,
    signer_name VARCHAR(100) NOT NULL,
    signer_role VARCHAR(50) NOT NULL, -- author, reviewer, approver
    signer_title VARCHAR(100),

    -- Signature data
    signature_data TEXT, -- Base64 encoded signature image or digital signature
    signature_type VARCHAR(20), -- drawn, typed, digital
    signature_hash VARCHAR(64),

    -- Status
    signed_at TIMESTAMP,
    ip_address VARCHAR(50),

    -- Certificate info (for digital signatures)
    certificate_serial VARCHAR(100),
    certificate_issuer VARCHAR(200),

    -- Notes
    notes TEXT
);

-- Create report_comments table for review comments
CREATE TABLE IF NOT EXISTS report_comments (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES generated_reports(id) ON DELETE CASCADE,
    comment_type VARCHAR(20), -- review, correction, approval, general
    section_reference VARCHAR(100),
    comment_text TEXT NOT NULL,
    author_id INTEGER,
    author_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by_id INTEGER,
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

-- Create report_audit_trail table
CREATE TABLE IF NOT EXISTS report_audit_trail (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES generated_reports(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- created, edited, reviewed, approved, signed, distributed
    action_details JSONB,
    performed_by_id INTEGER,
    performed_by_name VARCHAR(100),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_report_templates_id ON report_templates(template_id);
CREATE INDEX IF NOT EXISTS idx_report_templates_type ON report_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_report_templates_active ON report_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_generated_reports_id ON generated_reports(report_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_number ON generated_reports(report_number);
CREATE INDEX IF NOT EXISTS idx_generated_reports_status ON generated_reports(status);
CREATE INDEX IF NOT EXISTS idx_generated_reports_template ON generated_reports(template_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_generated ON generated_reports(generated_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_id ON scheduled_reports(schedule_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_active ON scheduled_reports(is_active);
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_next_run ON scheduled_reports(next_run);
CREATE INDEX IF NOT EXISTS idx_report_sections_code ON report_sections(section_code);
CREATE INDEX IF NOT EXISTS idx_report_distribution_log_report ON report_distribution_log(report_id);
CREATE INDEX IF NOT EXISTS idx_report_signatures_report ON report_signatures(report_id);
CREATE INDEX IF NOT EXISTS idx_report_comments_report ON report_comments(report_id);
CREATE INDEX IF NOT EXISTS idx_report_audit_trail_report ON report_audit_trail(report_id);

-- Create trigger to update report_templates timestamp
CREATE OR REPLACE FUNCTION update_report_templates_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS report_templates_update_timestamp ON report_templates;
CREATE TRIGGER report_templates_update_timestamp
BEFORE UPDATE ON report_templates
FOR EACH ROW
EXECUTE FUNCTION update_report_templates_timestamp();

-- Create function to generate report number
CREATE OR REPLACE FUNCTION generate_report_number(p_prefix VARCHAR DEFAULT 'RPT')
RETURNS VARCHAR AS $$
DECLARE
    v_year VARCHAR(4);
    v_month VARCHAR(2);
    v_sequence INTEGER;
    v_report_number VARCHAR;
BEGIN
    v_year := TO_CHAR(CURRENT_DATE, 'YYYY');
    v_month := TO_CHAR(CURRENT_DATE, 'MM');

    SELECT COALESCE(MAX(
        NULLIF(REGEXP_REPLACE(report_number, '[^0-9]', '', 'g'), '')::INTEGER
    ), 0) + 1
    INTO v_sequence
    FROM generated_reports
    WHERE report_number LIKE p_prefix || '-' || v_year || '-%';

    v_report_number := p_prefix || '-' || v_year || '-' || LPAD(v_sequence::TEXT, 5, '0');

    RETURN v_report_number;
END;
$$ LANGUAGE plpgsql;

-- Insert default report templates
INSERT INTO report_templates (template_id, template_name, template_type, version, is_active, description)
VALUES
    ('TPL-IEC61215', 'IEC 61215 Test Report', 'IEC 61215', '1.0', TRUE, 'Standard template for IEC 61215 PV module performance testing'),
    ('TPL-IEC61730', 'IEC 61730 Safety Report', 'IEC 61730', '1.0', TRUE, 'Standard template for IEC 61730 PV module safety testing'),
    ('TPL-NABL', 'NABL Accredited Report', 'NABL', '1.0', TRUE, 'Template compliant with NABL accreditation requirements'),
    ('TPL-CUSTOM', 'Custom Test Report', 'Custom', '1.0', TRUE, 'Customizable template for non-standard testing'),
    ('TPL-SUMMARY', 'Test Summary Report', 'Summary', '1.0', TRUE, 'Summary report template for multiple tests')
ON CONFLICT (template_id) DO NOTHING;

-- Insert default report sections
INSERT INTO report_sections (section_code, section_name, section_type, is_active)
VALUES
    ('SEC-HEADER', 'Report Header', 'header', TRUE),
    ('SEC-CLIENT', 'Client Information', 'body', TRUE),
    ('SEC-SAMPLE', 'Sample Details', 'body', TRUE),
    ('SEC-RESULTS', 'Test Results', 'body', TRUE),
    ('SEC-CHARTS', 'Data Charts', 'chart', TRUE),
    ('SEC-CONCLUSION', 'Conclusions', 'body', TRUE),
    ('SEC-SIGNATURES', 'Signature Block', 'signature', TRUE),
    ('SEC-FOOTER', 'Report Footer', 'footer', TRUE)
ON CONFLICT (section_code) DO NOTHING;

COMMIT;
