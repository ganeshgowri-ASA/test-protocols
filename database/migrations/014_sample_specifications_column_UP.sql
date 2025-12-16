-- ============================================================================
-- Migration: 014_sample_specifications_column_UP.sql
-- Description: Add missing specifications column to samples table
-- Date: 2024
-- Purpose: Enable sample specification tracking for Sample Allocation page
-- ============================================================================

-- Add specifications column if it doesn't exist (JSON type for flexible spec data)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'samples' AND column_name = 'specifications') THEN
        ALTER TABLE samples ADD COLUMN specifications JSON;
    END IF;
END $$;

-- ============================================================================
-- END OF MIGRATION 014
-- ============================================================================
