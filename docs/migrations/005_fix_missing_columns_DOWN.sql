-- ============================================================================
-- Migration 005: Fix Missing Columns - ROLLBACK
-- ============================================================================
-- Purpose: Remove columns added in 005_fix_missing_columns_UP.sql
-- Target: PostgreSQL (Railway deployment)
-- Author: Claude Code Review
-- Date: 2024-12-05
--
-- WARNING: This will remove data from these columns!
-- Only use for rollback if migration causes issues.
-- ============================================================================

-- NOTE: Rollback is generally NOT recommended as it will cause data loss
-- This script is provided for emergency rollback only

-- Drop indexes first
DROP INDEX IF EXISTS idx_samples_project_id;
DROP INDEX IF EXISTS idx_samples_status;
DROP INDEX IF EXISTS idx_samples_qr_code;

-- ============================================================================
-- Table: users - Remove added columns
-- ============================================================================
DO $$
BEGIN
    -- Only drop if column exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'password_hash'
    ) THEN
        ALTER TABLE users DROP COLUMN password_hash;
        RAISE NOTICE 'Dropped column: users.password_hash';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'phone'
    ) THEN
        ALTER TABLE users DROP COLUMN phone;
        RAISE NOTICE 'Dropped column: users.phone';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'department'
    ) THEN
        ALTER TABLE users DROP COLUMN department;
        RAISE NOTICE 'Dropped column: users.department';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'last_login'
    ) THEN
        ALTER TABLE users DROP COLUMN last_login;
        RAISE NOTICE 'Dropped column: users.last_login';
    END IF;
END $$;

-- ============================================================================
-- Table: samples - Remove added columns
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'status') THEN
        ALTER TABLE samples DROP COLUMN status;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'project_id') THEN
        ALTER TABLE samples DROP COLUMN project_id;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'sample_id') THEN
        ALTER TABLE samples DROP COLUMN sample_id;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'qr_code') THEN
        ALTER TABLE samples DROP COLUMN qr_code;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'qr_code_image_path') THEN
        ALTER TABLE samples DROP COLUMN qr_code_image_path;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'qr_data') THEN
        ALTER TABLE samples DROP COLUMN qr_data;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'current_location') THEN
        ALTER TABLE samples DROP COLUMN current_location;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'storage_location') THEN
        ALTER TABLE samples DROP COLUMN storage_location;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'allocation_date') THEN
        ALTER TABLE samples DROP COLUMN allocation_date;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'allocated_by_id') THEN
        ALTER TABLE samples DROP COLUMN allocated_by_id;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'assigned_protocol_ids') THEN
        ALTER TABLE samples DROP COLUMN assigned_protocol_ids;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'current_test_id') THEN
        ALTER TABLE samples DROP COLUMN current_test_id;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'tests_completed') THEN
        ALTER TABLE samples DROP COLUMN tests_completed;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'tests_total') THEN
        ALTER TABLE samples DROP COLUMN tests_total;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'overall_result') THEN
        ALTER TABLE samples DROP COLUMN overall_result;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'result_summary') THEN
        ALTER TABLE samples DROP COLUMN result_summary;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'specifications') THEN
        ALTER TABLE samples DROP COLUMN specifications;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'photos') THEN
        ALTER TABLE samples DROP COLUMN photos;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'custody_history') THEN
        ALTER TABLE samples DROP COLUMN custody_history;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'completed_at') THEN
        ALTER TABLE samples DROP COLUMN completed_at;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'disposed_at') THEN
        ALTER TABLE samples DROP COLUMN disposed_at;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'receipt_id') THEN
        ALTER TABLE samples DROP COLUMN receipt_id;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'samples' AND column_name = 'inspection_id') THEN
        ALTER TABLE samples DROP COLUMN inspection_id;
    END IF;
END $$;

-- ============================================================================
-- Table: incoming_inspections - Remove added columns
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'incoming_inspections' AND column_name = 'allocation_triggered'
    ) THEN
        ALTER TABLE incoming_inspections DROP COLUMN allocation_triggered;
        RAISE NOTICE 'Dropped column: incoming_inspections.allocation_triggered';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'incoming_inspections' AND column_name = 'photos'
    ) THEN
        ALTER TABLE incoming_inspections DROP COLUMN photos;
        RAISE NOTICE 'Dropped column: incoming_inspections.photos';
    END IF;
END $$;

-- ============================================================================
-- Verification (run manually)
-- ============================================================================
-- SELECT table_name, column_name FROM information_schema.columns
-- WHERE table_name IN ('users', 'samples', 'incoming_inspections')
-- ORDER BY table_name, column_name;
