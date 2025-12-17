-- =================================================================
-- Migration 007: Document Management - UP Migration
-- Description: Add document versioning and approval workflow
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Create documents table if not exists
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'other',
    document_type VARCHAR(50),

    -- Classification
    department VARCHAR(50),
    process_area VARCHAR(100),
    tags JSONB DEFAULT '[]',

    -- Version control
    version VARCHAR(20) DEFAULT '1.0',
    revision_number INTEGER DEFAULT 1,
    is_current_version BOOLEAN DEFAULT TRUE,
    previous_version_id INTEGER REFERENCES documents(id),

    -- File storage
    file_path VARCHAR(200),
    file_name VARCHAR(200),
    file_size_bytes INTEGER,
    file_hash VARCHAR(64),

    -- Review and approval
    author_id INTEGER,
    reviewer_id INTEGER,
    approver_id INTEGER,
    review_date TIMESTAMP,
    approval_date TIMESTAMP,

    -- Digital signatures
    author_signature TEXT,
    author_signature_date TIMESTAMP,
    reviewer_signature TEXT,
    reviewer_signature_date TIMESTAMP,
    approver_signature TEXT,
    approver_signature_date TIMESTAMP,

    -- Status
    status VARCHAR(20) DEFAULT 'draft',

    -- Effective dates
    effective_date TIMESTAMP,
    next_review_date TIMESTAMP,
    obsolete_date TIMESTAMP,

    -- Access control
    access_level VARCHAR(20) DEFAULT 'internal',
    allowed_roles JSONB,
    distribution_list JSONB,

    -- Notes
    change_summary TEXT,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create document_access_log table if not exists
CREATE TABLE IF NOT EXISTS document_access_log (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id INTEGER,
    user_name VARCHAR(100),
    access_type VARCHAR(20), -- view, download, print, edit
    access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent VARCHAR(200),
    notes TEXT
);

-- Create document_revisions table for full version history
CREATE TABLE IF NOT EXISTS document_revisions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    version VARCHAR(20) NOT NULL,
    change_type VARCHAR(50), -- major, minor, editorial
    change_description TEXT,
    file_path VARCHAR(200),
    file_hash VARCHAR(64),
    revised_by_id INTEGER,
    revised_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by_id INTEGER,
    approved_at TIMESTAMP,
    UNIQUE(document_id, revision_number)
);

-- Create document_approval_workflow table
CREATE TABLE IF NOT EXISTS document_approval_workflow (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    approver_role VARCHAR(50),
    approver_id INTEGER,
    required BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, skipped
    decision_date TIMESTAMP,
    comments TEXT,
    signature TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create document_distribution table
CREATE TABLE IF NOT EXISTS document_distribution (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    recipient_id INTEGER,
    recipient_email VARCHAR(100),
    distribution_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    distribution_method VARCHAR(50), -- email, print, portal
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    copy_number INTEGER,
    notes TEXT
);

-- Create document_templates table
CREATE TABLE IF NOT EXISTS document_templates (
    id SERIAL PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    template_content TEXT,
    placeholders JSONB,
    file_path VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_by_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_documents_number ON documents(document_number);
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_current ON documents(is_current_version);
CREATE INDEX IF NOT EXISTS idx_documents_department ON documents(department);
CREATE INDEX IF NOT EXISTS idx_documents_next_review ON documents(next_review_date);
CREATE INDEX IF NOT EXISTS idx_document_access_log_document ON document_access_log(document_id);
CREATE INDEX IF NOT EXISTS idx_document_access_log_user ON document_access_log(user_id);
CREATE INDEX IF NOT EXISTS idx_document_access_log_timestamp ON document_access_log(access_timestamp);
CREATE INDEX IF NOT EXISTS idx_document_revisions_document ON document_revisions(document_id);
CREATE INDEX IF NOT EXISTS idx_document_approval_workflow_document ON document_approval_workflow(document_id);
CREATE INDEX IF NOT EXISTS idx_document_distribution_document ON document_distribution(document_id);
CREATE INDEX IF NOT EXISTS idx_document_templates_code ON document_templates(template_code);

-- Create trigger to update documents timestamp
CREATE OR REPLACE FUNCTION update_documents_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS documents_update_timestamp ON documents;
CREATE TRIGGER documents_update_timestamp
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION update_documents_timestamp();

-- Create trigger to log document access
CREATE OR REPLACE FUNCTION log_document_access()
RETURNS TRIGGER AS $$
BEGIN
    -- This would be called from application code to log access
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMIT;
