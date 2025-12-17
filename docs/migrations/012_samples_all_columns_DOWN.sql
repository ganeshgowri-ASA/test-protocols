-- ============================================================================
-- Migration: 012_samples_all_columns_DOWN.sql
-- Description: Rollback comprehensive samples table columns
-- Date: 2024
-- WARNING: This will DROP columns and their data permanently!
-- ============================================================================

-- ============================================================================
-- DROP FOREIGN KEY CONSTRAINTS
-- ============================================================================

ALTER TABLE samples DROP CONSTRAINT IF EXISTS fk_samples_service_request;
ALTER TABLE samples DROP CONSTRAINT IF EXISTS fk_samples_receipt;
ALTER TABLE samples DROP CONSTRAINT IF EXISTS fk_samples_inspection;
ALTER TABLE samples DROP CONSTRAINT IF EXISTS fk_samples_allocated_by;

-- ============================================================================
-- DROP UNIQUE CONSTRAINTS
-- ============================================================================

ALTER TABLE samples DROP CONSTRAINT IF EXISTS samples_sample_id_key;
ALTER TABLE samples DROP CONSTRAINT IF EXISTS samples_qr_code_key;

-- ============================================================================
-- DROP INDEXES
-- ============================================================================

DROP INDEX IF EXISTS idx_samples_sample_id;
DROP INDEX IF EXISTS idx_samples_project_id;
DROP INDEX IF EXISTS idx_samples_service_request;
DROP INDEX IF EXISTS idx_samples_status;
DROP INDEX IF EXISTS idx_samples_qr_code;
DROP INDEX IF EXISTS idx_samples_current_location;
DROP INDEX IF EXISTS idx_samples_allocation_date;
DROP INDEX IF EXISTS idx_samples_created_at;

-- ============================================================================
-- DROP COLUMNS
-- Note: Be very careful with this - it deletes data permanently!
-- ============================================================================

-- Core identification columns
ALTER TABLE samples DROP COLUMN IF EXISTS sample_id;
ALTER TABLE samples DROP COLUMN IF EXISTS project_id;

-- Foreign key relationships
ALTER TABLE samples DROP COLUMN IF EXISTS service_request_id;
ALTER TABLE samples DROP COLUMN IF EXISTS receipt_id;
ALTER TABLE samples DROP COLUMN IF EXISTS inspection_id;

-- Sample details
ALTER TABLE samples DROP COLUMN IF EXISTS sample_type;
ALTER TABLE samples DROP COLUMN IF EXISTS manufacturer;
ALTER TABLE samples DROP COLUMN IF EXISTS model_number;
ALTER TABLE samples DROP COLUMN IF EXISTS serial_number;
ALTER TABLE samples DROP COLUMN IF EXISTS batch_number;

-- Physical properties
ALTER TABLE samples DROP COLUMN IF EXISTS length_mm;
ALTER TABLE samples DROP COLUMN IF EXISTS width_mm;
ALTER TABLE samples DROP COLUMN IF EXISTS thickness_mm;
ALTER TABLE samples DROP COLUMN IF EXISTS weight_kg;

-- QR Code fields
ALTER TABLE samples DROP COLUMN IF EXISTS qr_code;
ALTER TABLE samples DROP COLUMN IF EXISTS qr_code_image_path;
ALTER TABLE samples DROP COLUMN IF EXISTS qr_data;

-- Status and location tracking
ALTER TABLE samples DROP COLUMN IF EXISTS status;
ALTER TABLE samples DROP COLUMN IF EXISTS current_location;
ALTER TABLE samples DROP COLUMN IF EXISTS storage_location;

-- Allocation tracking
ALTER TABLE samples DROP COLUMN IF EXISTS allocation_date;
ALTER TABLE samples DROP COLUMN IF EXISTS allocated_by_id;

-- Test assignment tracking
ALTER TABLE samples DROP COLUMN IF EXISTS assigned_protocol_ids;
ALTER TABLE samples DROP COLUMN IF EXISTS current_test_id;
ALTER TABLE samples DROP COLUMN IF EXISTS tests_completed;
ALTER TABLE samples DROP COLUMN IF EXISTS tests_total;

-- Results summary
ALTER TABLE samples DROP COLUMN IF EXISTS overall_result;
ALTER TABLE samples DROP COLUMN IF EXISTS result_summary;

-- Metadata
ALTER TABLE samples DROP COLUMN IF EXISTS specifications;
ALTER TABLE samples DROP COLUMN IF EXISTS notes;
ALTER TABLE samples DROP COLUMN IF EXISTS photos;
ALTER TABLE samples DROP COLUMN IF EXISTS custody_history;

-- Timestamps
ALTER TABLE samples DROP COLUMN IF EXISTS created_at;
ALTER TABLE samples DROP COLUMN IF EXISTS updated_at;
ALTER TABLE samples DROP COLUMN IF EXISTS completed_at;
ALTER TABLE samples DROP COLUMN IF EXISTS disposed_at;

-- ============================================================================
-- END OF ROLLBACK
-- ============================================================================
