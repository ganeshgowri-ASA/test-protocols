-- ===================================================================================
-- Migration 009: Add ISO 17025 Sample ID Structure
-- ===================================================================================
-- Purpose: Implement dual sample identification system per ISO 17025 requirements:
--          1. Manufacturer Sample ID (original from client/manufacturer)
--          2. Lab-assigned Unique Sample ID (MCIND-YYYY-NNNN format)
-- Target: PostgreSQL (Railway deployment)
-- Author: Comet AI Assistant
-- Date: 2025-12-14
--
-- FIXES ERRORS:
-- - Sample Tracking Dashboard errors
-- - Sample Allocation errors  
-- - Sample flow tracking from receipt to testing
--
-- ISO 17025 Requirement: Unique laboratory identification for sample traceability
-- Reference: ISO/IEC 17025:2017, Clause 7.2 - Sample Handling

-- ===== SAMPLES TABLE: Add dual ID tracking =====
ALTER TABLE samples 
ADD COLUMN IF NOT EXISTS manufacturer_sample_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS lab_sample_id VARCHAR(50) UNIQUE,
ADD COLUMN IF NOT EXISTS id_assigned_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS id_assigned_by INTEGER REFERENCES users(id);

-- ===== SERVICE_REQUESTS TABLE: Track manufacturer sample IDs from client =====
ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS manufacturer_sample_ids JSONB;

-- ===== INCOMING_INSPECTIONS TABLE: Track ID assignment point =====
ALTER TABLE incoming_inspections
ADD COLUMN IF NOT EXISTS manufacturer_sample_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS lab_sample_id VARCHAR(50);

-- ===== SAMPLE_RECEIPTS TABLE: Track received manufacturer IDs =====
ALTER TABLE sample_receipts
ADD COLUMN IF NOT EXISTS manufacturer_sample_ids JSONB;

-- ===== Create indexes for performance =====
CREATE INDEX IF NOT EXISTS idx_samples_lab_id ON samples(lab_sample_id);
CREATE INDEX IF NOT EXISTS idx_samples_mfr_id ON samples(manufacturer_sample_id);
CREATE INDEX IF NOT EXISTS idx_inspections_lab_id ON incoming_inspections(lab_sample_id);
CREATE INDEX IF NOT EXISTS idx_inspections_mfr_id ON incoming_inspections(manufacturer_sample_id);

-- ===== Add comments for documentation =====
COMMENT ON COLUMN samples.manufacturer_sample_id IS 'Original manufacturer/client serial number';
COMMENT ON COLUMN samples.lab_sample_id IS 'Lab-assigned unique ID per ISO 17025';
COMMENT ON COLUMN samples.id_assigned_at IS 'Timestamp when lab ID was assigned';
COMMENT ON COLUMN samples.id_assigned_by IS 'User who assigned the lab ID';

COMMENT ON COLUMN service_requests.manufacturer_sample_ids IS 'JSON array of manufacturer sample IDs';
COMMENT ON COLUMN sample_receipts.manufacturer_sample_ids IS 'JSON array of manufacturer IDs received';

COMMENT ON COLUMN incoming_inspections.manufacturer_sample_id IS 'Input: Manufacturer serial number';
COMMENT ON COLUMN incoming_inspections.lab_sample_id IS 'Output: Lab unique ID assigned after inspection';
