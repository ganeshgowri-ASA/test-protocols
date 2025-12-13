-- ============================================================================
-- Migration 004: Data Analysis Models
-- ============================================================================
-- Purpose: Create tables for test results analytics and data export tracking
-- Models: AnalysisResult, DataExport
-- Author: Claude Code Review
-- Date: 2024-12-05
-- ============================================================================

-- Ensure idempotent execution
-- SQLite compatible syntax

-- ============================================================================
-- Table: analysis_results
-- Purpose: Store data analysis results and statistics from test data
-- ============================================================================
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id VARCHAR(50) UNIQUE NOT NULL,

    -- Analysis metadata
    analysis_type VARCHAR(100),           -- Trend, Comparison, Statistical
    date_range_start DATETIME,
    date_range_end DATETIME,
    filters_applied JSON,                 -- Store filter parameters as JSON

    -- Metrics
    total_tests INTEGER,
    pass_count INTEGER,
    fail_count INTEGER,
    pass_rate FLOAT,

    -- Statistical measures
    mean_value FLOAT,
    median_value FLOAT,
    std_deviation FLOAT,

    -- Chart data
    chart_type VARCHAR(50),
    chart_data JSON,                      -- Store Plotly chart JSON

    -- Audit fields
    created_by VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for analysis_results
CREATE INDEX IF NOT EXISTS idx_analysis_id ON analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_created ON analysis_results(created_at);

-- ============================================================================
-- Table: data_exports
-- Purpose: Track data exports (Excel, CSV, PDF) for audit trail
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    export_id VARCHAR(50) UNIQUE NOT NULL,

    -- Export metadata
    export_type VARCHAR(50),              -- Excel, CSV, PDF
    export_name VARCHAR(200),
    file_path VARCHAR(255),

    -- Export parameters
    date_range VARCHAR(100),
    filters JSON,
    records_count INTEGER,

    -- Audit fields
    exported_by VARCHAR(100),
    exported_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for data_exports
CREATE INDEX IF NOT EXISTS idx_export_id ON data_exports(export_id);
CREATE INDEX IF NOT EXISTS idx_export_type ON data_exports(export_type);
CREATE INDEX IF NOT EXISTS idx_export_date ON data_exports(exported_at);

-- ============================================================================
-- Verification queries (optional - for manual verification)
-- ============================================================================
-- SELECT name FROM sqlite_master WHERE type='table' AND name IN ('analysis_results', 'data_exports');
-- SELECT sql FROM sqlite_master WHERE type='table' AND name='analysis_results';
-- SELECT sql FROM sqlite_master WHERE type='table' AND name='data_exports';
