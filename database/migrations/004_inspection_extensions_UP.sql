-- ============================================================================
-- Migration: 004_inspection_extensions_UP.sql
-- Description: Add allocation tracking to incoming_inspections table
-- Date: 2024
-- ============================================================================

-- Add receipt_id foreign key column
ALTER TABLE incoming_inspections
ADD COLUMN IF NOT EXISTS receipt_id INTEGER REFERENCES sample_receipts(id);

-- Add allocation_triggered column
ALTER TABLE incoming_inspections
ADD COLUMN IF NOT EXISTS allocation_triggered BOOLEAN DEFAULT FALSE;

-- Add allocated_sample_id column
ALTER TABLE incoming_inspections
ADD COLUMN IF NOT EXISTS allocated_sample_id INTEGER;

-- Create index on receipt_id
CREATE INDEX IF NOT EXISTS idx_incoming_inspections_receipt_id ON incoming_inspections(receipt_id);

-- Create index on allocation_triggered for filtering
CREATE INDEX IF NOT EXISTS idx_incoming_inspections_allocation ON incoming_inspections(allocation_triggered);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
