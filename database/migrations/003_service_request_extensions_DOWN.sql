-- ============================================================================
-- Migration: 003_service_request_extensions_DOWN.sql
-- Description: Rollback sample quantity fields from service_requests table
-- Date: 2024
-- ============================================================================

-- Drop index first
DROP INDEX IF EXISTS idx_service_requests_receipt_id;

-- Drop columns
ALTER TABLE service_requests DROP COLUMN IF EXISTS expected_sample_quantity;
ALTER TABLE service_requests DROP COLUMN IF EXISTS actual_sample_quantity;
ALTER TABLE service_requests DROP COLUMN IF EXISTS quantity_verified;
ALTER TABLE service_requests DROP COLUMN IF EXISTS receipt_id;

-- ============================================================================
-- END OF ROLLBACK
-- ============================================================================
