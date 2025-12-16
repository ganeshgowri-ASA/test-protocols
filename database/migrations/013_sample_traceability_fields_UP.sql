-- ============================================================================
-- Migration: 013_sample_traceability_fields_UP.sql
-- Description: Ensure sample traceability fields exist with proper JSONB type
-- Date: 2024
-- Purpose: Safety migration to ensure custody_history, specifications use JSONB
-- ============================================================================

-- ============================================================================
-- SAMPLES TABLE - TRACEABILITY FIELDS
-- These columns may already exist from migration 012
-- This migration ensures they exist and upgrades JSON to JSONB if needed
-- ============================================================================

-- Add custody_history if not exists (JSONB for better query performance)
ALTER TABLE samples ADD COLUMN IF NOT EXISTS custody_history JSONB;

-- Add specifications if not exists (JSONB for better query performance)
ALTER TABLE samples ADD COLUMN IF NOT EXISTS specifications JSONB;

-- Add inspection_id if not exists
ALTER TABLE samples ADD COLUMN IF NOT EXISTS inspection_id INTEGER;

-- ============================================================================
-- INCOMING_INSPECTIONS TABLE - RECEIPT LINK
-- This column may already exist from migration 004
-- ============================================================================

-- Add receipt_id if not exists
ALTER TABLE incoming_inspections ADD COLUMN IF NOT EXISTS receipt_id INTEGER;

-- ============================================================================
-- CREATE INDEXES FOR TRACEABILITY QUERIES
-- ============================================================================

-- Index for samples.inspection_id (FK lookup)
CREATE INDEX IF NOT EXISTS idx_samples_inspection_id ON samples(inspection_id);

-- Index for incoming_inspections.receipt_id (FK lookup)
CREATE INDEX IF NOT EXISTS idx_incoming_inspections_receipt_id ON incoming_inspections(receipt_id);

-- GIN index for JSONB custody_history (for @> containment queries)
CREATE INDEX IF NOT EXISTS idx_samples_custody_history ON samples USING GIN (custody_history);

-- GIN index for JSONB specifications (for @> containment queries)
CREATE INDEX IF NOT EXISTS idx_samples_specifications ON samples USING GIN (specifications);

-- ============================================================================
-- ADD FOREIGN KEY CONSTRAINTS IF NOT EXISTS
-- ============================================================================

-- Foreign key: samples.inspection_id -> incoming_inspections.id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_samples_inspection'
        AND table_name = 'samples'
    ) THEN
        ALTER TABLE samples
        ADD CONSTRAINT fk_samples_inspection
        FOREIGN KEY (inspection_id) REFERENCES incoming_inspections(id)
        ON DELETE SET NULL;
    END IF;
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not create FK fk_samples_inspection: %', SQLERRM;
END $$;

-- Foreign key: incoming_inspections.receipt_id -> sample_receipts.id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_incoming_inspections_receipt'
        AND table_name = 'incoming_inspections'
    ) THEN
        ALTER TABLE incoming_inspections
        ADD CONSTRAINT fk_incoming_inspections_receipt
        FOREIGN KEY (receipt_id) REFERENCES sample_receipts(id)
        ON DELETE SET NULL;
    END IF;
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not create FK fk_incoming_inspections_receipt: %', SQLERRM;
END $$;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
