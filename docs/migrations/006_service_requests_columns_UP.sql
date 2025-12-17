-- ============================================================================
-- Migration 006: Add Missing Service Requests Columns
-- ============================================================================
-- Purpose: Add columns needed for Sample Receipt workflow integration
-- Target: PostgreSQL (Railway deployment)
-- Author: Comet AI Assistant  
-- Date: 2025-01-09
--
-- COLUMNS ADDED:
-- 1. service_requests.expected_sample_quantity
-- 2. service_requests.actual_sample_quantity
-- 3. service_requests.quantity_verified
-- 4. service_requests.receipt_id
-- ============================================================================

DO $$
BEGIN
    -- Add expected_sample_quantity column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'service_requests' AND column_name = 'expected_sample_quantity'
    ) THEN
        ALTER TABLE service_requests ADD COLUMN expected_sample_quantity INTEGER;
        RAISE NOTICE 'Added column: service_requests.expected_sample_quantity';
    END IF;

    -- Add actual_sample_quantity column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'service_requests' AND column_name = 'actual_sample_quantity'
    ) THEN
        ALTER TABLE service_requests ADD COLUMN actual_sample_quantity INTEGER;
        RAISE NOTICE 'Added column: service_requests.actual_sample_quantity';
    END IF;

    -- Add quantity_verified column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'service_requests' AND column_name = 'quantity_verified'
    ) THEN
        ALTER TABLE service_requests ADD COLUMN quantity_verified BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column: service_requests.quantity_verified';
    END IF;

    -- Add receipt_id column if not exists (foreign key to sample_receipts table)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'service_requests' AND column_name = 'receipt_id'
    ) THEN
        ALTER TABLE service_requests ADD COLUMN receipt_id INTEGER;
        RAISE NOTICE 'Added column: service_requests.receipt_id';
    END IF;
END $$;

-- ============================================================================
-- Create index for receipt_id for faster lookups
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_service_requests_receipt_id ON service_requests(receipt_id);
