-- ============================================================================
-- Migration: 013_sample_traceability_fields_DOWN.sql
-- Description: Rollback traceability fields migration
-- Date: 2024
-- WARNING: This will remove traceability columns - use with caution!
-- ============================================================================

-- ============================================================================
-- REMOVE COLUMNS FROM SAMPLES TABLE
-- ============================================================================

-- Remove receipt_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'samples' AND column_name = 'receipt_id') THEN
        ALTER TABLE samples DROP COLUMN receipt_id;
    END IF;
END $$;

-- Remove inspection_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'samples' AND column_name = 'inspection_id') THEN
        ALTER TABLE samples DROP COLUMN inspection_id;
    END IF;
END $$;

-- Remove batch_number
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'samples' AND column_name = 'batch_number') THEN
        ALTER TABLE samples DROP COLUMN batch_number;
    END IF;
END $$;

-- Remove custody_history
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'samples' AND column_name = 'custody_history') THEN
        ALTER TABLE samples DROP COLUMN custody_history;
    END IF;
END $$;

-- ============================================================================
-- REMOVE COLUMNS FROM INCOMING_INSPECTIONS TABLE
-- ============================================================================

-- Remove receipt_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'incoming_inspections' AND column_name = 'receipt_id') THEN
        ALTER TABLE incoming_inspections DROP COLUMN receipt_id;
    END IF;
END $$;

-- Remove allocation_triggered
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'incoming_inspections' AND column_name = 'allocation_triggered') THEN
        ALTER TABLE incoming_inspections DROP COLUMN allocation_triggered;
    END IF;
END $$;

-- Remove allocated_sample_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'incoming_inspections' AND column_name = 'allocated_sample_id') THEN
        ALTER TABLE incoming_inspections DROP COLUMN allocated_sample_id;
    END IF;
END $$;

-- ============================================================================
-- REMOVE COLUMNS FROM SERVICE_REQUESTS TABLE
-- ============================================================================

-- Remove expected_sample_quantity
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'service_requests' AND column_name = 'expected_sample_quantity') THEN
        ALTER TABLE service_requests DROP COLUMN expected_sample_quantity;
    END IF;
END $$;

-- Remove actual_sample_quantity
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'service_requests' AND column_name = 'actual_sample_quantity') THEN
        ALTER TABLE service_requests DROP COLUMN actual_sample_quantity;
    END IF;
END $$;

-- Remove quantity_verified
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'service_requests' AND column_name = 'quantity_verified') THEN
        ALTER TABLE service_requests DROP COLUMN quantity_verified;
    END IF;
END $$;

-- Remove receipt_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'service_requests' AND column_name = 'receipt_id') THEN
        ALTER TABLE service_requests DROP COLUMN receipt_id;
    END IF;
END $$;

-- ============================================================================
-- NOTE: We do NOT drop sample_receipts table in rollback
-- as it may contain critical data. Manual cleanup required if needed.
-- ============================================================================

-- ============================================================================
-- END OF MIGRATION 013 ROLLBACK
-- ============================================================================
