-- =================================================================
-- Migration 008: Training Records - UP Migration
-- Description: Add staff training and certification tracking
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Create staff_training table if not exists
CREATE TABLE IF NOT EXISTS staff_training (
    id SERIAL PRIMARY KEY,
    training_id VARCHAR(50) UNIQUE NOT NULL,

    -- Training details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- safety, equipment, protocol, qms, general
    training_type VARCHAR(50), -- initial, refresher, advanced, certification

    -- Requirements
    required_for_roles JSONB DEFAULT '[]',
    required_for_protocols JSONB DEFAULT '[]',
    prerequisite_trainings JSONB DEFAULT '[]',

    -- Content
    materials_path VARCHAR(200),
    duration_hours FLOAT,
    assessment_required BOOLEAN DEFAULT TRUE,
    passing_score FLOAT DEFAULT 80.0,

    -- Validity
    valid_months INTEGER DEFAULT 12,

    -- Metadata
    created_by_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create staff_training_records table if not exists
CREATE TABLE IF NOT EXISTS staff_training_records (
    id SERIAL PRIMARY KEY,
    record_number VARCHAR(50) UNIQUE NOT NULL,

    -- Links
    training_id INTEGER NOT NULL REFERENCES staff_training(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,

    -- Training session
    scheduled_date TIMESTAMP,
    completion_date TIMESTAMP,
    trainer_id INTEGER,
    trainer_name VARCHAR(100),

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, expired, cancelled

    -- Assessment
    assessment_score FLOAT,
    assessment_passed BOOLEAN,
    assessment_date TIMESTAMP,
    assessment_notes TEXT,

    -- Certificate
    certificate_number VARCHAR(50),
    certificate_path VARCHAR(200),

    -- Validity tracking
    expiry_date TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,

    -- Notes
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create training_sessions table for group training
CREATE TABLE IF NOT EXISTS training_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    training_id INTEGER NOT NULL REFERENCES staff_training(id) ON DELETE CASCADE,

    -- Session details
    session_date TIMESTAMP NOT NULL,
    location VARCHAR(200),
    max_participants INTEGER DEFAULT 20,
    current_participants INTEGER DEFAULT 0,

    -- Trainer
    trainer_id INTEGER,
    trainer_name VARCHAR(100),
    co_trainer_id INTEGER,

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled

    -- Materials
    materials_provided JSONB DEFAULT '[]',

    -- Notes
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create training_attendance table
CREATE TABLE IF NOT EXISTS training_attendance (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,

    -- Attendance
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attended BOOLEAN DEFAULT FALSE,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    attendance_duration_minutes INTEGER,

    -- Assessment (if done during session)
    assessment_completed BOOLEAN DEFAULT FALSE,
    assessment_score FLOAT,

    -- Certificate
    certificate_issued BOOLEAN DEFAULT FALSE,
    certificate_number VARCHAR(50),

    -- Notes
    notes TEXT,

    UNIQUE(session_id, user_id)
);

-- Create training_competencies table
CREATE TABLE IF NOT EXISTS training_competencies (
    id SERIAL PRIMARY KEY,
    competency_code VARCHAR(50) UNIQUE NOT NULL,
    competency_name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),

    -- Requirements
    required_trainings JSONB DEFAULT '[]',
    required_experience_months INTEGER DEFAULT 0,

    -- Assessment
    assessment_criteria JSONB,
    min_score FLOAT DEFAULT 80.0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_competencies table
CREATE TABLE IF NOT EXISTS user_competencies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    competency_id INTEGER NOT NULL REFERENCES training_competencies(id) ON DELETE CASCADE,

    -- Status
    status VARCHAR(20) DEFAULT 'not_started', -- not_started, in_progress, achieved, expired
    achieved_date TIMESTAMP,
    expiry_date TIMESTAMP,

    -- Assessment
    last_assessment_date TIMESTAMP,
    last_assessment_score FLOAT,
    assessor_id INTEGER,

    -- Evidence
    evidence_documents JSONB DEFAULT '[]',

    -- Notes
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, competency_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_staff_training_id ON staff_training(training_id);
CREATE INDEX IF NOT EXISTS idx_staff_training_category ON staff_training(category);
CREATE INDEX IF NOT EXISTS idx_staff_training_active ON staff_training(is_active);
CREATE INDEX IF NOT EXISTS idx_staff_training_records_training ON staff_training_records(training_id);
CREATE INDEX IF NOT EXISTS idx_staff_training_records_user ON staff_training_records(user_id);
CREATE INDEX IF NOT EXISTS idx_staff_training_records_status ON staff_training_records(status);
CREATE INDEX IF NOT EXISTS idx_staff_training_records_expiry ON staff_training_records(expiry_date);
CREATE INDEX IF NOT EXISTS idx_training_sessions_training ON training_sessions(training_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_date ON training_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON training_sessions(status);
CREATE INDEX IF NOT EXISTS idx_training_attendance_session ON training_attendance(session_id);
CREATE INDEX IF NOT EXISTS idx_training_attendance_user ON training_attendance(user_id);
CREATE INDEX IF NOT EXISTS idx_training_competencies_code ON training_competencies(competency_code);
CREATE INDEX IF NOT EXISTS idx_user_competencies_user ON user_competencies(user_id);
CREATE INDEX IF NOT EXISTS idx_user_competencies_competency ON user_competencies(competency_id);
CREATE INDEX IF NOT EXISTS idx_user_competencies_status ON user_competencies(status);

-- Create trigger to update staff_training timestamp
CREATE OR REPLACE FUNCTION update_staff_training_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS staff_training_update_timestamp ON staff_training;
CREATE TRIGGER staff_training_update_timestamp
BEFORE UPDATE ON staff_training
FOR EACH ROW
EXECUTE FUNCTION update_staff_training_timestamp();

DROP TRIGGER IF EXISTS staff_training_records_update_timestamp ON staff_training_records;
CREATE TRIGGER staff_training_records_update_timestamp
BEFORE UPDATE ON staff_training_records
FOR EACH ROW
EXECUTE FUNCTION update_staff_training_timestamp();

-- Create function to check training expiry
CREATE OR REPLACE FUNCTION check_training_expiry()
RETURNS void AS $$
BEGIN
    UPDATE staff_training_records
    SET status = 'expired', is_current = FALSE
    WHERE expiry_date < CURRENT_TIMESTAMP
      AND status = 'completed'
      AND is_current = TRUE;
END;
$$ LANGUAGE plpgsql;

-- Insert default training categories
INSERT INTO staff_training (training_id, title, category, training_type, duration_hours, valid_months, is_active)
VALUES
    ('TRN-SAF-001', 'Laboratory Safety Fundamentals', 'safety', 'initial', 4, 12, TRUE),
    ('TRN-SAF-002', 'Chemical Handling Safety', 'safety', 'initial', 2, 12, TRUE),
    ('TRN-EQP-001', 'Solar Simulator Operation', 'equipment', 'initial', 8, 24, TRUE),
    ('TRN-EQP-002', 'Climate Chamber Operation', 'equipment', 'initial', 6, 24, TRUE),
    ('TRN-QMS-001', 'Quality Management System Introduction', 'qms', 'initial', 4, 24, TRUE),
    ('TRN-QMS-002', 'Document Control Procedures', 'qms', 'initial', 2, 24, TRUE)
ON CONFLICT (training_id) DO NOTHING;

COMMIT;
