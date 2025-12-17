-- =================================================================
-- Migration 004: Test Protocols Enhancement - UP Migration
-- Description: Add protocol versioning and template fields
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Add versioning and template columns to test_protocols table
DO $$
BEGIN
    -- Add revision_number for tracking protocol revisions
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'revision_number') THEN
        ALTER TABLE test_protocols ADD COLUMN revision_number INTEGER DEFAULT 1;
    END IF;

    -- Add effective_date for when protocol becomes active
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'effective_date') THEN
        ALTER TABLE test_protocols ADD COLUMN effective_date TIMESTAMP;
    END IF;

    -- Add supersedes_id to link to previous version
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'supersedes_id') THEN
        ALTER TABLE test_protocols ADD COLUMN supersedes_id INTEGER REFERENCES test_protocols(id);
    END IF;

    -- Add template_content for storing full protocol template
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'template_content') THEN
        ALTER TABLE test_protocols ADD COLUMN template_content JSONB;
    END IF;

    -- Add form_definition for dynamic form generation
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'form_definition') THEN
        ALTER TABLE test_protocols ADD COLUMN form_definition JSONB;
    END IF;

    -- Add output_template for report output format
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'output_template') THEN
        ALTER TABLE test_protocols ADD COLUMN output_template JSONB;
    END IF;

    -- Add workflow_steps for multi-step protocols
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'workflow_steps') THEN
        ALTER TABLE test_protocols ADD COLUMN workflow_steps JSONB DEFAULT '[]';
    END IF;

    -- Add safety_requirements
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'safety_requirements') THEN
        ALTER TABLE test_protocols ADD COLUMN safety_requirements TEXT;
    END IF;

    -- Add environmental_conditions for test environment requirements
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'environmental_conditions') THEN
        ALTER TABLE test_protocols ADD COLUMN environmental_conditions JSONB;
    END IF;

    -- Add reviewer_id for protocol review
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'reviewer_id') THEN
        ALTER TABLE test_protocols ADD COLUMN reviewer_id INTEGER REFERENCES users(id);
    END IF;

    -- Add approver_id for protocol approval
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'approver_id') THEN
        ALTER TABLE test_protocols ADD COLUMN approver_id INTEGER REFERENCES users(id);
    END IF;

    -- Add review_date
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'review_date') THEN
        ALTER TABLE test_protocols ADD COLUMN review_date TIMESTAMP;
    END IF;

    -- Add approval_date
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'approval_date') THEN
        ALTER TABLE test_protocols ADD COLUMN approval_date TIMESTAMP;
    END IF;

    -- Add next_review_date for periodic review
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'next_review_date') THEN
        ALTER TABLE test_protocols ADD COLUMN next_review_date TIMESTAMP;
    END IF;

    -- Add status for protocol lifecycle
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'status') THEN
        ALTER TABLE test_protocols ADD COLUMN status VARCHAR(20) DEFAULT 'active';
    END IF;

    -- Add tags for categorization
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'test_protocols' AND column_name = 'tags') THEN
        ALTER TABLE test_protocols ADD COLUMN tags JSONB DEFAULT '[]';
    END IF;
END $$;

-- Create protocol_versions table for version history
CREATE TABLE IF NOT EXISTS protocol_versions (
    id SERIAL PRIMARY KEY,
    protocol_id INTEGER NOT NULL REFERENCES test_protocols(id) ON DELETE CASCADE,
    version_number VARCHAR(20) NOT NULL,
    revision_number INTEGER NOT NULL,
    change_summary TEXT,
    template_snapshot JSONB,
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(protocol_id, version_number, revision_number)
);

-- Create protocol_attachments table
CREATE TABLE IF NOT EXISTS protocol_attachments (
    id SERIAL PRIMARY KEY,
    protocol_id INTEGER NOT NULL REFERENCES test_protocols(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size INTEGER,
    description TEXT,
    uploaded_by_id INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_test_protocols_supersedes ON test_protocols(supersedes_id);
CREATE INDEX IF NOT EXISTS idx_test_protocols_status ON test_protocols(status);
CREATE INDEX IF NOT EXISTS idx_test_protocols_effective ON test_protocols(effective_date);
CREATE INDEX IF NOT EXISTS idx_test_protocols_next_review ON test_protocols(next_review_date);
CREATE INDEX IF NOT EXISTS idx_protocol_versions_protocol ON protocol_versions(protocol_id);
CREATE INDEX IF NOT EXISTS idx_protocol_attachments_protocol ON protocol_attachments(protocol_id);

COMMIT;
