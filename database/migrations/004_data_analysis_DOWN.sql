-- ============================================================================
-- Migration 004: Data Analysis Models - ROLLBACK
-- ============================================================================
-- Purpose: Remove data analysis tables for rollback
-- WARNING: This will permanently delete all analysis results and export logs!
-- Author: Claude Code Review
-- Date: 2024-12-05
-- ============================================================================

-- Drop indexes first (SQLite drops indexes automatically with table, but explicit for PostgreSQL compatibility)
DROP INDEX IF EXISTS idx_analysis_id;
DROP INDEX IF EXISTS idx_analysis_type;
DROP INDEX IF EXISTS idx_analysis_created;

DROP INDEX IF EXISTS idx_export_id;
DROP INDEX IF EXISTS idx_export_type;
DROP INDEX IF EXISTS idx_export_date;

-- Drop tables
DROP TABLE IF EXISTS analysis_results;
DROP TABLE IF EXISTS data_exports;

-- ============================================================================
-- Verification (optional)
-- ============================================================================
-- SELECT name FROM sqlite_master WHERE type='table' AND name IN ('analysis_results', 'data_exports');
-- Should return empty result after rollback
