-- ============================================================================
-- Migration: 014_sample_specifications_column_DOWN.sql
-- Description: Rollback specifications column migration
-- Date: 2024
-- WARNING: This will remove the specifications column - use with caution!
-- ============================================================================

-- Remove specifications column
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'samples' AND column_name = 'specifications') THEN
        ALTER TABLE samples DROP COLUMN specifications;
    END IF;
END $$;

-- ============================================================================
-- END OF MIGRATION 014 ROLLBACK
-- ============================================================================
