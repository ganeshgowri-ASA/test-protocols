-- ============================================================================
-- Migration: 003_sample_allocation_UP.sql
-- Description: Create sample_allocations table for protocol assignment and resource scheduling
-- Date: 2024-12-04
-- ============================================================================

-- ============================================================================
-- NEW ENUM TYPE: AllocationStatus
-- ============================================================================
CREATE TYPE allocation_status AS ENUM (
    'scheduled',
    'in_progress',
    'completed',
    'cancelled',
    'on_hold'
);

-- ============================================================================
-- TABLE: sample_allocations
-- Purpose: Track allocation of samples to test protocols with resource scheduling
-- ============================================================================
CREATE TABLE IF NOT EXISTS sample_allocations (
    id SERIAL PRIMARY KEY,
    allocation_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Sample and Protocol links
    sample_id INTEGER NOT NULL REFERENCES samples(id),
    protocol_id INTEGER NOT NULL REFERENCES test_protocols(id),
    
    -- Resource allocation
    equipment_id INTEGER REFERENCES equipment(id),
    technician_id INTEGER REFERENCES users(id),
    
    -- Scheduling
    scheduled_start TIMESTAMP NOT NULL,
    scheduled_end TIMESTAMP NOT NULL,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    
    -- Status and priority
    status allocation_status DEFAULT 'scheduled',
    priority INTEGER DEFAULT 2,  -- 1=High, 2=Medium, 3=Low
    
    -- Additional info
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_schedule CHECK (scheduled_end > scheduled_start),
    CONSTRAINT valid_priority CHECK (priority BETWEEN 1 AND 3)
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================
CREATE INDEX idx_allocations_sample ON sample_allocations(sample_id);
CREATE INDEX idx_allocations_protocol ON sample_allocations(protocol_id);
CREATE INDEX idx_allocations_equipment ON sample_allocations(equipment_id);
CREATE INDEX idx_allocations_technician ON sample_allocations(technician_id);
CREATE INDEX idx_allocations_status ON sample_allocations(status);
CREATE INDEX idx_allocations_schedule ON sample_allocations(scheduled_start, scheduled_end);
CREATE INDEX idx_allocations_created_at ON sample_allocations(created_at);

-- ============================================================================
-- COMMENTS for Documentation
-- ============================================================================
COMMENT ON TABLE sample_allocations IS 'Sample allocation to test protocols with resource scheduling';
COMMENT ON COLUMN sample_allocations.allocation_number IS 'Unique allocation identifier (e.g., ALLOC-20241204123456)';
COMMENT ON COLUMN sample_allocations.priority IS '1=High, 2=Medium, 3=Low';
COMMENT ON COLUMN sample_allocations.scheduled_start IS 'Planned start time for the test';
COMMENT ON COLUMN sample_allocations.scheduled_end IS 'Planned end time for the test';
COMMENT ON COLUMN sample_allocations.actual_start IS 'Actual start time when test begins';
COMMENT ON COLUMN sample_allocations.actual_end IS 'Actual end time when test completes';

-- ============================================================================
-- Migration Complete
-- ============================================================================
