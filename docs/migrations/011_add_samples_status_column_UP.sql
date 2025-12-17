-- =====================================================
-- Migration: 011_add_samples_status_column_UP.sql
-- Description: Add missing status column to samples table
-- Date: 2024
-- =====================================================

-- Add status column to samples table if it doesn't exist
-- Status values: received, inspected, allocated, assigned, in_test, completed, analyzed, reported, rejected, on_hold
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'samples' AND column_name = 'status'
  ) THEN
    ALTER TABLE samples ADD COLUMN status VARCHAR(20) DEFAULT 'received';
    
    -- Create index for status column for faster queries
    CREATE INDEX IF NOT EXISTS idx_samples_status ON samples(status);
    
    RAISE NOTICE 'Added status column to samples table';
  ELSE
    RAISE NOTICE 'status column already exists in samples table';
  END IF;
END $$;
