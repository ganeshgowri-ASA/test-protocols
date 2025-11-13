-- LETID-001 Test Protocol Database Schema
-- Light and Elevated Temperature Induced Degradation Test
-- IEC 61215-2:2021

-- =============================================================================
-- Test Sessions Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS letid001_test_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id VARCHAR(100) UNIQUE NOT NULL,
    protocol_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',

    -- Sample Information
    module_id VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(200) NOT NULL,
    model VARCHAR(200) NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    cell_technology VARCHAR(50) NOT NULL,
    rated_power DECIMAL(10, 2) NOT NULL,

    -- Test Status
    status VARCHAR(50) NOT NULL DEFAULT 'planned',
    -- Status values: planned, in_progress, completed, failed, cancelled

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Test Configuration
    target_temperature DECIMAL(5, 2) DEFAULT 75.0,
    target_irradiance DECIMAL(7, 2) DEFAULT 1000.0,
    planned_duration_hours INT DEFAULT 300,

    -- User/Lab Information
    operator_id VARCHAR(100),
    laboratory VARCHAR(200),
    equipment_id VARCHAR(100),

    -- Notes
    notes TEXT,

    CONSTRAINT valid_status CHECK (status IN ('planned', 'in_progress', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_cell_tech CHECK (cell_technology IN ('mono-PERC', 'multi-PERC', 'n-type', 'HJT', 'TOPCon', 'other')),
    CONSTRAINT positive_power CHECK (rated_power > 0)
);

CREATE INDEX idx_letid001_sessions_module ON letid001_test_sessions(module_id);
CREATE INDEX idx_letid001_sessions_status ON letid001_test_sessions(status);
CREATE INDEX idx_letid001_sessions_created ON letid001_test_sessions(created_at);

-- =============================================================================
-- Initial Characterization Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS letid001_initial_characterization (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES letid001_test_sessions(session_id) ON DELETE CASCADE,

    -- Measurement timestamp
    measured_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Electrical Parameters
    pmax DECIMAL(10, 3) NOT NULL,           -- Maximum power (W)
    voc DECIMAL(8, 3) NOT NULL,             -- Open circuit voltage (V)
    isc DECIMAL(8, 3) NOT NULL,             -- Short circuit current (A)
    vmp DECIMAL(8, 3) NOT NULL,             -- Voltage at max power (V)
    imp DECIMAL(8, 3) NOT NULL,             -- Current at max power (A)
    fill_factor DECIMAL(5, 2) NOT NULL,     -- Fill factor (%)

    -- Measurement Conditions
    measurement_temp DECIMAL(5, 2),         -- Module temperature during measurement (°C)
    measurement_irradiance DECIMAL(7, 2),   -- Irradiance during measurement (W/m²)

    -- Metadata
    equipment_id VARCHAR(100),
    operator_id VARCHAR(100),
    notes TEXT,

    CONSTRAINT one_initial_per_session UNIQUE(session_id),
    CONSTRAINT positive_values CHECK (pmax > 0 AND voc > 0 AND isc > 0 AND fill_factor > 0)
);

CREATE INDEX idx_letid001_initial_session ON letid001_initial_characterization(session_id);

-- =============================================================================
-- Time Series Measurements Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS letid001_time_series (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES letid001_test_sessions(session_id) ON DELETE CASCADE,

    -- Temporal Information
    measured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    elapsed_hours DECIMAL(10, 2) NOT NULL,

    -- Electrical Parameters
    pmax DECIMAL(10, 3) NOT NULL,
    voc DECIMAL(8, 3),
    isc DECIMAL(8, 3),
    vmp DECIMAL(8, 3),
    imp DECIMAL(8, 3),

    -- Environmental Conditions
    module_temp DECIMAL(5, 2) NOT NULL,
    irradiance DECIMAL(7, 2) NOT NULL,
    humidity DECIMAL(5, 2),

    -- Calculated Fields (can be computed or stored)
    normalized_power DECIMAL(6, 2),         -- Normalized to initial (%)
    degradation_percent DECIMAL(6, 3),      -- Degradation from initial (%)

    -- Quality Flags
    data_quality VARCHAR(20) DEFAULT 'good',
    -- Quality values: good, questionable, bad

    -- Metadata
    measurement_type VARCHAR(50) DEFAULT 'periodic',
    notes TEXT,

    CONSTRAINT valid_quality CHECK (data_quality IN ('good', 'questionable', 'bad')),
    CONSTRAINT positive_power_ts CHECK (pmax > 0),
    CONSTRAINT positive_elapsed CHECK (elapsed_hours >= 0),
    CONSTRAINT unique_measurement_time UNIQUE(session_id, elapsed_hours)
);

CREATE INDEX idx_letid001_ts_session ON letid001_time_series(session_id);
CREATE INDEX idx_letid001_ts_elapsed ON letid001_time_series(session_id, elapsed_hours);
CREATE INDEX idx_letid001_ts_measured_at ON letid001_time_series(measured_at);

-- =============================================================================
-- Final Characterization Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS letid001_final_characterization (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES letid001_test_sessions(session_id) ON DELETE CASCADE,

    -- Measurement timestamp
    measured_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Electrical Parameters
    pmax DECIMAL(10, 3) NOT NULL,
    voc DECIMAL(8, 3) NOT NULL,
    isc DECIMAL(8, 3) NOT NULL,
    vmp DECIMAL(8, 3) NOT NULL,
    imp DECIMAL(8, 3) NOT NULL,
    fill_factor DECIMAL(5, 2) NOT NULL,

    -- Measurement Conditions
    measurement_temp DECIMAL(5, 2),
    measurement_irradiance DECIMAL(7, 2),

    -- Metadata
    equipment_id VARCHAR(100),
    operator_id VARCHAR(100),
    notes TEXT,

    CONSTRAINT one_final_per_session UNIQUE(session_id),
    CONSTRAINT positive_values_final CHECK (pmax > 0 AND voc > 0 AND isc > 0 AND fill_factor > 0)
);

CREATE INDEX idx_letid001_final_session ON letid001_final_characterization(session_id);

-- =============================================================================
-- Test Results Summary Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS letid001_results (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES letid001_test_sessions(session_id) ON DELETE CASCADE,

    -- Power Degradation Results
    initial_pmax DECIMAL(10, 3) NOT NULL,
    final_pmax DECIMAL(10, 3) NOT NULL,
    power_degradation_percent DECIMAL(6, 3) NOT NULL,
    degradation_rate_per_hour DECIMAL(10, 6),

    -- Statistical Summary
    max_degradation_percent DECIMAL(6, 3),
    stabilization_hours DECIMAL(10, 2),
    total_exposure_hours DECIMAL(10, 2) NOT NULL,

    -- Environmental Summary
    avg_temperature DECIMAL(5, 2),
    std_temperature DECIMAL(5, 2),
    avg_irradiance DECIMAL(7, 2),
    std_irradiance DECIMAL(7, 2),

    -- Pass/Fail
    pass_fail VARCHAR(20) NOT NULL,
    -- Values: pass, fail, conditional

    -- Acceptance Criteria Checks
    meets_max_degradation BOOLEAN,
    meets_stabilization BOOLEAN,

    -- Model Fitting
    model_type VARCHAR(50),
    model_r_squared DECIMAL(5, 4),
    model_parameters JSONB,

    -- Analysis timestamp
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Report
    report_path VARCHAR(500),

    CONSTRAINT one_result_per_session UNIQUE(session_id),
    CONSTRAINT valid_pass_fail CHECK (pass_fail IN ('pass', 'fail', 'conditional'))
);

CREATE INDEX idx_letid001_results_session ON letid001_results(session_id);
CREATE INDEX idx_letid001_results_pass_fail ON letid001_results(pass_fail);

-- =============================================================================
-- Audit Log Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS letid001_audit_log (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES letid001_test_sessions(session_id) ON DELETE CASCADE,

    -- Event Information
    event_type VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- User/System
    user_id VARCHAR(100),
    system_id VARCHAR(100),

    -- Event Details
    event_data JSONB,
    description TEXT,

    -- Source
    source_ip VARCHAR(50),
    source_application VARCHAR(100)
);

CREATE INDEX idx_letid001_audit_session ON letid001_audit_log(session_id);
CREATE INDEX idx_letid001_audit_timestamp ON letid001_audit_log(event_timestamp);
CREATE INDEX idx_letid001_audit_event_type ON letid001_audit_log(event_type);

-- =============================================================================
-- Views
-- =============================================================================

-- Complete Test Overview View
CREATE OR REPLACE VIEW letid001_test_overview AS
SELECT
    s.session_id,
    s.test_id,
    s.module_id,
    s.manufacturer,
    s.model,
    s.serial_number,
    s.cell_technology,
    s.status,
    s.started_at,
    s.completed_at,
    i.pmax as initial_pmax,
    f.pmax as final_pmax,
    r.power_degradation_percent,
    r.pass_fail,
    r.total_exposure_hours,
    COUNT(ts.id) as num_measurements
FROM letid001_test_sessions s
LEFT JOIN letid001_initial_characterization i ON s.session_id = i.session_id
LEFT JOIN letid001_final_characterization f ON s.session_id = f.session_id
LEFT JOIN letid001_results r ON s.session_id = r.session_id
LEFT JOIN letid001_time_series ts ON s.session_id = ts.session_id
GROUP BY s.session_id, s.test_id, s.module_id, s.manufacturer, s.model,
         s.serial_number, s.cell_technology, s.status, s.started_at,
         s.completed_at, i.pmax, f.pmax, r.power_degradation_percent,
         r.pass_fail, r.total_exposure_hours;

-- =============================================================================
-- Functions
-- =============================================================================

-- Function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for test_sessions table
CREATE TRIGGER update_letid001_sessions_updated_at
    BEFORE UPDATE ON letid001_test_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate degradation automatically
CREATE OR REPLACE FUNCTION calculate_time_series_metrics()
RETURNS TRIGGER AS $$
DECLARE
    initial_power DECIMAL(10,3);
BEGIN
    -- Get initial power for this session
    SELECT pmax INTO initial_power
    FROM letid001_initial_characterization
    WHERE session_id = NEW.session_id;

    IF initial_power IS NOT NULL AND initial_power > 0 THEN
        NEW.normalized_power = (NEW.pmax / initial_power) * 100;
        NEW.degradation_percent = ((NEW.pmax - initial_power) / initial_power) * 100;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic calculation
CREATE TRIGGER calculate_ts_metrics_trigger
    BEFORE INSERT OR UPDATE ON letid001_time_series
    FOR EACH ROW
    EXECUTE FUNCTION calculate_time_series_metrics();

-- =============================================================================
-- Sample Data Insertion (for testing)
-- =============================================================================

-- Uncomment to insert sample test session
/*
INSERT INTO letid001_test_sessions (
    test_id, module_id, manufacturer, model, serial_number,
    cell_technology, rated_power, status, operator_id, laboratory
) VALUES (
    'LETID-2025-001',
    'MOD-12345',
    'SampleSolar Inc.',
    'SS-360-PERC',
    'SN-2025-001',
    'mono-PERC',
    360.0,
    'planned',
    'operator123',
    'PV Test Lab A'
);
*/
