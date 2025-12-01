-- ============================================================================
-- PHASE 1: EQUIPMENT MANAGEMENT - UP MIGRATION
-- File: migrations/001_equipment_management_UP.sql
-- Description: Create equipment and equipment_calibration tables
-- Author: Claude Opus 4.5 (Perplexity)
-- Date: 2025-12-01
-- ============================================================================

-- Create equipment table
CREATE TABLE IF NOT EXISTS equipment (
    equipment_id SERIAL PRIMARY KEY,
    equipment_name VARCHAR(255) NOT NULL,
    equipment_code VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(255),
    model_number VARCHAR(100),
    serial_number VARCHAR(100),
    purchase_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    location VARCHAR(255),
    last_calibration_date DATE,
    next_calibration_date DATE,
    calibration_frequency_days INTEGER DEFAULT 365,
    specifications TEXT,
    attachments TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create equipment_calibration table
CREATE TABLE IF NOT EXISTS equipment_calibration (
    calibration_id SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    calibration_date DATE NOT NULL,
    next_calibration_date DATE,
    calibration_status VARCHAR(50) NOT NULL,
    performed_by VARCHAR(255),
    certificate_number VARCHAR(100),
    calibration_agency VARCHAR(255),
    remarks TEXT,
    attachments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_equipment_code ON equipment(equipment_code);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_next_cal_date ON equipment(next_calibration_date);
CREATE INDEX IF NOT EXISTS idx_equipment_calibration_equip_id ON equipment_calibration(equipment_id);

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_equipment_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS set_equipment_updated_at ON equipment;
CREATE TRIGGER set_equipment_updated_at
    BEFORE UPDATE ON equipment
    FOR EACH ROW
    EXECUTE FUNCTION update_equipment_updated_at();

-- Insert seed data (5 equipment records)
INSERT INTO equipment (
    equipment_name, equipment_code, category, manufacturer, model_number,
    serial_number, purchase_date, status, location, last_calibration_date,
    next_calibration_date, calibration_frequency_days, specifications
) VALUES
(
    'Solar Simulator SS-3000',
    'SS-001',
    'Solar Simulator',
    'PASAN',
    'SunSim 3c',
    'SN-SS-2023-001',
    '2023-01-15',
    'Active',
    'Lab 1, Test Bay A',
    '2024-01-15',
    '2025-01-15',
    365,
    'Class AAA, 1000 W/m² irradiance, AM 1.5G spectrum, Temperature control 25°C ± 2°C'
),
(
    'Climate Chamber CC-500',
    'CC-001',
    'Climate Chamber',
    'ESPEC',
    'TSA-71H-W',
    'SN-CC-2023-002',
    '2023-02-20',
    'Active',
    'Lab 2, Environmental Testing',
    '2024-02-20',
    '2025-02-20',
    365,
    'Temperature: -40°C to +150°C, Humidity: 20% to 98% RH, Volume: 500L'
),
(
    'Digital Multimeter DMM-789',
    'DMM-001',
    'Multimeter',
    'Fluke',
    '287',
    'SN-DMM-2023-003',
    '2023-03-10',
    'Active',
    'Lab 1, Measurement Station',
    '2024-09-10',
    '2025-09-10',
    365,
    'True RMS, 4.5 digit resolution, 0.025% accuracy, Voltage/Current/Resistance'
),
(
    'IV Curve Tracer IVT-2000',
    'IVT-001',
    'IV Tracer',
    'PVE',
    'IVT-2000',
    'SN-IVT-2023-004',
    '2023-04-05',
    'Active',
    'Lab 1, IV Testing Station',
    '2024-10-05',
    '2025-10-05',
    365,
    'Max Current: 20A, Max Voltage: 1500V, Accuracy: ±0.5%'
),
(
    'EL Camera System EL-Pro',
    'EL-001',
    'EL Camera',
    'BT Imaging',
    'LumiSolar Pro',
    'SN-EL-2023-005',
    '2023-05-12',
    'Active',
    'Lab 2, Imaging Station',
    '2024-11-12',
    '2025-11-12',
    365,
    'Resolution: 1280x1024, Quantum Efficiency: >40%, Spectral Range: 900-1700nm'
)
ON CONFLICT (equipment_code) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Equipment table created successfully';
    RAISE NOTICE '✅ Equipment calibration table created successfully';
    RAISE NOTICE '✅ Indexes created successfully';
    RAISE NOTICE '✅ Trigger created successfully';
    RAISE NOTICE '✅ Seed data inserted successfully (5 equipment records)';
    RAISE NOTICE '🚀 UP migration completed - Equipment Management ready';
END $$;