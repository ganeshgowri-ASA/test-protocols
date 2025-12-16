-- ============================================================================
-- Migration: 003_service_request_extensions_UP.sql
-- Description: Add sample quantity fields to service_requests table
-- Date: 2024
-- ============================================================================

-- Add expected_sample_quantity column
ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS expected_sample_quantity INTEGER DEFAULT 1;

-- Add actual_sample_quantity column
ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS actual_sample_quantity INTEGER;

-- Add quantity_verified column
ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS quantity_verified BOOLEAN DEFAULT FALSE;

-- Add receipt_id foreign key column
ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS receipt_id INTEGER REFERENCES sample_receipts(id);

-- Create index on receipt_id for better query performance
CREATE INDEX IF NOT EXISTS idx_service_requests_receipt_id ON service_requests(receipt_id);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
