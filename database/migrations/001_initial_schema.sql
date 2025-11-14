-- Migration: 001_initial_schema
-- Description: Initial database schema for PV Testing Protocol Framework
-- Date: 2025-01-14
-- Author: PV Testing Framework

BEGIN;

-- Create protocols table
CREATE TABLE IF NOT EXISTS protocols (
    protocol_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    standards TEXT[],
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author VARCHAR(255),
    tags TEXT[],
    protocol_json JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(protocol_id, version)
);

CREATE INDEX idx_protocols_category ON protocols(category);
CREATE INDEX idx_protocols_active ON protocols(is_active);

-- Create test_runs table
CREATE TABLE IF NOT EXISTS test_runs (
    test_run_id VARCHAR(100) PRIMARY KEY,
    protocol_id VARCHAR(50) NOT NULL REFERENCES protocols(protocol_id),
    protocol_version VARCHAR(20) NOT NULL,
    sample_id VARCHAR(100) NOT NULL,
    operator VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    current_phase VARCHAR(50),
    current_step VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_runs_protocol ON test_runs(protocol_id);
CREATE INDEX idx_test_runs_sample ON test_runs(sample_id);
CREATE INDEX idx_test_runs_status ON test_runs(status);

-- Create measurements table
CREATE TABLE IF NOT EXISTS measurements (
    measurement_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    measurement_type_id VARCHAR(50) NOT NULL,
    measurement_name VARCHAR(255) NOT NULL,
    value NUMERIC NOT NULL,
    unit VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    phase VARCHAR(50),
    step VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurements_test_run ON measurements(test_run_id);
CREATE INDEX idx_measurements_type ON measurements(measurement_type_id);
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp);

-- Create qc_results table
CREATE TABLE IF NOT EXISTS qc_results (
    qc_result_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    criterion_id VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(50) NOT NULL,
    passed BOOLEAN NOT NULL,
    condition JSONB NOT NULL,
    actual_value NUMERIC,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_run_id, criterion_id)
);

CREATE INDEX idx_qc_results_test_run ON qc_results(test_run_id);
CREATE INDEX idx_qc_results_passed ON qc_results(passed);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    note_id SERIAL PRIMARY KEY,
    test_run_id VARCHAR(100) NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(50) NOT NULL,
    note TEXT NOT NULL,
    phase VARCHAR(50),
    step VARCHAR(50),
    author VARCHAR(255)
);

CREATE INDEX idx_notes_test_run ON notes(test_run_id);
CREATE INDEX idx_notes_category ON notes(category);

COMMIT;
