-- ============================================================================
-- Migration: 013_sample_traceability_fields_DOWN.sql
-- Description: Rollback sample traceability fields
-- Date: 2024
-- WARNING: This will remove traceability data - use with caution!
-- ============================================================================

-- ============================================================================
-- DROP FOREIGN KEY CONSTRAINTS
-- ============================================================================

-- Drop FK: incoming_inspections.receipt_id
ALTER TABLE incoming_inspections
DROP CONSTRAINT IF EXISTS fk_incoming_inspections_receipt;

-- Drop FK: samples.inspection_id
ALTER TABLE samples
DROP CONSTRAINT IF EXISTS fk_samples_inspection;

-- ============================================================================
-- DROP INDEXES
-- ============================================================================

-- Drop GIN indexes for JSONB columns
DROP INDEX IF EXISTS idx_samples_custody_history;
DROP INDEX IF EXISTS idx_samples_specifications;

-- Drop FK lookup indexes
DROP INDEX IF EXISTS idx_samples_inspection_id;
DROP INDEX IF EXISTS idx_incoming_inspections_receipt_id;

-- ============================================================================
-- DROP COLUMNS
-- Note: Only drop if you're sure the data is not needed
-- ============================================================================

-- Drop from samples table
ALTER TABLE samples DROP COLUMN IF EXISTS custody_history;
ALTER TABLE samples DROP COLUMN IF EXISTS specifications;
ALTER TABLE samples DROP COLUMN IF EXISTS inspection_id;

-- Drop from incoming_inspections table
ALTER TABLE incoming_inspections DROP COLUMN IF EXISTS receipt_id;

-- ============================================================================
-- END OF ROLLBACK
-- ============================================================================
