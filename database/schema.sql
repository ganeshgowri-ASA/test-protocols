-- PV Testing Protocol Framework Database Schema
-- PostgreSQL Schema for storing protocol executions and results
-- Version: 1.0.0

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Protocols registry
CREATE TABLE protocols (
    protocol_id VARCHAR(20) PRIMARY KEY,
    protocol_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    standard_reference VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Protocol executions
CREATE TABLE protocol_executions (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    protocol_id VARCHAR(20) NOT NULL REFERENCES protocols(protocol_id),
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test setup parameters
CREATE TABLE test_parameters (
    id SERIAL PRIMARY KEY,
    execution_id UUID NOT NULL REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_value TEXT,
    parameter_unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test data (time-series and raw measurements)
CREATE TABLE test_data (
    id SERIAL PRIMARY KEY,
    execution_id UUID NOT NULL REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    data_type VARCHAR(100) NOT NULL,
    data_json JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    execution_id UUID NOT NULL REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    result_name VARCHAR(100) NOT NULL,
    result_value NUMERIC,
    result_unit VARCHAR(50),
    result_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Validation results
CREATE TABLE validation_results (
    id SERIAL PRIMARY KEY,
    execution_id UUID NOT NULL REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    validation_level VARCHAR(20) NOT NULL,
    field_name VARCHAR(100),
    message TEXT,
    expected_value TEXT,
    actual_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports
CREATE TABLE reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    report_format VARCHAR(20) NOT NULL,
    report_data BYTEA,
    file_path VARCHAR(512),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit trail
CREATE TABLE audit_trail (
    id SERIAL PRIMARY KEY,
    execution_id UUID REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    user_id VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CATEGORY-SPECIFIC TABLES
-- ============================================================================

-- Performance protocols
CREATE TABLE performance_test_executions (
    execution_id UUID PRIMARY KEY REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    irradiance NUMERIC,
    cell_temperature NUMERIC,
    ambient_temperature NUMERIC,
    isc NUMERIC,
    voc NUMERIC,
    imp NUMERIC,
    vmp NUMERIC,
    pmax NUMERIC,
    fill_factor NUMERIC,
    efficiency NUMERIC
);

-- Degradation protocols
CREATE TABLE degradation_test_executions (
    execution_id UUID PRIMARY KEY REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    initial_power NUMERIC,
    final_power NUMERIC,
    power_loss_pct NUMERIC,
    degradation_rate NUMERIC,
    stress_type VARCHAR(100),
    stress_duration NUMERIC,
    recovery_percentage NUMERIC
);

-- Environmental protocols
CREATE TABLE environmental_test_executions (
    execution_id UUID PRIMARY KEY REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    test_type VARCHAR(100),
    number_of_cycles INTEGER,
    temperature_min NUMERIC,
    temperature_max NUMERIC,
    humidity NUMERIC,
    exposure_duration NUMERIC,
    visual_defects JSONB,
    pass_fail BOOLEAN
);

-- Mechanical protocols
CREATE TABLE mechanical_test_executions (
    execution_id UUID PRIMARY KEY REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    test_type VARCHAR(100),
    load_applied NUMERIC,
    load_unit VARCHAR(20),
    deflection NUMERIC,
    structural_integrity BOOLEAN,
    crack_count INTEGER,
    visual_damage JSONB
);

-- Safety protocols
CREATE TABLE safety_test_executions (
    execution_id UUID PRIMARY KEY REFERENCES protocol_executions(execution_id) ON DELETE CASCADE,
    test_type VARCHAR(100),
    insulation_resistance NUMERIC,
    leakage_current NUMERIC,
    test_voltage NUMERIC,
    dielectric_strength NUMERIC,
    ground_continuity BOOLEAN,
    pass_fail BOOLEAN
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_protocol_executions_protocol_id ON protocol_executions(protocol_id);
CREATE INDEX idx_protocol_executions_status ON protocol_executions(status);
CREATE INDEX idx_protocol_executions_created_at ON protocol_executions(created_at);
CREATE INDEX idx_test_parameters_execution_id ON test_parameters(execution_id);
CREATE INDEX idx_test_data_execution_id ON test_data(execution_id);
CREATE INDEX idx_analysis_results_execution_id ON analysis_results(execution_id);
CREATE INDEX idx_validation_results_execution_id ON validation_results(execution_id);
CREATE INDEX idx_audit_trail_execution_id ON audit_trail(execution_id);
CREATE INDEX idx_audit_trail_timestamp ON audit_trail(timestamp);

-- JSONB indexes for efficient querying
CREATE INDEX idx_test_data_json ON test_data USING GIN (data_json);
CREATE INDEX idx_analysis_results_json ON analysis_results USING GIN (result_json);
CREATE INDEX idx_validation_results_level ON validation_results(validation_level);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_protocols_updated_at
    BEFORE UPDATE ON protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_protocol_executions_updated_at
    BEFORE UPDATE ON protocol_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to create audit trail entry
CREATE OR REPLACE FUNCTION create_audit_entry()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_trail (execution_id, event_type, event_data, timestamp)
    VALUES (NEW.execution_id, TG_OP, row_to_json(NEW)::jsonb, CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Audit triggers
CREATE TRIGGER audit_protocol_execution_insert
    AFTER INSERT ON protocol_executions
    FOR EACH ROW EXECUTE FUNCTION create_audit_entry();

CREATE TRIGGER audit_protocol_execution_update
    AFTER UPDATE ON protocol_executions
    FOR EACH ROW EXECUTE FUNCTION create_audit_entry();

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- Summary view for all executions
CREATE VIEW v_execution_summary AS
SELECT
    pe.execution_id,
    pe.protocol_id,
    p.protocol_name,
    p.category,
    pe.status,
    pe.started_at,
    pe.completed_at,
    pe.duration_seconds,
    COUNT(DISTINCT vr.id) FILTER (WHERE vr.validation_level = 'ERROR') as error_count,
    COUNT(DISTINCT vr.id) FILTER (WHERE vr.validation_level = 'WARNING') as warning_count,
    pe.created_at
FROM protocol_executions pe
JOIN protocols p ON pe.protocol_id = p.protocol_id
LEFT JOIN validation_results vr ON pe.execution_id = vr.execution_id
GROUP BY pe.execution_id, p.protocol_name, p.category;

-- Performance summary view
CREATE VIEW v_performance_summary AS
SELECT
    es.*,
    pte.pmax,
    pte.efficiency,
    pte.fill_factor,
    pte.irradiance,
    pte.cell_temperature
FROM v_execution_summary es
JOIN performance_test_executions pte ON es.execution_id = pte.execution_id
WHERE es.category = 'performance';

-- Degradation summary view
CREATE VIEW v_degradation_summary AS
SELECT
    es.*,
    dte.initial_power,
    dte.final_power,
    dte.power_loss_pct,
    dte.degradation_rate,
    dte.stress_type
FROM v_execution_summary es
JOIN degradation_test_executions dte ON es.execution_id = dte.execution_id
WHERE es.category = 'degradation';

-- ============================================================================
-- SEED DATA - Insert all 54 protocols
-- ============================================================================

INSERT INTO protocols (protocol_id, protocol_name, category, version, standard_reference, description) VALUES
-- Performance Protocols
('STC-001', 'Standard Test Conditions (STC) Performance Test', 'performance', '1.0.0', 'IEC 61215-1:2021 MQT 01', 'Measurement of electrical performance at Standard Test Conditions'),
('NOCT-001', 'Nominal Operating Cell Temperature (NOCT) Test', 'performance', '1.0.0', 'IEC 61215-2:2021', 'Measurement of module operating temperature under specified conditions'),
('LIC-001', 'Low Irradiance Characterization', 'performance', '1.0.0', 'IEC 61853-1:2011', 'Performance characterization at low irradiance levels'),
('PERF-001', 'Performance Rating Test - Matrix Conditions', 'performance', '1.0.0', 'IEC 61853-1:2011', 'Performance measurement at multiple irradiance and temperature conditions'),
('PERF-002', 'Annual Energy Yield Prediction', 'performance', '1.0.0', 'IEC 61853-3:2018', 'Energy yield prediction based on climate data and performance matrix'),
('IAM-001', 'Incidence Angle Modifier (IAM) Test', 'performance', '1.0.0', 'IEC 61853-2:2016', 'Effect of angle of incidence on module performance'),
('SPEC-001', 'Spectral Response Measurement', 'performance', '1.0.0', 'IEC 60904-8:2014', 'Spectral response and quantum efficiency measurement'),
('TEMP-001', 'Temperature Coefficient Measurement', 'performance', '1.0.0', 'IEC 60891:2021', 'Measurement of temperature coefficients for Isc, Voc, and Pmax'),
('ENER-001', 'Energy Rating Test', 'performance', '1.0.0', 'IEC 61853-3:2018', 'Energy rating calculation for different climate zones'),
('BIFI-001', 'Bifacial Module Characterization', 'performance', '1.0.0', 'IEC TS 60904-1-2:2019', 'Characterization of bifacial modules under front and rear irradiance'),
('TRACK-001', 'Tracking System Performance Evaluation', 'performance', '1.0.0', 'IEC 62817:2014', 'Performance evaluation of solar tracking systems'),
('CONC-001', 'Concentrator PV System Test', 'performance', '1.0.0', 'IEC 62670-1:2013', 'Performance testing of concentrator photovoltaic systems'),

-- Degradation Protocols
('LID-001', 'Light-Induced Degradation (LID) Test', 'degradation', '1.0.0', 'IEC 61215-2:2021 MQT 19', 'Evaluation of power degradation due to light exposure'),
('LETID-001', 'Light and Elevated Temperature Induced Degradation', 'degradation', '1.0.0', 'IEC TS 63126:2020', 'Evaluation of combined light and temperature induced degradation'),
('PID-001', 'Potential-Induced Degradation (PID) Test', 'degradation', '1.0.0', 'IEC 62804-1:2015', 'Assessment of degradation due to high voltage stress'),
('PID-002', 'PID Recovery Test', 'degradation', '1.0.0', 'IEC 62804-1:2015', 'Evaluation of power recovery after PID stress'),
('UVID-001', 'UV-Induced Degradation Test', 'degradation', '1.0.0', 'IEC 61215-2:2021 MQT 10', 'Assessment of UV radiation effects on module performance'),
('SPONGE-001', 'Sponge Layer Formation Detection', 'degradation', '1.0.0', 'Internal Test Method', 'Detection and characterization of sponge layer defects'),
('SNAIL-001', 'Snail Trail Defect Analysis', 'degradation', '1.0.0', 'Internal Test Method', 'Detection and analysis of snail trail defects'),
('DELAM-001', 'Delamination Detection and Analysis', 'degradation', '1.0.0', 'IEC 61215-2:2021', 'Detection and quantification of encapsulant delamination'),
('CORR-001', 'Corrosion Resistance Test', 'degradation', '1.0.0', 'IEC 61215-2:2021 MQT 12', 'Assessment of module resistance to corrosion'),
('CHALK-001', 'Chalking and Discoloration Test', 'degradation', '1.0.0', 'ASTM D4214', 'Assessment of backsheet chalking and discoloration'),
('YELLOW-001', 'Encapsulant Yellowing Test', 'degradation', '1.0.0', 'IEC 61215-2:2021', 'Assessment of encapsulant discoloration'),
('CRACK-001', 'Cell Crack Detection and Analysis', 'degradation', '1.0.0', 'IEC TS 62782:2016', 'Detection and classification of cell cracks using EL imaging'),
('SOLDER-001', 'Solder Bond Integrity Test', 'degradation', '1.0.0', 'IEC 61215-2:2021 MQT 16', 'Assessment of solder bond quality and degradation'),
('JBOX-001', 'Junction Box Integrity Test', 'degradation', '1.0.0', 'IEC 61215-2:2021 MQT 08', 'Assessment of junction box adhesion and functionality'),
('SEAL-001', 'Edge Seal Integrity Test', 'degradation', '1.0.0', 'IEC 61215-2:2021', 'Assessment of module edge seal integrity'),

-- Environmental Protocols
('TC-001', 'Thermal Cycling Test', 'environmental', '1.0.0', 'IEC 61215-2:2021 MQT 11', 'Assessment of module durability under thermal stress cycles'),
('DH-001', 'Damp Heat Test - 1000 hours', 'environmental', '1.0.0', 'IEC 61215-2:2021 MQT 13', 'Accelerated aging test at 85°C/85% RH for 1000 hours'),
('DH-002', 'Extended Damp Heat Test - 2000 hours', 'environmental', '1.0.0', 'IEC 61215-2:2021', 'Extended damp heat exposure for harsh climate certification'),
('HF-001', 'Humidity Freeze Test', 'environmental', '1.0.0', 'IEC 61215-2:2021 MQT 12', 'Combined humidity and freeze cycle test'),
('UV-001', 'UV Preconditioning Test', 'environmental', '1.0.0', 'IEC 61215-2:2021 MQT 10', 'UV exposure preconditioning test'),
('SALT-001', 'Salt Mist Corrosion Test', 'environmental', '1.0.0', 'IEC 61701:2020', 'Salt mist exposure test for coastal environments'),
('SAND-001', 'Sand and Dust Resistance Test', 'environmental', '1.0.0', 'IEC 60068-2-68:2017', 'Resistance to sand and dust in desert climates'),
('AMMON-001', 'Ammonia Exposure Test', 'environmental', '1.0.0', 'IEC 62716:2013', 'Resistance to ammonia corrosion in agricultural environments'),
('SO2-001', 'Sulfur Dioxide Exposure Test', 'environmental', '1.0.0', 'Internal Test Method', 'Resistance to SO2 in industrial environments'),
('H2S-001', 'Hydrogen Sulfide Exposure Test', 'environmental', '1.0.0', 'Internal Test Method', 'Resistance to H2S in geothermal and industrial areas'),
('TROP-001', 'Tropical Climate Test Sequence', 'environmental', '1.0.0', 'IEC 61215-2:2021', 'Combined stress test for tropical climates'),
('DESERT-001', 'Desert Climate Test Sequence', 'environmental', '1.0.0', 'IEC 61215-2:2021', 'Combined stress test for desert climates'),

-- Mechanical Protocols
('ML-001', 'Mechanical Load Test - Static', 'mechanical', '1.0.0', 'IEC 61215-2:2021 MQT 15', 'Static mechanical load test at specified pressures'),
('ML-002', 'Mechanical Load Test - Dynamic', 'mechanical', '1.0.0', 'IEC 61215-2:2021 MQT 16', 'Dynamic mechanical load test with cyclic loading'),
('HAIL-001', 'Hail Impact Resistance Test', 'mechanical', '1.0.0', 'IEC 61215-2:2021 MQT 17', 'Impact resistance test simulating hail stones'),
('WIND-001', 'Wind Load Resistance Test', 'mechanical', '1.0.0', 'IEC 61215-2:2021', 'Resistance to wind loads and vibrations'),
('SNOW-001', 'Snow Load Test', 'mechanical', '1.0.0', 'IEC 61215-2:2021', 'Resistance to snow load accumulation'),
('VIBR-001', 'Vibration Test - Transportation', 'mechanical', '1.0.0', 'IEC 61215-2:2021', 'Vibration resistance during transportation'),
('TWIST-001', 'Torsion/Twist Test', 'mechanical', '1.0.0', 'IEC 61215-2:2021 MQT 18', 'Resistance to torsional stress'),
('TERM-001', 'Terminal Strength Test', 'mechanical', '1.0.0', 'IEC 61215-2:2021 MQT 07', 'Mechanical strength of cable terminals'),

-- Safety Protocols
('INSU-001', 'Insulation Resistance Test', 'safety', '1.0.0', 'IEC 61215-2:2021 MQT 01', 'Measurement of insulation resistance to ensure electrical safety'),
('WET-001', 'Wet Leakage Current Test', 'safety', '1.0.0', 'IEC 61215-2:2021 MQT 15', 'Leakage current measurement under wet conditions'),
('DIEL-001', 'Dielectric Withstand Test', 'safety', '1.0.0', 'IEC 61215-2:2021 MQT 01', 'High voltage dielectric strength test'),
('GROUND-001', 'Ground Continuity Test', 'safety', '1.0.0', 'IEC 61215-2:2021 MQT 01', 'Verification of grounding conductor continuity'),
('HOT-001', 'Hot Spot Endurance Test', 'safety', '1.0.0', 'IEC 61215-2:2021 MQT 09', 'Ability to withstand hot spot heating effects'),
('BYPASS-001', 'Bypass Diode Thermal Test', 'safety', '1.0.0', 'IEC 61215-2:2021 MQT 18', 'Thermal performance of bypass diodes under stress'),
('FIRE-001', 'Fire Resistance Test', 'safety', '1.0.0', 'UL 1703 / IEC 61730-2', 'Fire resistance and flame spread characteristics');

-- ============================================================================
-- GRANT PERMISSIONS (adjust as needed for your environment)
-- ============================================================================

-- Grant read/write to application user
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pv_testing_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO pv_testing_app;
