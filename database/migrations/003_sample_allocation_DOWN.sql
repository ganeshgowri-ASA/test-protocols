-- ============================================================================
-- Migration: 003_sample_allocation_DOWN.sql
-- Description: Rollback sample_allocations table and allocation_status enum
-- Date: 2024-12-04
-- ============================================================================

-- Drop indexes
DROP INDEX IF EXISTS idx_allocations_created_at;
DROP INDEX IF EXISTS idx_allocations_schedule;
DROP INDEX IF EXISTS idx_allocations_status;
DROP INDEX IF EXISTS idx_allocations_technician;
DROP INDEX IF EXISTS idx_allocations_equipment;
DROP INDEX IF EXISTS idx_allocations_protocol;
DROP INDEX IF EXISTS idx_allocations_sample;

-- Drop table
DROP TABLE IF EXISTS sample_allocations;

-- Drop enum type
DROP TYPE IF EXISTS allocation_status;

-- ============================================================================
-- Rollback Complete
-- ============================================================================
