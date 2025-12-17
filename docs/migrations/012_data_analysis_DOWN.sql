-- =================================================================
-- Migration 012: Data Analysis - DOWN Migration
-- Description: Rollback analysis results and statistical data tables
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop triggers and functions
DROP TRIGGER IF EXISTS spc_data_points_check_limits ON spc_data_points;
DROP TRIGGER IF EXISTS spc_control_charts_update_timestamp ON spc_control_charts;
DROP FUNCTION IF EXISTS check_spc_control_limits() CASCADE;
DROP FUNCTION IF EXISTS update_spc_charts_timestamp() CASCADE;
DROP FUNCTION IF EXISTS calculate_basic_stats(FLOAT[]) CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_comparison_analysis_id;
DROP INDEX IF EXISTS idx_trend_analysis_parameter;
DROP INDEX IF EXISTS idx_trend_analysis_id;
DROP INDEX IF EXISTS idx_analysis_widgets_id;
DROP INDEX IF EXISTS idx_analysis_dashboards_active;
DROP INDEX IF EXISTS idx_analysis_dashboards_id;
DROP INDEX IF EXISTS idx_spc_data_points_date;
DROP INDEX IF EXISTS idx_spc_data_points_chart;
DROP INDEX IF EXISTS idx_spc_control_charts_active;
DROP INDEX IF EXISTS idx_spc_control_charts_id;
DROP INDEX IF EXISTS idx_data_exports_status;
DROP INDEX IF EXISTS idx_data_exports_date;
DROP INDEX IF EXISTS idx_data_exports_type;
DROP INDEX IF EXISTS idx_data_exports_id;
DROP INDEX IF EXISTS idx_analysis_results_created;
DROP INDEX IF EXISTS idx_analysis_results_type;
DROP INDEX IF EXISTS idx_analysis_results_id;

-- Drop tables
DROP TABLE IF EXISTS comparison_analysis CASCADE;
DROP TABLE IF EXISTS trend_analysis CASCADE;
DROP TABLE IF EXISTS analysis_widgets CASCADE;
DROP TABLE IF EXISTS analysis_dashboards CASCADE;
DROP TABLE IF EXISTS spc_data_points CASCADE;
DROP TABLE IF EXISTS spc_control_charts CASCADE;
DROP TABLE IF EXISTS data_exports CASCADE;
DROP TABLE IF EXISTS analysis_results CASCADE;

COMMIT;
