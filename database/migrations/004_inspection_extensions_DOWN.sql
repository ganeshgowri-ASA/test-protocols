-- ============================================================================
-- Migration: 004_inspection_extensions_DOWN.sql
-- Description: Rollback allocation tracking from incoming_inspections table
-- Date: 2024
-- ============================================================================

-- Drop indexes first
DROP INDEX IF EXISTS idx_incoming_inspections_receipt_id;
DROP INDEX IF EXISTS idx_incoming_inspections_allocation;

-- Drop columns
ALTER TABLE incoming_inspections DROP COLUMN IF EXISTS receipt_id;
ALTER TABLE incoming_inspections DROP COLUMN IF EXISTS allocation_triggered;
ALTER TABLE incoming_inspections DROP COLUMN IF EXISTS allocated_sample_id;

-- ============================================================================
-- END OF ROLLBACK
-- ============================================================================
