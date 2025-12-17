-- =================================================================
-- Migration 003: User Roles - DOWN Migration
-- Description: Rollback role-based access control columns
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop trigger
DROP TRIGGER IF EXISTS role_permissions_update_timestamp ON role_permissions;
DROP FUNCTION IF EXISTS update_role_permissions_timestamp() CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_user_role_history_changed_at;
DROP INDEX IF EXISTS idx_user_role_history_user;
DROP INDEX IF EXISTS idx_role_permissions_name;
DROP INDEX IF EXISTS idx_users_can_approve;
DROP INDEX IF EXISTS idx_users_access_level;
DROP INDEX IF EXISTS idx_users_supervisor;

-- Drop tables
DROP TABLE IF EXISTS user_role_history CASCADE;
DROP TABLE IF EXISTS role_permissions CASCADE;

-- Remove columns from users table
ALTER TABLE users DROP COLUMN IF EXISTS signature_date;
ALTER TABLE users DROP COLUMN IF EXISTS signature;
ALTER TABLE users DROP COLUMN IF EXISTS can_approve;
ALTER TABLE users DROP COLUMN IF EXISTS allowed_equipment;
ALTER TABLE users DROP COLUMN IF EXISTS allowed_protocols;
ALTER TABLE users DROP COLUMN IF EXISTS access_level;
ALTER TABLE users DROP COLUMN IF EXISTS role_assigned_by;
ALTER TABLE users DROP COLUMN IF EXISTS role_assigned_at;
ALTER TABLE users DROP COLUMN IF EXISTS supervisor_id;
ALTER TABLE users DROP COLUMN IF EXISTS permissions;

COMMIT;
