-- ============================================================================
-- Migration: 012_samples_all_columns_UP.sql
-- Description: Comprehensive migration to add ALL missing columns to samples table
-- Date: 2024
-- Purpose: Fix "column samples.project_id does not exist" and related errors
-- ============================================================================

-- ============================================================================
-- SAMPLES TABLE COLUMN ADDITIONS
-- These are idempotent - safe to run multiple times
-- ============================================================================

-- Core identification columns
ALTER TABLE samples ADD COLUMN IF NOT EXISTS sample_id VARCHAR(50);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS project_id VARCHAR(50);

-- Foreign key relationships
ALTER TABLE samples ADD COLUMN IF NOT EXISTS service_request_id INTEGER;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS receipt_id INTEGER;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS inspection_id INTEGER;

-- Sample details
ALTER TABLE samples ADD COLUMN IF NOT EXISTS sample_type VARCHAR(50);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(100);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS model_number VARCHAR(100);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS serial_number VARCHAR(100);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS batch_number VARCHAR(100);

-- Physical properties
ALTER TABLE samples ADD COLUMN IF NOT EXISTS length_mm FLOAT;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS width_mm FLOAT;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS thickness_mm FLOAT;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS weight_kg FLOAT;

-- QR Code fields
ALTER TABLE samples ADD COLUMN IF NOT EXISTS qr_code VARCHAR(200);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS qr_code_image_path VARCHAR(200);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS qr_data JSON;

-- Status and location tracking
ALTER TABLE samples ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'received';
ALTER TABLE samples ADD COLUMN IF NOT EXISTS current_location VARCHAR(100);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS storage_location VARCHAR(100);

-- Allocation tracking
ALTER TABLE samples ADD COLUMN IF NOT EXISTS allocation_date TIMESTAMP;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS allocated_by_id INTEGER;

-- Test assignment tracking
ALTER TABLE samples ADD COLUMN IF NOT EXISTS assigned_protocol_ids JSON;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS current_test_id INTEGER;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS tests_completed INTEGER DEFAULT 0;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS tests_total INTEGER DEFAULT 0;

-- Results summary
ALTER TABLE samples ADD COLUMN IF NOT EXISTS overall_result VARCHAR(20);
ALTER TABLE samples ADD COLUMN IF NOT EXISTS result_summary TEXT;

-- Metadata
ALTER TABLE samples ADD COLUMN IF NOT EXISTS specifications JSON;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS photos JSON;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS custody_history JSON;

-- Timestamps
ALTER TABLE samples ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;
ALTER TABLE samples ADD COLUMN IF NOT EXISTS disposed_at TIMESTAMP;

-- ============================================================================
-- CREATE INDEXES FOR BETTER PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_samples_sample_id ON samples(sample_id);
CREATE INDEX IF NOT EXISTS idx_samples_project_id ON samples(project_id);
CREATE INDEX IF NOT EXISTS idx_samples_service_request ON samples(service_request_id);
CREATE INDEX IF NOT EXISTS idx_samples_status ON samples(status);
CREATE INDEX IF NOT EXISTS idx_samples_qr_code ON samples(qr_code);
CREATE INDEX IF NOT EXISTS idx_samples_current_location ON samples(current_location);
CREATE INDEX IF NOT EXISTS idx_samples_allocation_date ON samples(allocation_date);
CREATE INDEX IF NOT EXISTS idx_samples_created_at ON samples(created_at);

-- ============================================================================
-- ADD UNIQUE CONSTRAINTS IF NOT EXISTS
-- Note: These may fail if duplicates exist - handle in application
-- ============================================================================

-- Make sample_id unique (skip if already exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'samples_sample_id_key'
    ) THEN
        ALTER TABLE samples ADD CONSTRAINT samples_sample_id_key UNIQUE (sample_id);
    END IF;
EXCEPTION WHEN duplicate_table THEN
    -- Constraint already exists, ignore
    NULL;
END $$;

-- Make qr_code unique (skip if already exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'samples_qr_code_key'
    ) THEN
        ALTER TABLE samples ADD CONSTRAINT samples_qr_code_key UNIQUE (qr_code);
    END IF;
EXCEPTION WHEN duplicate_table THEN
    -- Constraint already exists, ignore
    NULL;
END $$;

-- ============================================================================
-- ADD FOREIGN KEY CONSTRAINTS IF NOT EXISTS
-- ============================================================================

-- Foreign key to service_requests
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_samples_service_request'
        AND table_name = 'samples'
    ) THEN
        ALTER TABLE samples
        ADD CONSTRAINT fk_samples_service_request
        FOREIGN KEY (service_request_id) REFERENCES service_requests(id);
    END IF;
EXCEPTION WHEN others THEN
    -- Constraint creation failed, possibly due to data integrity issues
    RAISE NOTICE 'Could not create FK fk_samples_service_request: %', SQLERRM;
END $$;

-- Foreign key to sample_receipts
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_samples_receipt'
        AND table_name = 'samples'
    ) THEN
        ALTER TABLE samples
        ADD CONSTRAINT fk_samples_receipt
        FOREIGN KEY (receipt_id) REFERENCES sample_receipts(id);
    END IF;
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not create FK fk_samples_receipt: %', SQLERRM;
END $$;

-- Foreign key to incoming_inspections
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_samples_inspection'
        AND table_name = 'samples'
    ) THEN
        ALTER TABLE samples
        ADD CONSTRAINT fk_samples_inspection
        FOREIGN KEY (inspection_id) REFERENCES incoming_inspections(id);
    END IF;
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not create FK fk_samples_inspection: %', SQLERRM;
END $$;

-- Foreign key to users (allocated_by)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_samples_allocated_by'
        AND table_name = 'samples'
    ) THEN
        ALTER TABLE samples
        ADD CONSTRAINT fk_samples_allocated_by
        FOREIGN KEY (allocated_by_id) REFERENCES users(id);
    END IF;
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not create FK fk_samples_allocated_by: %', SQLERRM;
END $$;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
