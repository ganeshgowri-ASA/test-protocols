-- ============================================================================
-- Migration: 002_sample_management_DOWN.sql
-- Description: Rollback Sample Management & Tracking System tables
-- Date: 2024
-- ============================================================================

-- Drop tables in reverse dependency order

-- Drop access logs first
DROP TABLE IF EXISTS document_access_log;
DROP TABLE IF EXISTS qr_scan_log;
DROP TABLE IF EXISTS bom_usage_log;

-- Drop junction/relationship tables
DROP TABLE IF EXISTS bom_protocol_requirements;
DROP TABLE IF EXISTS staff_training_records;

-- Drop main tables
DROP TABLE IF EXISTS calibration_records;
DROP TABLE IF EXISTS bom_items;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS staff_training;
DROP TABLE IF EXISTS sample_inventory;
DROP TABLE IF EXISTS sample_test_assignments;
DROP TABLE IF EXISTS route_cards;
DROP TABLE IF EXISTS sample_status_history;
DROP TABLE IF EXISTS samples;
DROP TABLE IF EXISTS sample_receipts;

-- Remove columns from existing tables
ALTER TABLE service_requests DROP COLUMN IF EXISTS expected_sample_quantity;
ALTER TABLE service_requests DROP COLUMN IF EXISTS actual_sample_quantity;
ALTER TABLE service_requests DROP COLUMN IF EXISTS quantity_verified;
ALTER TABLE service_requests DROP COLUMN IF EXISTS receipt_id;

ALTER TABLE incoming_inspections DROP COLUMN IF EXISTS receipt_id;
ALTER TABLE incoming_inspections DROP COLUMN IF EXISTS allocation_triggered;
ALTER TABLE incoming_inspections DROP COLUMN IF EXISTS allocated_sample_id;

-- Drop enum types (PostgreSQL only)
DROP TYPE IF EXISTS sample_status;
DROP TYPE IF EXISTS document_category;
DROP TYPE IF EXISTS training_status;
DROP TYPE IF EXISTS bom_item_type;

-- ============================================================================
-- END OF ROLLBACK
-- ============================================================================
