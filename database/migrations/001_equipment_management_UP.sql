-- =================================================================
-- Phase 1: Equipment Management System - UP Migration
-- Description: Adds equipment and calibration tables
-- Created: 2025-12-01
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Create equipment table
CREATE TABLE IF NOT EXISTS equipment_phase1 (
    id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(150),
    model_number VARCHAR(100),
    serial_number VARCHAR(150) UNIQUE,
    purchase_date DATE,
    installation_date DATE,
    warranty_expiry DATE,
    location VARCHAR(200),
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    last_calibration_date DATE,
    next_calibration_due DATE,
    calibration_frequency_days INTEGER DEFAULT 365,
    specifications JSONB,
    maintenance_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    CONSTRAINT equipment_status_check CHECK (status IN ('Active', 'Inactive', 'Under Maintenance', 'Retired', 'Calibration Due'))
);

-- Create calibration_records table
CREATE TABLE IF NOT EXISTS calibration_records_phase1 (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment_phase1(id) ON DELETE CASCADE,
    calibration_date DATE NOT NULL,
    calibration_due_date DATE NOT NULL,
    calibrated_by VARCHAR(150) NOT NULL,
    calibration_agency VARCHAR(200),
    certificate_number VARCHAR(150),
    calibration_result VARCHAR(50) NOT NULL,
    deviations JSONB,
    remarks TEXT,
    attachment_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    CONSTRAINT calibration_result_check CHECK (calibration_result IN ('Pass', 'Fail', 'Conditional Pass'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_equipment_equipment_id ON equipment_phase1(equipment_id);
CREATE INDEX IF NOT EXISTS idx_equipment_category ON equipment_phase1(category);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment_phase1(status);
CREATE INDEX IF NOT EXISTS idx_equipment_next_calibration ON equipment_phase1(next_calibration_due);
CREATE INDEX IF NOT EXISTS idx_calibration_equipment_id ON calibration_records_phase1(equipment_id);
CREATE INDEX IF NOT EXISTS idx_calibration_date ON calibration_records_phase1(calibration_date);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_equipment_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER equipment_update_timestamp
BEFORE UPDATE ON equipment_phase1 FOR EACH ROW
EXECUTE FUNCTION update_equipment_timestamp();

-- Create trigger to auto-UPDATE equipment_phase1 status based on calibration
CREATE OR REPLACE FUNCTION check_calibration_status()
RETURNS TRIGGER AS $$
BEGIN
    -- UPDATE equipment_phase1 last calibration date
    UPDATE equipment_phase1
    SET last_calibration_date = NEW.calibration_date,
        next_calibration_due = NEW.calibration_due_date,
        status = CASE
            WHEN NEW.calibration_result = 'Pass' AND NEW.calibration_due_date > CURRENT_DATE THEN 'Active'
            WHEN NEW.calibration_result = 'Pass' AND NEW.calibration_due_date <= CURRENT_DATE THEN 'Calibration Due'
            WHEN NEW.calibration_result IN ('Fail', 'Conditional Pass') THEN 'Under Maintenance'
            ELSE status
        END
    WHERE id = NEW.equipment_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calibration_status_update
AFTER INSERT ON calibration_records_phase1
FOR EACH ROW
EXECUTE FUNCTION check_calibration_status();

-- Seed initial equipment data
INSERT INTO equipment_phase1 (equipment_id, name, category, manufacturer, model_number, location, status, calibration_frequency_days, created_by)
VALUES
    ('EQP-001', 'Solar Simulator AAA Class', 'Testing Equipment', 'Pasan', 'HighLIGHT LED+', 'Testing Lab 1', 'Active', 365, 'System'),
    ('EQP-002', 'IV Curve Tracer', 'Testing Equipment', 'Keysight', 'B2900A', 'Testing Lab 1', 'Active', 365, 'System'),
    ('EQP-003', 'EL Camera System', 'Imaging Equipment', 'BT Imaging', 'LIS-R1', 'Imaging Lab', 'Active', 180, 'System'),
    ('EQP-004', 'IR Thermal Camera', 'Imaging Equipment', 'FLIR', 'T1020', 'Imaging Lab', 'Active', 365, 'System'),
    ('EQP-005', 'Climate Chamber 1000L', 'Environmental Testing', 'Espec', 'SH-641', 'Climate Test Bay', 'Active', 180, 'System'),
    ('EQP-006', 'UV Weathering Chamber', 'Environmental Testing', 'Q-Lab', 'QUV/se', 'Climate Test Bay', 'Active', 180, 'System'),
    ('EQP-007', 'Multimeter (Calibrated)', 'Measurement Device', 'Fluke', '87V', 'Testing Lab 1', 'Active', 365, 'System'),
    ('EQP-008', 'Reference Cell (c-Si)', 'Calibration Standard', 'Newport', 'PV-100', 'Calibration Lab', 'Active', 180, 'System')
ON CONFLICT (equipment_id) DO NOTHING;

-- Create view for equipment with upcoming calibrations
CREATE OR REPLACE VIEW equipment_calibration_status AS
SELECT
    e.id,
    e.equipment_id,
    e.name,
    e.category,
    e.status,
    e.last_calibration_date,
    e.next_calibration_due,
    e.calibration_frequency_days,
    CASE
        WHEN e.next_calibration_due IS NULL THEN 'No Calibration Data'
        WHEN e.next_calibration_due < CURRENT_DATE THEN 'Overdue'
        WHEN e.next_calibration_due <= CURRENT_DATE + INTERVAL '30 days' THEN 'Due Soon'
        ELSE 'Current'
    END AS calibration_status,
    e.next_calibration_due - CURRENT_DATE AS days_until_due
FROM equipment_phase1 e
WHERE e.status != 'Retired'
ORDER BY e.next_calibration_due ASC NULLS LAST;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON equipment TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON calibration_records_phase1 TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;


COMMIT;
