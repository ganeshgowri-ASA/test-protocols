-- =================================================================
-- Migration 005: Equipment Booking Enhancement - UP Migration
-- Description: Add recurring booking and conflict detection
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Add recurring booking columns to equipment_bookings table
DO $$
BEGIN
    -- Add is_recurring for recurring bookings
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'is_recurring') THEN
        ALTER TABLE equipment_bookings ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
    END IF;

    -- Add recurrence_pattern (daily, weekly, monthly)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'recurrence_pattern') THEN
        ALTER TABLE equipment_bookings ADD COLUMN recurrence_pattern VARCHAR(20);
    END IF;

    -- Add recurrence_interval (e.g., every 2 weeks)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'recurrence_interval') THEN
        ALTER TABLE equipment_bookings ADD COLUMN recurrence_interval INTEGER DEFAULT 1;
    END IF;

    -- Add recurrence_end_date
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'recurrence_end_date') THEN
        ALTER TABLE equipment_bookings ADD COLUMN recurrence_end_date TIMESTAMP;
    END IF;

    -- Add parent_booking_id for linked recurring instances
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'parent_booking_id') THEN
        ALTER TABLE equipment_bookings ADD COLUMN parent_booking_id INTEGER REFERENCES equipment_bookings(id);
    END IF;

    -- Add priority_level for conflict resolution
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'priority_level') THEN
        ALTER TABLE equipment_bookings ADD COLUMN priority_level INTEGER DEFAULT 5;
    END IF;

    -- Add booking_type (standard, maintenance, calibration, reserved)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'booking_type') THEN
        ALTER TABLE equipment_bookings ADD COLUMN booking_type VARCHAR(30) DEFAULT 'standard';
    END IF;

    -- Add approval_required flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'approval_required') THEN
        ALTER TABLE equipment_bookings ADD COLUMN approval_required BOOLEAN DEFAULT FALSE;
    END IF;

    -- Add approved_by_id
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'approved_by_id') THEN
        ALTER TABLE equipment_bookings ADD COLUMN approved_by_id INTEGER REFERENCES users(id);
    END IF;

    -- Add approved_at
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'approved_at') THEN
        ALTER TABLE equipment_bookings ADD COLUMN approved_at TIMESTAMP;
    END IF;

    -- Add status for booking workflow
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'status') THEN
        ALTER TABLE equipment_bookings ADD COLUMN status VARCHAR(20) DEFAULT 'pending';
    END IF;

    -- Add conflict_checked flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'conflict_checked') THEN
        ALTER TABLE equipment_bookings ADD COLUMN conflict_checked BOOLEAN DEFAULT FALSE;
    END IF;

    -- Add conflict_override_reason
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'conflict_override_reason') THEN
        ALTER TABLE equipment_bookings ADD COLUMN conflict_override_reason TEXT;
    END IF;

    -- Add notification_sent flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'notification_sent') THEN
        ALTER TABLE equipment_bookings ADD COLUMN notification_sent BOOLEAN DEFAULT FALSE;
    END IF;

    -- Add reminder_sent flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'equipment_bookings' AND column_name = 'reminder_sent') THEN
        ALTER TABLE equipment_bookings ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Create booking_conflicts table for tracking conflicts
CREATE TABLE IF NOT EXISTS booking_conflicts (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES equipment_bookings(id) ON DELETE CASCADE,
    conflicting_booking_id INTEGER NOT NULL REFERENCES equipment_bookings(id) ON DELETE CASCADE,
    conflict_type VARCHAR(50) NOT NULL, -- overlap, maintenance, calibration
    conflict_start TIMESTAMP NOT NULL,
    conflict_end TIMESTAMP NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_method VARCHAR(50),
    resolved_by_id INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create equipment_maintenance_schedule table
CREATE TABLE IF NOT EXISTS equipment_maintenance_schedule (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(50) NOT NULL, -- preventive, corrective, calibration
    scheduled_date TIMESTAMP NOT NULL,
    duration_hours FLOAT DEFAULT 2,
    assigned_to_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    completed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_equipment_bookings_recurring ON equipment_bookings(is_recurring);
CREATE INDEX IF NOT EXISTS idx_equipment_bookings_parent ON equipment_bookings(parent_booking_id);
CREATE INDEX IF NOT EXISTS idx_equipment_bookings_priority ON equipment_bookings(priority_level);
CREATE INDEX IF NOT EXISTS idx_equipment_bookings_type ON equipment_bookings(booking_type);
CREATE INDEX IF NOT EXISTS idx_equipment_bookings_status ON equipment_bookings(status);
CREATE INDEX IF NOT EXISTS idx_booking_conflicts_booking ON booking_conflicts(booking_id);
CREATE INDEX IF NOT EXISTS idx_booking_conflicts_conflicting ON booking_conflicts(conflicting_booking_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_schedule_equipment ON equipment_maintenance_schedule(equipment_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_schedule_date ON equipment_maintenance_schedule(scheduled_date);

-- Create function to check for booking conflicts
CREATE OR REPLACE FUNCTION check_booking_conflict(
    p_equipment_id INTEGER,
    p_start_time TIMESTAMP,
    p_end_time TIMESTAMP,
    p_exclude_booking_id INTEGER DEFAULT NULL
) RETURNS TABLE(
    conflict_booking_id INTEGER,
    conflict_start TIMESTAMP,
    conflict_end TIMESTAMP,
    conflict_type VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        eb.id as conflict_booking_id,
        eb.start_time as conflict_start,
        eb.end_time as conflict_end,
        eb.booking_type::VARCHAR as conflict_type
    FROM equipment_bookings eb
    WHERE eb.equipment_id = p_equipment_id
      AND eb.is_cancelled = FALSE
      AND (p_exclude_booking_id IS NULL OR eb.id != p_exclude_booking_id)
      AND (
          (eb.start_time < p_end_time AND eb.end_time > p_start_time)
      );
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update maintenance schedule timestamp
CREATE OR REPLACE FUNCTION update_maintenance_schedule_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS maintenance_schedule_update_timestamp ON equipment_maintenance_schedule;
CREATE TRIGGER maintenance_schedule_update_timestamp
BEFORE UPDATE ON equipment_maintenance_schedule
FOR EACH ROW
EXECUTE FUNCTION update_maintenance_schedule_timestamp();

COMMIT;
