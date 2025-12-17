-- =================================================================
-- Migration 012: Data Analysis - UP Migration
-- Description: Add analysis results and statistical data tables
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Create analysis_results table if not exists
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(50) UNIQUE NOT NULL,

    -- Analysis metadata
    analysis_type VARCHAR(100), -- Trend, Comparison, Statistical, SPC
    analysis_name VARCHAR(200),
    description TEXT,

    -- Date range
    date_range_start TIMESTAMP,
    date_range_end TIMESTAMP,
    filters_applied JSONB,

    -- Metrics
    total_tests INTEGER,
    pass_count INTEGER,
    fail_count INTEGER,
    pass_rate FLOAT,

    -- Statistical measures
    mean_value FLOAT,
    median_value FLOAT,
    std_deviation FLOAT,
    min_value FLOAT,
    max_value FLOAT,
    variance FLOAT,
    coefficient_of_variation FLOAT,

    -- Chart data
    chart_type VARCHAR(50),
    chart_data JSONB,
    chart_config JSONB,

    -- Audit fields
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create data_exports table if not exists
CREATE TABLE IF NOT EXISTS data_exports (
    id SERIAL PRIMARY KEY,
    export_id VARCHAR(50) UNIQUE NOT NULL,

    -- Export metadata
    export_type VARCHAR(50), -- Excel, CSV, PDF, JSON
    export_name VARCHAR(200),
    file_path VARCHAR(255),
    file_size INTEGER,

    -- Export parameters
    date_range VARCHAR(100),
    filters JSONB,
    columns_included JSONB,
    records_count INTEGER,

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT,

    -- Audit fields
    exported_by VARCHAR(100),
    exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create spc_control_charts table for Statistical Process Control
CREATE TABLE IF NOT EXISTS spc_control_charts (
    id SERIAL PRIMARY KEY,
    chart_id VARCHAR(50) UNIQUE NOT NULL,
    chart_name VARCHAR(200) NOT NULL,
    chart_type VARCHAR(50) NOT NULL, -- x_bar, r_chart, p_chart, c_chart, etc.

    -- Configuration
    parameter_name VARCHAR(100),
    measurement_unit VARCHAR(50),
    target_value FLOAT,
    specification_upper FLOAT,
    specification_lower FLOAT,

    -- Control limits
    ucl FLOAT, -- Upper Control Limit
    lcl FLOAT, -- Lower Control Limit
    center_line FLOAT,

    -- Calculation settings
    subgroup_size INTEGER DEFAULT 5,
    sample_count INTEGER DEFAULT 25,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spc_data_points table
CREATE TABLE IF NOT EXISTS spc_data_points (
    id SERIAL PRIMARY KEY,
    chart_id INTEGER REFERENCES spc_control_charts(id) ON DELETE CASCADE,

    -- Data point
    subgroup_number INTEGER,
    value FLOAT NOT NULL,
    sample_size INTEGER,

    -- Statistical values
    range_value FLOAT,
    moving_range FLOAT,

    -- Flags
    out_of_control BOOLEAN DEFAULT FALSE,
    out_of_spec BOOLEAN DEFAULT FALSE,
    rule_violations JSONB, -- Western Electric rules violations

    -- Context
    test_execution_id INTEGER,
    sample_id INTEGER,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Notes
    notes TEXT
);

-- Create analysis_dashboards table
CREATE TABLE IF NOT EXISTS analysis_dashboards (
    id SERIAL PRIMARY KEY,
    dashboard_id VARCHAR(50) UNIQUE NOT NULL,
    dashboard_name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Configuration
    layout JSONB, -- Widget positions and sizes
    widgets JSONB, -- Widget definitions
    refresh_interval INTEGER DEFAULT 300, -- seconds

    -- Access
    is_public BOOLEAN DEFAULT FALSE,
    allowed_roles JSONB DEFAULT '[]',
    owner_id INTEGER,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analysis_widgets table
CREATE TABLE IF NOT EXISTS analysis_widgets (
    id SERIAL PRIMARY KEY,
    widget_id VARCHAR(50) UNIQUE NOT NULL,
    widget_name VARCHAR(200) NOT NULL,
    widget_type VARCHAR(50), -- chart, metric, table, gauge

    -- Configuration
    data_source VARCHAR(100),
    query_config JSONB,
    visualization_config JSONB,
    refresh_interval INTEGER,

    -- Default size
    default_width INTEGER DEFAULT 4,
    default_height INTEGER DEFAULT 3,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trend_analysis table for tracking trends over time
CREATE TABLE IF NOT EXISTS trend_analysis (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(50) UNIQUE NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,

    -- Configuration
    time_period VARCHAR(20), -- daily, weekly, monthly, quarterly
    protocol_ids JSONB DEFAULT '[]',
    sample_types JSONB DEFAULT '[]',

    -- Trend data
    data_points JSONB, -- Array of {date, value, count}
    trend_direction VARCHAR(20), -- increasing, decreasing, stable
    trend_slope FLOAT,
    r_squared FLOAT,

    -- Statistics
    period_count INTEGER,
    total_samples INTEGER,
    average_value FLOAT,
    trend_percentage FLOAT,

    -- Alerts
    alert_threshold FLOAT,
    alert_triggered BOOLEAN DEFAULT FALSE,

    -- Timestamps
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_calculation TIMESTAMP
);

-- Create comparison_analysis table
CREATE TABLE IF NOT EXISTS comparison_analysis (
    id SERIAL PRIMARY KEY,
    comparison_id VARCHAR(50) UNIQUE NOT NULL,
    comparison_name VARCHAR(200) NOT NULL,
    comparison_type VARCHAR(50), -- protocol, equipment, technician, time_period

    -- Configuration
    group_a_config JSONB,
    group_b_config JSONB,

    -- Results
    group_a_stats JSONB, -- mean, std, count, etc.
    group_b_stats JSONB,
    difference FLOAT,
    difference_percentage FLOAT,
    p_value FLOAT, -- Statistical significance
    is_significant BOOLEAN,

    -- Timestamps
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_analysis_results_id ON analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created ON analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_data_exports_id ON data_exports(export_id);
CREATE INDEX IF NOT EXISTS idx_data_exports_type ON data_exports(export_type);
CREATE INDEX IF NOT EXISTS idx_data_exports_date ON data_exports(exported_at);
CREATE INDEX IF NOT EXISTS idx_data_exports_status ON data_exports(status);
CREATE INDEX IF NOT EXISTS idx_spc_control_charts_id ON spc_control_charts(chart_id);
CREATE INDEX IF NOT EXISTS idx_spc_control_charts_active ON spc_control_charts(is_active);
CREATE INDEX IF NOT EXISTS idx_spc_data_points_chart ON spc_data_points(chart_id);
CREATE INDEX IF NOT EXISTS idx_spc_data_points_date ON spc_data_points(measured_at);
CREATE INDEX IF NOT EXISTS idx_analysis_dashboards_id ON analysis_dashboards(dashboard_id);
CREATE INDEX IF NOT EXISTS idx_analysis_dashboards_active ON analysis_dashboards(is_active);
CREATE INDEX IF NOT EXISTS idx_analysis_widgets_id ON analysis_widgets(widget_id);
CREATE INDEX IF NOT EXISTS idx_trend_analysis_id ON trend_analysis(analysis_id);
CREATE INDEX IF NOT EXISTS idx_trend_analysis_parameter ON trend_analysis(parameter_name);
CREATE INDEX IF NOT EXISTS idx_comparison_analysis_id ON comparison_analysis(comparison_id);

-- Create trigger to update spc_control_charts timestamp
CREATE OR REPLACE FUNCTION update_spc_charts_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS spc_control_charts_update_timestamp ON spc_control_charts;
CREATE TRIGGER spc_control_charts_update_timestamp
BEFORE UPDATE ON spc_control_charts
FOR EACH ROW
EXECUTE FUNCTION update_spc_charts_timestamp();

-- Create function to check SPC control limits
CREATE OR REPLACE FUNCTION check_spc_control_limits()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if value is outside control limits
    IF NEW.chart_id IS NOT NULL THEN
        SELECT
            (NEW.value > ucl OR NEW.value < lcl) INTO NEW.out_of_control,
            (NEW.value > specification_upper OR NEW.value < specification_lower) INTO NEW.out_of_spec
        FROM spc_control_charts
        WHERE id = NEW.chart_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS spc_data_points_check_limits ON spc_data_points;
CREATE TRIGGER spc_data_points_check_limits
BEFORE INSERT OR UPDATE ON spc_data_points
FOR EACH ROW
EXECUTE FUNCTION check_spc_control_limits();

-- Create function to calculate basic statistics
CREATE OR REPLACE FUNCTION calculate_basic_stats(p_values FLOAT[])
RETURNS TABLE(
    mean_val FLOAT,
    median_val FLOAT,
    std_dev FLOAT,
    min_val FLOAT,
    max_val FLOAT,
    count_val INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        AVG(v)::FLOAT as mean_val,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY v)::FLOAT as median_val,
        STDDEV(v)::FLOAT as std_dev,
        MIN(v)::FLOAT as min_val,
        MAX(v)::FLOAT as max_val,
        COUNT(v)::INTEGER as count_val
    FROM UNNEST(p_values) as v;
END;
$$ LANGUAGE plpgsql;

-- Insert default analysis dashboard
INSERT INTO analysis_dashboards (dashboard_id, dashboard_name, description, is_public, is_active)
VALUES
    ('DASH-MAIN', 'Main Analytics Dashboard', 'Primary dashboard for test analytics', TRUE, TRUE),
    ('DASH-QC', 'Quality Control Dashboard', 'Quality control and SPC monitoring', TRUE, TRUE),
    ('DASH-PERFORMANCE', 'Performance Dashboard', 'Test performance metrics', TRUE, TRUE)
ON CONFLICT (dashboard_id) DO NOTHING;

COMMIT;
