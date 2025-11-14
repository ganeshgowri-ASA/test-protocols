-- Test Protocols Schema
-- Database schema for storing test protocol definitions and configurations

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Test Protocols Table
-- Stores protocol definitions loaded from JSON files
CREATE TABLE IF NOT EXISTS test_protocols (
    protocol_id VARCHAR(50) PRIMARY KEY,
    protocol_name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    standard VARCHAR(100),
    category VARCHAR(50) NOT NULL CHECK (category IN ('safety', 'performance', 'reliability', 'environmental', 'mechanical', 'electrical')),
    description TEXT NOT NULL,
    config_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    review_status VARCHAR(20) DEFAULT 'draft' CHECK (review_status IN ('draft', 'review', 'approved', 'deprecated')),
    effective_date DATE,
    next_review_date DATE,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),

    -- Ensure unique protocol_id + version combination
    CONSTRAINT unique_protocol_version UNIQUE (protocol_id, version)
);

-- Create indexes for common queries
CREATE INDEX idx_test_protocols_category ON test_protocols(category);
CREATE INDEX idx_test_protocols_is_active ON test_protocols(is_active);
CREATE INDEX idx_test_protocols_review_status ON test_protocols(review_status);
CREATE INDEX idx_test_protocols_standard ON test_protocols(standard);
CREATE INDEX idx_test_protocols_config_json ON test_protocols USING GIN (config_json);

-- Equipment Table
-- Stores equipment information used in tests
CREATE TABLE IF NOT EXISTS equipment (
    equipment_id VARCHAR(50) PRIMARY KEY,
    equipment_name VARCHAR(255) NOT NULL,
    equipment_type VARCHAR(100),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    specifications JSONB,
    calibration_required BOOLEAN DEFAULT FALSE,
    calibration_interval_days INTEGER,
    last_calibration_date DATE,
    next_calibration_date DATE,
    calibration_certificate_path TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'calibration', 'retired')),
    location VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for equipment
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_equipment_next_calibration ON equipment(next_calibration_date);

-- Protocol Equipment Association Table
-- Links protocols with required equipment
CREATE TABLE IF NOT EXISTS protocol_equipment (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(50) REFERENCES test_protocols(protocol_id) ON DELETE CASCADE,
    equipment_id VARCHAR(50) REFERENCES equipment(equipment_id) ON DELETE RESTRICT,
    required BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_protocol_equipment UNIQUE (protocol_id, equipment_id)
);

CREATE INDEX idx_protocol_equipment_protocol ON protocol_equipment(protocol_id);
CREATE INDEX idx_protocol_equipment_equipment ON protocol_equipment(equipment_id);

-- Test Specimens/Modules Table
-- Stores information about modules or specimens under test
CREATE TABLE IF NOT EXISTS test_specimens (
    specimen_id SERIAL PRIMARY KEY,
    module_id VARCHAR(100) NOT NULL UNIQUE,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    module_type VARCHAR(50),
    power_rating_w NUMERIC(10, 2),
    voltage_rating_v NUMERIC(10, 2),
    current_rating_a NUMERIC(10, 2),
    module_area_m2 NUMERIC(10, 4),
    manufacturing_date DATE,
    received_date DATE,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'testing', 'passed', 'failed', 'quarantine', 'disposed')),
    location VARCHAR(100),
    metadata JSONB,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for test specimens
CREATE INDEX idx_test_specimens_module_id ON test_specimens(module_id);
CREATE INDEX idx_test_specimens_manufacturer ON test_specimens(manufacturer);
CREATE INDEX idx_test_specimens_status ON test_specimens(status);
CREATE INDEX idx_test_specimens_metadata ON test_specimens USING GIN (metadata);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_test_protocols_updated_at
    BEFORE UPDATE ON test_protocols
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equipment_updated_at
    BEFORE UPDATE ON equipment
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_specimens_updated_at
    BEFORE UPDATE ON test_specimens
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE test_protocols IS 'Stores test protocol definitions and configurations';
COMMENT ON TABLE equipment IS 'Stores equipment and calibration information';
COMMENT ON TABLE protocol_equipment IS 'Associates protocols with required equipment';
COMMENT ON TABLE test_specimens IS 'Stores information about test specimens/modules';

COMMENT ON COLUMN test_protocols.config_json IS 'Full protocol configuration in JSON format';
COMMENT ON COLUMN test_protocols.review_status IS 'Current review/approval status of the protocol';
COMMENT ON COLUMN equipment.calibration_interval_days IS 'Number of days between required calibrations';
COMMENT ON COLUMN test_specimens.metadata IS 'Additional specimen metadata in JSON format';
