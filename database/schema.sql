-- SPONGE-001 Database Schema
-- Sponge Effect Testing Protocol Data Model

-- Drop tables if they exist (for clean re-creation)
DROP TABLE IF EXISTS sponge_analysis CASCADE;
DROP TABLE IF EXISTS sponge_measurements CASCADE;
DROP TABLE IF EXISTS sponge_samples CASCADE;
DROP TABLE IF EXISTS sponge_tests CASCADE;

-- Main test table
CREATE TABLE sponge_tests (
    test_id UUID PRIMARY KEY,
    protocol_version VARCHAR(20) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    operator_id VARCHAR(100) NOT NULL,
    chamber_id VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Test parameters (stored as JSONB for flexibility)
    test_parameters JSONB,

    CONSTRAINT valid_status CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'aborted'))
);

-- Sample information table
CREATE TABLE sponge_samples (
    sample_id UUID PRIMARY KEY,
    test_id UUID NOT NULL REFERENCES sponge_tests(test_id) ON DELETE CASCADE,
    sample_serial VARCHAR(100) NOT NULL UNIQUE,
    manufacturer VARCHAR(200),
    model VARCHAR(200),
    technology_type VARCHAR(100),
    rated_power_w DECIMAL(10, 2),

    -- Initial characterization
    initial_weight_g DECIMAL(10, 3),
    initial_pmax_w DECIMAL(10, 2),
    initial_voc_v DECIMAL(8, 2),
    initial_isc_a DECIMAL(8, 2),
    initial_ff_percent DECIMAL(5, 2),

    -- Final characterization
    final_weight_g DECIMAL(10, 3),
    final_pmax_w DECIMAL(10, 2),
    final_voc_v DECIMAL(8, 2),
    final_isc_a DECIMAL(8, 2),
    final_ff_percent DECIMAL(5, 2),

    -- Visual inspection results (JSONB for structured defect data)
    initial_inspection JSONB,
    final_inspection JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Measurement data table
CREATE TABLE sponge_measurements (
    measurement_id UUID PRIMARY KEY,
    sample_id UUID NOT NULL REFERENCES sponge_samples(sample_id) ON DELETE CASCADE,
    cycle_number INTEGER NOT NULL,
    phase VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Weight measurements
    weight_g DECIMAL(10, 3),

    -- Electrical measurements
    pmax_w DECIMAL(10, 2),
    voc_v DECIMAL(8, 2),
    isc_a DECIMAL(8, 2),
    ff_percent DECIMAL(5, 2),

    -- Environmental conditions
    temperature_c DECIMAL(5, 2),
    rh_percent DECIMAL(5, 2),

    -- Additional data (for extensibility)
    additional_data JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_phase CHECK (phase IN ('initial', 'humid', 'dry', 'final')),
    CONSTRAINT valid_cycle CHECK (cycle_number >= 0),
    CONSTRAINT valid_rh CHECK (rh_percent IS NULL OR (rh_percent >= 0 AND rh_percent <= 100))
);

-- Analysis results table
CREATE TABLE sponge_analysis (
    analysis_id UUID PRIMARY KEY,
    test_id UUID NOT NULL REFERENCES sponge_tests(test_id) ON DELETE CASCADE,
    sample_id UUID NOT NULL REFERENCES sponge_samples(sample_id) ON DELETE CASCADE,

    -- Moisture metrics
    moisture_absorption_percent DECIMAL(5, 3),
    moisture_desorption_percent DECIMAL(5, 3),
    sponge_coefficient DECIMAL(8, 4),
    avg_absorption_rate_g_per_cycle DECIMAL(8, 4),
    avg_desorption_rate_g_per_cycle DECIMAL(8, 4),

    -- Performance degradation metrics
    pmax_degradation_percent DECIMAL(5, 2),
    voc_degradation_percent DECIMAL(5, 2),
    isc_degradation_percent DECIMAL(5, 2),
    ff_degradation_percent DECIMAL(5, 2),

    -- Reversible vs irreversible degradation
    reversible_degradation_percent DECIMAL(5, 2),
    irreversible_degradation_percent DECIMAL(5, 2),

    -- Quality control results
    pass_fail VARCHAR(20) NOT NULL,
    qc_notes TEXT,

    -- Analysis metadata
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_by VARCHAR(100),

    -- Detailed results (JSONB for flexibility)
    detailed_results JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_pass_fail CHECK (pass_fail IN ('PASS', 'FAIL', 'WARNING')),
    UNIQUE(test_id, sample_id)
);

-- Indexes for performance optimization
CREATE INDEX idx_sponge_tests_status ON sponge_tests(status);
CREATE INDEX idx_sponge_tests_start_date ON sponge_tests(start_date);
CREATE INDEX idx_sponge_samples_test_id ON sponge_samples(test_id);
CREATE INDEX idx_sponge_samples_serial ON sponge_samples(sample_serial);
CREATE INDEX idx_sponge_measurements_sample_id ON sponge_measurements(sample_id);
CREATE INDEX idx_sponge_measurements_cycle ON sponge_measurements(cycle_number);
CREATE INDEX idx_sponge_measurements_phase ON sponge_measurements(phase);
CREATE INDEX idx_sponge_measurements_timestamp ON sponge_measurements(timestamp);
CREATE INDEX idx_sponge_analysis_test_id ON sponge_analysis(test_id);
CREATE INDEX idx_sponge_analysis_pass_fail ON sponge_analysis(pass_fail);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_sponge_tests_updated_at
    BEFORE UPDATE ON sponge_tests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sponge_samples_updated_at
    BEFORE UPDATE ON sponge_samples
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries

-- View: Test summary with sample counts
CREATE OR REPLACE VIEW vw_sponge_test_summary AS
SELECT
    t.test_id,
    t.protocol_version,
    t.start_date,
    t.end_date,
    t.status,
    t.operator_id,
    COUNT(DISTINCT s.sample_id) AS num_samples,
    COUNT(m.measurement_id) AS num_measurements,
    COUNT(DISTINCT CASE WHEN a.pass_fail = 'PASS' THEN s.sample_id END) AS samples_passed,
    COUNT(DISTINCT CASE WHEN a.pass_fail = 'FAIL' THEN s.sample_id END) AS samples_failed,
    COUNT(DISTINCT CASE WHEN a.pass_fail = 'WARNING' THEN s.sample_id END) AS samples_warning
FROM sponge_tests t
LEFT JOIN sponge_samples s ON t.test_id = s.test_id
LEFT JOIN sponge_measurements m ON s.sample_id = m.sample_id
LEFT JOIN sponge_analysis a ON t.test_id = a.test_id AND s.sample_id = a.sample_id
GROUP BY t.test_id, t.protocol_version, t.start_date, t.end_date, t.status, t.operator_id;

-- View: Sample performance summary
CREATE OR REPLACE VIEW vw_sponge_sample_performance AS
SELECT
    s.sample_id,
    s.test_id,
    s.sample_serial,
    s.manufacturer,
    s.model,
    s.initial_pmax_w,
    s.final_pmax_w,
    ROUND(((s.initial_pmax_w - s.final_pmax_w) / s.initial_pmax_w * 100)::numeric, 2) AS pmax_degradation_percent,
    s.initial_weight_g,
    s.final_weight_g,
    ROUND(((s.final_weight_g - s.initial_weight_g) / s.initial_weight_g * 100)::numeric, 3) AS weight_change_percent,
    a.moisture_absorption_percent,
    a.sponge_coefficient,
    a.reversible_degradation_percent,
    a.irreversible_degradation_percent,
    a.pass_fail
FROM sponge_samples s
LEFT JOIN sponge_analysis a ON s.sample_id = a.sample_id;

-- View: Cycle-by-cycle measurements
CREATE OR REPLACE VIEW vw_sponge_cycle_data AS
SELECT
    m.sample_id,
    s.sample_serial,
    m.cycle_number,
    m.phase,
    m.timestamp,
    m.weight_g,
    m.pmax_w,
    CASE
        WHEN s.initial_pmax_w > 0 THEN
            ROUND(((m.pmax_w / s.initial_pmax_w * 100))::numeric, 2)
        ELSE NULL
    END AS pmax_normalized_percent,
    m.voc_v,
    m.isc_a,
    m.ff_percent,
    m.temperature_c,
    m.rh_percent
FROM sponge_measurements m
JOIN sponge_samples s ON m.sample_id = s.sample_id
ORDER BY m.sample_id, m.cycle_number, m.timestamp;

-- Comments for documentation
COMMENT ON TABLE sponge_tests IS 'Main test information for SPONGE-001 protocol';
COMMENT ON TABLE sponge_samples IS 'Sample information and characterization data';
COMMENT ON TABLE sponge_measurements IS 'Individual measurement data points';
COMMENT ON TABLE sponge_analysis IS 'Analyzed results and quality control data';

COMMENT ON COLUMN sponge_measurements.phase IS 'Test phase: initial, humid, dry, or final';
COMMENT ON COLUMN sponge_analysis.sponge_coefficient IS 'Ratio of absorption to desorption, indicates hysteresis';
COMMENT ON COLUMN sponge_analysis.pass_fail IS 'Overall pass/fail status based on acceptance criteria';
