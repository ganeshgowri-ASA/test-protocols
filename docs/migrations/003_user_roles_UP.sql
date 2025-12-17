-- =================================================================
-- Migration 003: User Roles - UP Migration
-- Description: Add role-based access control columns
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Add additional role-related columns to users table
DO $$
BEGIN
    -- Add permissions JSON column for granular permissions
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'permissions') THEN
        ALTER TABLE users ADD COLUMN permissions JSONB DEFAULT '{}';
    END IF;

    -- Add supervisor_id for role hierarchy
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'supervisor_id') THEN
        ALTER TABLE users ADD COLUMN supervisor_id INTEGER REFERENCES users(id);
    END IF;

    -- Add role_assigned_at timestamp
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'role_assigned_at') THEN
        ALTER TABLE users ADD COLUMN role_assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;

    -- Add role_assigned_by for audit
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'role_assigned_by') THEN
        ALTER TABLE users ADD COLUMN role_assigned_by INTEGER REFERENCES users(id);
    END IF;

    -- Add access_level for document/data access control
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'access_level') THEN
        ALTER TABLE users ADD COLUMN access_level VARCHAR(20) DEFAULT 'standard';
    END IF;

    -- Add allowed_protocols for protocol-level access
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'allowed_protocols') THEN
        ALTER TABLE users ADD COLUMN allowed_protocols JSONB DEFAULT '[]';
    END IF;

    -- Add allowed_equipment for equipment-level access
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'allowed_equipment') THEN
        ALTER TABLE users ADD COLUMN allowed_equipment JSONB DEFAULT '[]';
    END IF;

    -- Add can_approve for approval workflow permissions
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'can_approve') THEN
        ALTER TABLE users ADD COLUMN can_approve BOOLEAN DEFAULT FALSE;
    END IF;

    -- Add signature for digital signature storage
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'signature') THEN
        ALTER TABLE users ADD COLUMN signature TEXT;
    END IF;

    -- Add signature_date
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'signature_date') THEN
        ALTER TABLE users ADD COLUMN signature_date TIMESTAMP;
    END IF;
END $$;

-- Create role_permissions table for predefined role permissions
CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    permissions JSONB NOT NULL DEFAULT '{}',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_role_history table for audit trail
CREATE TABLE IF NOT EXISTS user_role_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    previous_role VARCHAR(50),
    new_role VARCHAR(50) NOT NULL,
    changed_by_id INTEGER REFERENCES users(id),
    reason TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_supervisor ON users(supervisor_id);
CREATE INDEX IF NOT EXISTS idx_users_access_level ON users(access_level);
CREATE INDEX IF NOT EXISTS idx_users_can_approve ON users(can_approve);
CREATE INDEX IF NOT EXISTS idx_role_permissions_name ON role_permissions(role_name);
CREATE INDEX IF NOT EXISTS idx_user_role_history_user ON user_role_history(user_id);
CREATE INDEX IF NOT EXISTS idx_user_role_history_changed_at ON user_role_history(changed_at);

-- Insert default role permissions
INSERT INTO role_permissions (role_name, permissions, description) VALUES
    ('admin', '{"all": true, "manage_users": true, "manage_equipment": true, "approve_tests": true, "generate_reports": true, "manage_documents": true}', 'Full system access'),
    ('supervisor', '{"approve_tests": true, "generate_reports": true, "manage_samples": true, "view_all": true}', 'Supervisory access with approval rights'),
    ('technician', '{"execute_tests": true, "manage_samples": true, "view_assigned": true}', 'Standard technician access'),
    ('viewer', '{"view_reports": true, "view_samples": true}', 'Read-only access')
ON CONFLICT (role_name) DO NOTHING;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_role_permissions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS role_permissions_update_timestamp ON role_permissions;
CREATE TRIGGER role_permissions_update_timestamp
BEFORE UPDATE ON role_permissions
FOR EACH ROW
EXECUTE FUNCTION update_role_permissions_timestamp();

COMMIT;
