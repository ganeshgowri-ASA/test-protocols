-- ===================================================================================
-- Migration 008: Add Projects Table and Project Management Structure
-- ===================================================================================
-- Purpose: Add ISO 17025 compliant project management to track service requests,
--          samples, protocols, equipment, and resources under unified project IDs
-- Target: PostgreSQL (Railway deployment)
-- Author: Comet AI Assistant
-- Date: 2025-12-14
--
-- TABLES ADDED:
-- 1. projects: Main project management table
-- 2. project_resources: Link projects to equipment and resources
-- 3. project_milestones: Track project milestones and deliverables
--
-- COLUMNS ADDED TO EXISTING TABLES:
-- - service_requests.project_id
-- - samples.project_id
-- - sample_receipts.project_id
-- - incoming_inspections.project_id
-- - test_executions.project_id

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) UNIQUE NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    service_request_id INTEGER REFERENCES service_requests(id) ON DELETE SET NULL,
    project_manager_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'INITIATED',
    priority VARCHAR(20) DEFAULT 'NORMAL',
    start_date TIMESTAMP,
    target_completion_date TIMESTAMP,
    actual_completion_date TIMESTAMP,
    budget DECIMAL(12, 2),
    actual_cost DECIMAL(12, 2),
    completion_percentage INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create project_resources table (link projects to equipment/staff)
CREATE TABLE IF NOT EXISTS project_resources (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER NOT NULL,
    allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    release_date TIMESTAMP,
    utilization_hours DECIMAL(8, 2),
    notes TEXT
);

-- Create project_milestones table
CREATE TABLE IF NOT EXISTS project_milestones (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    milestone_name VARCHAR(255) NOT NULL,
    milestone_type VARCHAR(50),
    target_date TIMESTAMP,
    actual_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'PENDING',
    responsible_user_id INTEGER REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add project_id to existing tables
ALTER TABLE service_requests 
ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL;

ALTER TABLE samples 
ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL;

ALTER TABLE sample_receipts 
ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL;

ALTER TABLE incoming_inspections 
ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL;

ALTER TABLE test_executions 
ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_project_id ON projects(project_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_manager ON projects(project_manager_id);
CREATE INDEX IF NOT EXISTS idx_service_requests_project ON service_requests(project_id);
CREATE INDEX IF NOT EXISTS idx_samples_project ON samples(project_id);

-- Add comments
COMMENT ON TABLE projects IS 'Main project management table linking service requests to all project activities';
COMMENT ON COLUMN projects.project_id IS 'Unique lab-assigned project identifier: PROJECT-YYYY-NNNN';
COMMENT ON COLUMN projects.status IS 'Values: INITIATED, ACTIVE, ON_HOLD, COMPLETED, CLOSED, CANCELLED';

COMMENT ON TABLE project_resources IS 'Links projects to equipment, staff, and other resources';
COMMENT ON COLUMN project_resources.resource_type IS 'Values: EQUIPMENT, USER, FACILITY, MATERIAL';

COMMENT ON TABLE project_milestones IS 'Tracks project milestones and deliverables';
COMMENT ON COLUMN project_milestones.milestone_type IS 'Values: SAMPLE_RECEIPT, INSPECTION, TEST_START, TEST_END, REPORT_DRAFT, REPORT_FINAL, DELIVERY';

-- Migration complete
-- Next: Run Migration 009 to add ISO 17025 sample ID structure
