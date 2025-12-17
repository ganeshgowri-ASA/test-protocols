-- ====================================================================================
-- Migration: 004_add_missing_columns_UP.sql
-- Description: Add missing columns from PR #65 to ServiceRequest and IncomingInspection
-- Date: 2024-12-13
-- ====================================================================================

-- Add missing columns to service_requests table
ALTER TABLE service_requests ADD COLUMN IF NOT EXISTS expected_sample_quantity INTEGER DEFAULT 1;
ALTER TABLE service_requests ADD COLUMN IF NOT EXISTS actual_sample_quantity INTEGER;
ALTER TABLE service_requests ADD COLUMN IF NOT EXISTS quantity_verified BOOLEAN DEFAULT FALSE;

-- Add missing columns to incoming_inspections table 
ALTER TABLE incoming_inspections ADD COLUMN IF NOT EXISTS receipt_id VARCHAR REFERENCES service_requests(id);
ALTER TABLE incoming_inspections ADD COLUMN IF NOT EXISTS allocation_triggered BOOLEAN DEFAULT FALSE;
ALTER TABLE incoming_inspections ADD COLUMN IF NOT EXISTS allocated_sample_id VARCHAR;

-- Add missing column to users table for Report Generation
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR;

-- Success message
SELECT 'Migration 004 completed successfully' AS status;
