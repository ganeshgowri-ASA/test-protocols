-- Quality Checks Schema
-- Database schema for quality control checks and validation

-- Quality Checks Table
-- Stores QC check results for test executions
CREATE TABLE IF NOT EXISTS quality_checks (
    qc_id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES test_executions(execution_id) ON DELETE CASCADE,

    -- Check identification
    check_id VARCHAR(50) NOT NULL,
    check_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(50) CHECK (check_type IN ('range', 'comparison', 'tolerance', 'boolean', 'custom')),
    check_category VARCHAR(50) CHECK (check_category IN ('equipment', 'environment', 'procedure', 'data', 'compliance')),

    -- Check criteria
    expected_value NUMERIC(20, 6),
    actual_value NUMERIC(20, 6),
    tolerance NUMERIC(20, 6),
    tolerance_type VARCHAR(20) CHECK (tolerance_type IN ('absolute', 'percentage', 'not_applicable')),

    -- String-based checks
    expected_text TEXT,
    actual_text TEXT,

    -- Boolean checks
    expected_boolean BOOLEAN,
    actual_boolean BOOLEAN,

    -- Check result
    result VARCHAR(20) CHECK (result IN ('pass', 'fail', 'warning', 'not_applicable', 'pending')),
    deviation NUMERIC(20, 6),
    deviation_pct NUMERIC(10, 4),

    -- Check metadata
    is_critical BOOLEAN DEFAULT FALSE,
    description TEXT,
    failure_impact TEXT,

    -- Audit information
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    checked_by VARCHAR(100),

    -- Disposition
    disposition VARCHAR(20) CHECK (disposition IN ('accepted', 'rejected', 'waived', 'pending_review')),
    disposition_reason TEXT,
    disposition_by VARCHAR(100),
    disposition_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for quality checks
CREATE INDEX idx_quality_checks_execution ON quality_checks(execution_id);
CREATE INDEX idx_quality_checks_check_id ON quality_checks(check_id);
CREATE INDEX idx_quality_checks_result ON quality_checks(result);
CREATE INDEX idx_quality_checks_critical ON quality_checks(is_critical);
CREATE INDEX idx_quality_checks_disposition ON quality_checks(disposition);
CREATE INDEX idx_quality_checks_checked_at ON quality_checks(checked_at);

-- QC Rules Table
-- Defines reusable quality control rules
CREATE TABLE IF NOT EXISTS qc_rules (
    rule_id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(50) REFERENCES test_protocols(protocol_id) ON DELETE CASCADE,

    -- Rule definition
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) CHECK (rule_type IN ('range', 'comparison', 'tolerance', 'boolean', 'custom', 'formula')),
    rule_category VARCHAR(50),

    -- Rule parameters
    target_field VARCHAR(100),
    comparison_operator VARCHAR(20) CHECK (comparison_operator IN ('eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'between', 'in', 'not_in')),
    reference_value NUMERIC(20, 6),
    min_value NUMERIC(20, 6),
    max_value NUMERIC(20, 6),
    tolerance NUMERIC(20, 6),
    tolerance_type VARCHAR(20) CHECK (tolerance_type IN ('absolute', 'percentage')),

    -- Custom formula
    formula TEXT,

    -- Rule metadata
    description TEXT,
    severity VARCHAR(20) CHECK (severity IN ('critical', 'major', 'minor', 'informational')),
    is_active BOOLEAN DEFAULT TRUE,

    -- Execution control
    execution_order INTEGER,
    depends_on_rules INTEGER[],

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

CREATE INDEX idx_qc_rules_protocol ON qc_rules(protocol_id);
CREATE INDEX idx_qc_rules_active ON qc_rules(is_active);
CREATE INDEX idx_qc_rules_severity ON qc_rules(severity);

-- Calibration Records Table
-- Tracks equipment calibration history
CREATE TABLE IF NOT EXISTS calibration_records (
    calibration_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,

    -- Calibration details
    calibration_date DATE NOT NULL,
    next_calibration_date DATE NOT NULL,
    calibration_type VARCHAR(50) CHECK (calibration_type IN ('initial', 'periodic', 'after_repair', 'verification')),

    -- Calibration provider
    calibrated_by VARCHAR(100) NOT NULL,
    calibration_lab VARCHAR(200),
    certificate_number VARCHAR(100),
    certificate_path TEXT,

    -- Calibration results
    status VARCHAR(20) CHECK (status IN ('pass', 'pass_with_adjustment', 'fail', 'informational')),
    adjustment_performed BOOLEAN DEFAULT FALSE,
    adjustment_details TEXT,

    -- Traceability
    reference_standard VARCHAR(200),
    traceability_chain TEXT,

    -- Standards and uncertainty
    calibration_standard VARCHAR(100),
    measurement_uncertainty JSONB,

    -- Out-of-tolerance findings
    out_of_tolerance BOOLEAN DEFAULT FALSE,
    oot_details TEXT,

    -- Data and attachments
    calibration_data JSONB,
    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

CREATE INDEX idx_calibration_equipment ON calibration_records(equipment_id);
CREATE INDEX idx_calibration_date ON calibration_records(calibration_date);
CREATE INDEX idx_calibration_next_date ON calibration_records(next_calibration_date);
CREATE INDEX idx_calibration_status ON calibration_records(status);

-- Non-Conformance Reports (NCR) Table
-- Tracks quality issues and non-conformances
CREATE TABLE IF NOT EXISTS non_conformance_reports (
    ncr_id SERIAL PRIMARY KEY,
    ncr_number VARCHAR(50) UNIQUE NOT NULL,
    execution_id INTEGER REFERENCES test_executions(execution_id) ON DELETE SET NULL,

    -- NCR details
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    ncr_type VARCHAR(50) CHECK (ncr_type IN ('test_failure', 'equipment_issue', 'procedure_deviation', 'data_quality', 'safety', 'other')),
    severity VARCHAR(20) CHECK (severity IN ('critical', 'major', 'minor')) NOT NULL,

    -- Impact assessment
    impact_area VARCHAR(50) CHECK (impact_area IN ('test_results', 'specimen', 'equipment', 'procedure', 'documentation', 'safety')),
    affected_tests INTEGER[],
    affected_specimens INTEGER[],

    -- Root cause analysis
    root_cause TEXT,
    contributing_factors TEXT,

    -- Corrective action
    corrective_action_required BOOLEAN DEFAULT TRUE,
    corrective_action TEXT,
    preventive_action TEXT,
    action_owner VARCHAR(100),
    action_due_date DATE,

    -- Status tracking
    status VARCHAR(20) CHECK (status IN ('open', 'under_investigation', 'action_in_progress', 'verification', 'closed', 'cancelled')) DEFAULT 'open',
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')),

    -- User tracking
    reported_by VARCHAR(100) NOT NULL,
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_to VARCHAR(100),
    investigated_by VARCHAR(100),
    closed_by VARCHAR(100),
    closed_at TIMESTAMP WITH TIME ZONE,

    -- Verification
    verification_required BOOLEAN DEFAULT TRUE,
    verified_by VARCHAR(100),
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ncr_number ON non_conformance_reports(ncr_number);
CREATE INDEX idx_ncr_execution ON non_conformance_reports(execution_id);
CREATE INDEX idx_ncr_type ON non_conformance_reports(ncr_type);
CREATE INDEX idx_ncr_status ON non_conformance_reports(status);
CREATE INDEX idx_ncr_severity ON non_conformance_reports(severity);
CREATE INDEX idx_ncr_reported_at ON non_conformance_reports(reported_at);

-- Corrective Actions Table
-- Tracks corrective and preventive actions
CREATE TABLE IF NOT EXISTS corrective_actions (
    action_id SERIAL PRIMARY KEY,
    ncr_id INTEGER REFERENCES non_conformance_reports(ncr_id) ON DELETE CASCADE,

    -- Action details
    action_type VARCHAR(50) CHECK (action_type IN ('corrective', 'preventive', 'improvement')) NOT NULL,
    action_description TEXT NOT NULL,
    action_category VARCHAR(50),

    -- Assignment and tracking
    assigned_to VARCHAR(100) NOT NULL,
    due_date DATE NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')),

    -- Status
    status VARCHAR(20) CHECK (status IN ('planned', 'in_progress', 'completed', 'verified', 'overdue', 'cancelled')) DEFAULT 'planned',
    completion_date DATE,
    verified_date DATE,

    -- Effectiveness
    effectiveness_check_required BOOLEAN DEFAULT TRUE,
    effectiveness_check_date DATE,
    effectiveness_result VARCHAR(20) CHECK (effectiveness_result IN ('effective', 'partially_effective', 'ineffective', 'pending')),
    effectiveness_notes TEXT,

    -- Resources
    estimated_cost NUMERIC(12, 2),
    actual_cost NUMERIC(12, 2),
    resources_required TEXT,

    -- Documentation
    implementation_notes TEXT,
    verification_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

CREATE INDEX idx_corrective_actions_ncr ON corrective_actions(ncr_id);
CREATE INDEX idx_corrective_actions_assigned ON corrective_actions(assigned_to);
CREATE INDEX idx_corrective_actions_status ON corrective_actions(status);
CREATE INDEX idx_corrective_actions_due_date ON corrective_actions(due_date);

-- Create triggers for updated_at
CREATE TRIGGER update_qc_rules_updated_at
    BEFORE UPDATE ON qc_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ncr_updated_at
    BEFORE UPDATE ON non_conformance_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_corrective_actions_updated_at
    BEFORE UPDATE ON corrective_actions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Views for QC management

-- View: Critical QC Failures
CREATE OR REPLACE VIEW critical_qc_failures AS
SELECT
    qc.qc_id,
    qc.execution_id,
    e.protocol_id,
    e.module_id,
    e.test_date,
    qc.check_name,
    qc.expected_value,
    qc.actual_value,
    qc.result,
    qc.disposition
FROM quality_checks qc
JOIN test_executions e ON qc.execution_id = e.execution_id
WHERE qc.is_critical = TRUE
  AND qc.result = 'fail'
  AND qc.disposition IS NULL;

-- View: Overdue Calibrations
CREATE OR REPLACE VIEW overdue_calibrations AS
SELECT
    e.equipment_id,
    e.equipment_name,
    e.equipment_type,
    e.last_calibration_date,
    e.next_calibration_date,
    CURRENT_DATE - e.next_calibration_date as days_overdue,
    e.status
FROM equipment e
WHERE e.calibration_required = TRUE
  AND e.next_calibration_date < CURRENT_DATE
  AND e.status = 'active';

-- View: Open Non-Conformances
CREATE OR REPLACE VIEW open_non_conformances AS
SELECT
    ncr.ncr_id,
    ncr.ncr_number,
    ncr.title,
    ncr.ncr_type,
    ncr.severity,
    ncr.status,
    ncr.reported_by,
    ncr.reported_at,
    ncr.assigned_to,
    ncr.action_due_date,
    CASE
        WHEN ncr.action_due_date < CURRENT_DATE THEN 'overdue'
        WHEN ncr.action_due_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'due_soon'
        ELSE 'on_track'
    END as due_status
FROM non_conformance_reports ncr
WHERE ncr.status NOT IN ('closed', 'cancelled');

-- Comments for documentation
COMMENT ON TABLE quality_checks IS 'QC check results for test executions';
COMMENT ON TABLE qc_rules IS 'Reusable quality control rules and criteria';
COMMENT ON TABLE calibration_records IS 'Equipment calibration history and records';
COMMENT ON TABLE non_conformance_reports IS 'Quality issues and non-conformance tracking';
COMMENT ON TABLE corrective_actions IS 'Corrective and preventive action tracking';

COMMENT ON COLUMN quality_checks.deviation IS 'Absolute deviation from expected value';
COMMENT ON COLUMN quality_checks.deviation_pct IS 'Percentage deviation from expected value';
COMMENT ON COLUMN qc_rules.depends_on_rules IS 'Array of rule IDs that must pass before this rule';
COMMENT ON COLUMN calibration_records.traceability_chain IS 'Calibration traceability to national/international standards';
