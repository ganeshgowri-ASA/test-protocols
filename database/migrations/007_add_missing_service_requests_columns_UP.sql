-- ===================================================================================
-- Migration 007: Add Missing service_requests Columns
-- ===================================================================================
-- Purpose: Add columns needed for Sample Receipt workflow integration
-- Target: PostgreSQL (Railway deployment)
-- Author: Comet AI Assistant
-- Date: 2025-01-09
--
-- COLUMNS ADDED:
-- 1. expected_sample_quantity: Number of samples expected in the service request
-- 2. receipt_id: Foreign key linking to sample_receipts table

ALTER TABLE service_requests 
ADD COLUMN IF NOT EXISTS expected_sample_quantity INTEGER,
ADD COLUMN IF NOT EXISTS receipt_id INTEGER REFERENCES sample_receipts(id) ON DELETE SET NULL;
