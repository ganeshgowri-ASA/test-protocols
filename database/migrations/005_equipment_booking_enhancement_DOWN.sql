-- =================================================================
-- Migration 005: Equipment Booking Enhancement - DOWN Migration
-- Description: Rollback recurring booking and conflict detection
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop triggers
DROP TRIGGER IF EXISTS maintenance_schedule_update_timestamp ON equipment_maintenance_schedule;
DROP FUNCTION IF EXISTS update_maintenance_schedule_timestamp() CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS check_booking_conflict(INTEGER, TIMESTAMP, TIMESTAMP, INTEGER) CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_maintenance_schedule_date;
DROP INDEX IF EXISTS idx_maintenance_schedule_equipment;
DROP INDEX IF EXISTS idx_booking_conflicts_conflicting;
DROP INDEX IF EXISTS idx_booking_conflicts_booking;
DROP INDEX IF EXISTS idx_equipment_bookings_status;
DROP INDEX IF EXISTS idx_equipment_bookings_type;
DROP INDEX IF EXISTS idx_equipment_bookings_priority;
DROP INDEX IF EXISTS idx_equipment_bookings_parent;
DROP INDEX IF EXISTS idx_equipment_bookings_recurring;

-- Drop tables
DROP TABLE IF EXISTS equipment_maintenance_schedule CASCADE;
DROP TABLE IF EXISTS booking_conflicts CASCADE;

-- Remove columns from equipment_bookings table
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS reminder_sent;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS notification_sent;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS conflict_override_reason;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS conflict_checked;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS status;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS approved_at;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS approved_by_id;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS approval_required;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS booking_type;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS priority_level;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS parent_booking_id;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS recurrence_end_date;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS recurrence_interval;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS recurrence_pattern;
ALTER TABLE equipment_bookings DROP COLUMN IF EXISTS is_recurring;

COMMIT;
