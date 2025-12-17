-- =================================================================
-- Migration 010: QR Code Scanning - DOWN Migration
-- Description: Rollback QR scan logging and tracking
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop triggers and functions
DROP TRIGGER IF EXISTS qr_scan_log_update_stats ON qr_scan_log;
DROP FUNCTION IF EXISTS update_qr_code_scan_stats() CASCADE;
DROP FUNCTION IF EXISTS get_next_qr_sequence(VARCHAR) CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_qr_scan_workflows_code;
DROP INDEX IF EXISTS idx_qr_scan_actions_entity;
DROP INDEX IF EXISTS idx_qr_scan_actions_code;
DROP INDEX IF EXISTS idx_qr_batch_generation_status;
DROP INDEX IF EXISTS idx_qr_batch_generation_batch;
DROP INDEX IF EXISTS idx_qr_code_templates_entity;
DROP INDEX IF EXISTS idx_qr_code_templates_code;
DROP INDEX IF EXISTS idx_qr_scan_log_user;
DROP INDEX IF EXISTS idx_qr_scan_log_action;
DROP INDEX IF EXISTS idx_qr_scan_log_timestamp;
DROP INDEX IF EXISTS idx_qr_scan_log_entity;
DROP INDEX IF EXISTS idx_qr_scan_log_qr_code;
DROP INDEX IF EXISTS idx_qr_codes_active;
DROP INDEX IF EXISTS idx_qr_codes_entity;
DROP INDEX IF EXISTS idx_qr_codes_code;

-- Drop tables
DROP TABLE IF EXISTS qr_scan_workflows CASCADE;
DROP TABLE IF EXISTS qr_scan_actions CASCADE;
DROP TABLE IF EXISTS qr_batch_generation CASCADE;
DROP TABLE IF EXISTS qr_code_templates CASCADE;
DROP TABLE IF EXISTS qr_scan_log CASCADE;
DROP TABLE IF EXISTS qr_codes CASCADE;

COMMIT;
