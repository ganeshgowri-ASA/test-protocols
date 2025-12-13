-- ============================================================================
-- Migration 005: Fix Missing Columns for Railway PostgreSQL
-- ============================================================================
-- Purpose: Add missing columns identified in production deployment
-- Target: PostgreSQL (Railway deployment)
-- Author: Claude Code Review
-- Date: 2024-12-05
--
-- ERRORS FIXED:
-- 1. users.password_hash does not exist
-- 2. samples.status does not exist
-- 3. samples.project_id does not exist
-- 4. incoming_inspections.allocation_triggered does not exist
-- ============================================================================

-- PostgreSQL: Add columns only if they don't exist
-- Using DO blocks for idempotent execution

-- ============================================================================
-- Table: users - Fix missing columns
-- ============================================================================
DO $$
BEGIN
    -- Add password_hash column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'password_hash'
    ) THEN
        ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
        RAISE NOTICE 'Added column: users.password_hash';
    END IF;

    -- Add phone column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'phone'
    ) THEN
        ALTER TABLE users ADD COLUMN phone VARCHAR(20);
        RAISE NOTICE 'Added column: users.phone';
    END IF;

    -- Add department column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'department'
    ) THEN
        ALTER TABLE users ADD COLUMN department VARCHAR(50);
        RAISE NOTICE 'Added column: users.department';
    END IF;

    -- Add last_login column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'last_login'
    ) THEN
        ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
        RAISE NOTICE 'Added column: users.last_login';
    END IF;
END $$;

