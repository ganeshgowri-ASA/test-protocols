-- ===================================================================================
-- Migration 010: Add Missing Critical Columns
-- ===================================================================================
-- Purpose: Add all remaining missing columns that are causing page errors
-- Target: PostgreSQL (Railway deployment)
-- Author: Comet AI Assistant
-- Date: 2025-12-14
--
-- FIXES ERRORS:
-- 1. Training Management page error (users.password_hash missing)
-- 2. Sample Tracking Dashboard error (samples.status missing)
-- 3. Sample Allocation error (samples.status missing)
-- 4. Sample Registration error (incoming_inspections.receipt_id missing)
-- 5. Sample Receipt page error (sample_receipts date column naming issue)

-- ===== USERS TABLE: Add password_hash for authentication =====
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- ===== SAMPLES TABLE: Add status column for lifecycle tracking =====
ALTER TABLE samples
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'RECEIVED';

-- ===== INCOMING_INSPECTIONS TABLE: Add receipt_id foreign key =====
ALTER TABLE incoming_inspections
ADD COLUMN IF NOT EXISTS receipt_id INTEGER REFERENCES sample_receipts(id) ON DELETE SET NULL;

-- ===== SAMPLE_RECEIPTS TABLE: Fix date column naming issue =====
-- Check if old column exists and rename it, or create new one
DO $$
BEGIN
    -- Try to rename if column exists with wrong name
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='sample_receipts' AND column_name='received_date') THEN
        ALTER TABLE sample_receipts RENAME COLUMN received_date TO receipt_date;
    ELSE
        -- Create new column if it doesn't exist
        ALTER TABLE sample_receipts ADD COLUMN IF NOT EXISTS receipt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- ===== Create indexes for performance =====
CREATE INDEX IF NOT EXISTS idx_samples_status ON samples(status);
CREATE INDEX IF NOT EXISTS idx_inspections_receipt ON incoming_inspections(receipt_id);
CREATE INDEX IF NOT EXISTS idx_sample_receipts_date ON sample_receipts(receipt_date);

-- ===== Add comments for documentation =====
COMMENT ON COLUMN users.password_hash IS 'Hashed password for user authentication';
COMMENT ON COLUMN samples.status IS 'Sample lifecycle status: RECEIVED, INSPECTED, ALLOCATED, TESTING, COMPLETED, DISPOSED';
COMMENT ON COLUMN incoming_inspections.receipt_id IS 'Link to sample receipt record';
COMMENT ON COLUMN sample_receipts.receipt_date IS 'Timestamp when samples were received (renamed from received_date)';

-- Migration complete
-- All critical missing columns added - ready for QA testing
