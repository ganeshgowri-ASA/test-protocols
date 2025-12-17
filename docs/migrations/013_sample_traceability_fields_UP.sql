-- ============================================================================
-- Migration: 013_sample_traceability_fields_UP.sql
-- Description: Add missing traceability fields to samples and related tables
-- Date: 2024
-- Purpose: Ensure sample traceability chain is complete
-- ============================================================================

-- ============================================================================
-- ADD MISSING COLUMNS TO SAMPLES TABLE
-- These columns enable full traceability from receipt to completion
-- ============================================================================

-- Add receipt_id if it doesn't exist (links sample to its receipt record)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'samples' AND column_name = 'receipt_id') THEN
        ALTER TABLE samples ADD COLUMN receipt_id INTEGER REFERENCES sample_receipts(id);
        CREATE INDEX IF NOT EXISTS idx_samples_receipt_id ON samples(receipt_id);
    END IF;
END $$;

-- Add inspection_id if it doesn't exist (links sample to its inspection record)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'samples' AND column_name = 'inspection_id') THEN
        ALTER TABLE samples ADD COLUMN inspection_id INTEGER REFERENCES incoming_inspections(id);
        CREATE INDEX IF NOT EXISTS idx_samples_inspection_id ON samples(inspection_id);
    END IF;
END $$;

-- Add batch_number if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'samples' AND column_name = 'batch_number') THEN
        ALTER TABLE samples ADD COLUMN batch_number VARCHAR(100);
    END IF;
END $$;

-- Add custody_history if it doesn't exist (chain of custody tracking)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'samples' AND column_name = 'custody_history') THEN
        ALTER TABLE samples ADD COLUMN custody_history JSON;
    END IF;
END $$;

-- ============================================================================
-- ADD MISSING COLUMNS TO INCOMING_INSPECTIONS TABLE
-- These columns enable allocation workflow tracking
-- ============================================================================

-- Add receipt_id to link inspection to receipt
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'incoming_inspections' AND column_name = 'receipt_id') THEN
        ALTER TABLE incoming_inspections ADD COLUMN receipt_id INTEGER REFERENCES sample_receipts(id);
        CREATE INDEX IF NOT EXISTS idx_incoming_inspections_receipt_id ON incoming_inspections(receipt_id);
    END IF;
END $$;

-- Add allocation_triggered flag
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'incoming_inspections' AND column_name = 'allocation_triggered') THEN
        ALTER TABLE incoming_inspections ADD COLUMN allocation_triggered BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Add allocated_sample_id to track which sample was created from this inspection
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'incoming_inspections' AND column_name = 'allocated_sample_id') THEN
        ALTER TABLE incoming_inspections ADD COLUMN allocated_sample_id INTEGER;
    END IF;
END $$;

-- ============================================================================
-- ADD MISSING COLUMNS TO SERVICE_REQUESTS TABLE
-- These columns enable sample quantity tracking
-- ============================================================================

-- Add expected_sample_quantity
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'service_requests' AND column_name = 'expected_sample_quantity') THEN
        ALTER TABLE service_requests ADD COLUMN expected_sample_quantity INTEGER DEFAULT 1;
    END IF;
END $$;

-- Add actual_sample_quantity
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'service_requests' AND column_name = 'actual_sample_quantity') THEN
        ALTER TABLE service_requests ADD COLUMN actual_sample_quantity INTEGER;
    END IF;
END $$;

-- Add quantity_verified flag
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'service_requests' AND column_name = 'quantity_verified') THEN
        ALTER TABLE service_requests ADD COLUMN quantity_verified BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Add receipt_id to link service request to receipt
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'service_requests' AND column_name = 'receipt_id') THEN
        ALTER TABLE service_requests ADD COLUMN receipt_id INTEGER REFERENCES sample_receipts(id);
    END IF;
END $$;

-- ============================================================================
-- CREATE SAMPLE_RECEIPTS TABLE IF NOT EXISTS
-- This table is needed for the traceability chain
-- ============================================================================

CREATE TABLE IF NOT EXISTS sample_receipts (
    id SERIAL PRIMARY KEY,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    service_request_id INTEGER REFERENCES service_requests(id),
    received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    received_by_id INTEGER REFERENCES users(id),
    client_name VARCHAR(100),
    client_reference VARCHAR(100),
    courier_name VARCHAR(100),
    tracking_number VARCHAR(100),
    package_count INTEGER DEFAULT 1,
    package_condition VARCHAR(50),
    package_photos JSON,
    expected_sample_count INTEGER,
    actual_sample_count INTEGER,
    quantity_mismatch BOOLEAN DEFAULT FALSE,
    mismatch_notes TEXT,
    requires_supervisor_approval BOOLEAN DEFAULT FALSE,
    supervisor_approved BOOLEAN,
    supervisor_id INTEGER REFERENCES users(id),
    approval_date TIMESTAMP,
    approval_notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sample_receipts_service_request ON sample_receipts(service_request_id);
CREATE INDEX IF NOT EXISTS idx_sample_receipts_received_date ON sample_receipts(received_date);
CREATE INDEX IF NOT EXISTS idx_sample_receipts_status ON sample_receipts(status);

-- ============================================================================
-- END OF MIGRATION 013
-- ============================================================================