-- ============================================================================
-- Table: samples - Fix missing columns
-- ============================================================================
DO $$
BEGIN
    -- Add status column if not exists (ENUM type)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'status'
    ) THEN
        ALTER TABLE samples ADD COLUMN status VARCHAR(20) DEFAULT 'received';
        RAISE NOTICE 'Added column: samples.status';
    END IF;

    -- Add project_id column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'project_id'
    ) THEN
        ALTER TABLE samples ADD COLUMN project_id VARCHAR(50);
        RAISE NOTICE 'Added column: samples.project_id';
    END IF;

    -- Add sample_id column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'sample_id'
    ) THEN
        ALTER TABLE samples ADD COLUMN sample_id VARCHAR(50);
        RAISE NOTICE 'Added column: samples.sample_id';
    END IF;

    -- Add qr_code column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'qr_code'
    ) THEN
        ALTER TABLE samples ADD COLUMN qr_code VARCHAR(200);
        RAISE NOTICE 'Added column: samples.qr_code';
    END IF;

    -- Add qr_code_image_path column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'qr_code_image_path'
    ) THEN
        ALTER TABLE samples ADD COLUMN qr_code_image_path VARCHAR(200);
        RAISE NOTICE 'Added column: samples.qr_code_image_path';
    END IF;

    -- Add qr_data column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'qr_data'
    ) THEN
        ALTER TABLE samples ADD COLUMN qr_data JSONB;
        RAISE NOTICE 'Added column: samples.qr_data';
    END IF;

    -- Add current_location column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'current_location'
    ) THEN
        ALTER TABLE samples ADD COLUMN current_location VARCHAR(100);
        RAISE NOTICE 'Added column: samples.current_location';
    END IF;

    -- Add storage_location column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'storage_location'
    ) THEN
        ALTER TABLE samples ADD COLUMN storage_location VARCHAR(100);
        RAISE NOTICE 'Added column: samples.storage_location';
    END IF;

    -- Add allocation_date column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'allocation_date'
    ) THEN
        ALTER TABLE samples ADD COLUMN allocation_date TIMESTAMP;
        RAISE NOTICE 'Added column: samples.allocation_date';
    END IF;

    -- Add allocated_by_id column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'allocated_by_id'
    ) THEN
        ALTER TABLE samples ADD COLUMN allocated_by_id INTEGER REFERENCES users(id);
        RAISE NOTICE 'Added column: samples.allocated_by_id';
    END IF;

    -- Add assigned_protocol_ids column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'assigned_protocol_ids'
    ) THEN
        ALTER TABLE samples ADD COLUMN assigned_protocol_ids JSONB;
        RAISE NOTICE 'Added column: samples.assigned_protocol_ids';
    END IF;

    -- Add current_test_id column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'current_test_id'
    ) THEN
        ALTER TABLE samples ADD COLUMN current_test_id INTEGER;
        RAISE NOTICE 'Added column: samples.current_test_id';
    END IF;

    -- Add tests_completed column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'tests_completed'
    ) THEN
        ALTER TABLE samples ADD COLUMN tests_completed INTEGER DEFAULT 0;
        RAISE NOTICE 'Added column: samples.tests_completed';
    END IF;

    -- Add tests_total column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'tests_total'
    ) THEN
        ALTER TABLE samples ADD COLUMN tests_total INTEGER DEFAULT 0;
        RAISE NOTICE 'Added column: samples.tests_total';
    END IF;

    -- Add overall_result column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'overall_result'
    ) THEN
        ALTER TABLE samples ADD COLUMN overall_result VARCHAR(20);
        RAISE NOTICE 'Added column: samples.overall_result';
    END IF;

    -- Add result_summary column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'result_summary'
    ) THEN
        ALTER TABLE samples ADD COLUMN result_summary TEXT;
        RAISE NOTICE 'Added column: samples.result_summary';
    END IF;

    -- Add specifications column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'specifications'
    ) THEN
        ALTER TABLE samples ADD COLUMN specifications JSONB;
        RAISE NOTICE 'Added column: samples.specifications';
    END IF;

    -- Add photos column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'photos'
    ) THEN
        ALTER TABLE samples ADD COLUMN photos JSONB;
        RAISE NOTICE 'Added column: samples.photos';
    END IF;

    -- Add custody_history column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'custody_history'
    ) THEN
        ALTER TABLE samples ADD COLUMN custody_history JSONB;
        RAISE NOTICE 'Added column: samples.custody_history';
    END IF;

    -- Add completed_at column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'completed_at'
    ) THEN
        ALTER TABLE samples ADD COLUMN completed_at TIMESTAMP;
        RAISE NOTICE 'Added column: samples.completed_at';
    END IF;

    -- Add disposed_at column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'disposed_at'
    ) THEN
        ALTER TABLE samples ADD COLUMN disposed_at TIMESTAMP;
        RAISE NOTICE 'Added column: samples.disposed_at';
    END IF;

    -- Add receipt_id column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'receipt_id'
    ) THEN
        ALTER TABLE samples ADD COLUMN receipt_id INTEGER;
        RAISE NOTICE 'Added column: samples.receipt_id';
    END IF;

    -- Add inspection_id column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'samples' AND column_name = 'inspection_id'
    ) THEN
        ALTER TABLE samples ADD COLUMN inspection_id INTEGER;
        RAISE NOTICE 'Added column: samples.inspection_id';
    END IF;
END $$;

-- ============================================================================
-- Table: incoming_inspections - Fix missing columns
-- ============================================================================
DO $$
BEGIN
    -- Add allocation_triggered column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'incoming_inspections' AND column_name = 'allocation_triggered'
    ) THEN
        ALTER TABLE incoming_inspections ADD COLUMN allocation_triggered BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column: incoming_inspections.allocation_triggered';
    END IF;

    -- Add photos column if not exists (JSON type)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'incoming_inspections' AND column_name = 'photos'
    ) THEN
        ALTER TABLE incoming_inspections ADD COLUMN photos JSONB;
        RAISE NOTICE 'Added column: incoming_inspections.photos';
    END IF;
END $$;

-- ============================================================================
-- Create indexes for new columns (if not exists)
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_samples_project_id ON samples(project_id);
CREATE INDEX IF NOT EXISTS idx_samples_status ON samples(status);
CREATE INDEX IF NOT EXISTS idx_samples_qr_code ON samples(qr_code);

-- ============================================================================
-- Verification query (run manually to check)
-- ============================================================================
-- SELECT column_name, data_type FROM information_schema.columns
-- WHERE table_name IN ('users', 'samples', 'incoming_inspections')
-- ORDER BY table_name, ordinal_position;
