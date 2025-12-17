-- =================================================================
-- Migration 007: Document Management - DOWN Migration
-- Description: Rollback document versioning and approval workflow
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop triggers and functions
DROP TRIGGER IF EXISTS documents_update_timestamp ON documents;
DROP FUNCTION IF EXISTS update_documents_timestamp() CASCADE;
DROP FUNCTION IF EXISTS log_document_access() CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_document_templates_code;
DROP INDEX IF EXISTS idx_document_distribution_document;
DROP INDEX IF EXISTS idx_document_approval_workflow_document;
DROP INDEX IF EXISTS idx_document_revisions_document;
DROP INDEX IF EXISTS idx_document_access_log_timestamp;
DROP INDEX IF EXISTS idx_document_access_log_user;
DROP INDEX IF EXISTS idx_document_access_log_document;
DROP INDEX IF EXISTS idx_documents_next_review;
DROP INDEX IF EXISTS idx_documents_department;
DROP INDEX IF EXISTS idx_documents_current;
DROP INDEX IF EXISTS idx_documents_status;
DROP INDEX IF EXISTS idx_documents_category;
DROP INDEX IF EXISTS idx_documents_number;

-- Drop tables
DROP TABLE IF EXISTS document_templates CASCADE;
DROP TABLE IF EXISTS document_distribution CASCADE;
DROP TABLE IF EXISTS document_approval_workflow CASCADE;
DROP TABLE IF EXISTS document_revisions CASCADE;
DROP TABLE IF EXISTS document_access_log CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

COMMIT;
