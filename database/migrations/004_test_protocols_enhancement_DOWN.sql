-- =================================================================
-- Migration 004: Test Protocols Enhancement - DOWN Migration
-- Description: Rollback protocol versioning and template fields
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop indexes
DROP INDEX IF EXISTS idx_protocol_attachments_protocol;
DROP INDEX IF EXISTS idx_protocol_versions_protocol;
DROP INDEX IF EXISTS idx_test_protocols_next_review;
DROP INDEX IF EXISTS idx_test_protocols_effective;
DROP INDEX IF EXISTS idx_test_protocols_status;
DROP INDEX IF EXISTS idx_test_protocols_supersedes;

-- Drop tables
DROP TABLE IF EXISTS protocol_attachments CASCADE;
DROP TABLE IF EXISTS protocol_versions CASCADE;

-- Remove columns from test_protocols table
ALTER TABLE test_protocols DROP COLUMN IF EXISTS tags;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS status;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS next_review_date;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS approval_date;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS review_date;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS approver_id;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS reviewer_id;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS environmental_conditions;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS safety_requirements;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS workflow_steps;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS output_template;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS form_definition;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS template_content;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS supersedes_id;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS effective_date;
ALTER TABLE test_protocols DROP COLUMN IF EXISTS revision_number;

COMMIT;
