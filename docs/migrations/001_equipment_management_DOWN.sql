-- ============================================================================
-- PHASE 1: EQUIPMENT MANAGEMENT - DOWN MIGRATION (ROLLBACK)
-- File: migrations/001_equipment_management_DOWN.sql
-- Description: Rollback equipment management changes
-- Author: Claude Opus 4.5 (Perplexity)
-- Date: 2025-12-01
-- WARNING: This will delete all equipment and calibration data!
-- ============================================================================

-- Verify tables exist before attempting to drop
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'equipment_calibration') THEN
        RAISE NOTICE '⚠️  Found equipment_calibration table - proceeding with DROP';
    ELSE
        RAISE NOTICE 'ℹ️  equipment_calibration table not found - skipping';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'equipment') THEN
        RAISE NOTICE '⚠️  Found equipment table - proceeding with DROP';
    ELSE
        RAISE NOTICE 'ℹ️  equipment table not found - skipping';
    END IF;
END $$;

-- Drop tables (cascade will automatically drop dependent objects)
DROP TABLE IF EXISTS equipment_calibration CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;

-- Drop trigger (if it exists)
DROP TRIGGER IF EXISTS set_equipment_updated_at ON equipment;

-- Drop trigger function
DROP FUNCTION IF EXISTS update_equipment_updated_at() CASCADE;

-- Drop indexes (automatically dropped with tables, but being explicit)
-- DROP INDEX IF EXISTS idx_equipment_code;
-- DROP INDEX IF EXISTS idx_equipment_status;
-- DROP INDEX IF EXISTS idx_equipment_next_cal_date;
-- DROP INDEX IF EXISTS idx_equipment_calibration_equip_id;

-- Rollback completion message
DO $$
BEGIN
    RAISE NOTICE '✅ Rollback completed successfully';
    RAISE NOTICE '✅ Removed tables: equipment, equipment_calibration';
    RAISE NOTICE '✅ System restored to pre-Phase 1 state';
END $$;