-- =================================================================
-- Migration 009: BOM Management - UP Migration
-- Description: Add bill of materials and inventory tracking
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Create bom_items table if not exists
CREATE TABLE IF NOT EXISTS bom_items (
    id SERIAL PRIMARY KEY,
    item_code VARCHAR(50) UNIQUE NOT NULL,

    -- Item details
    name VARCHAR(200) NOT NULL,
    description TEXT,
    item_type VARCHAR(20) DEFAULT 'material', -- material, consumable, equipment, service, labor
    category VARCHAR(50),

    -- Specifications
    specifications JSONB,
    unit VARCHAR(20),

    -- Inventory
    current_stock FLOAT DEFAULT 0,
    minimum_stock FLOAT DEFAULT 0,
    reorder_point FLOAT DEFAULT 0,
    reorder_quantity FLOAT,

    -- Cost tracking
    unit_cost FLOAT DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    cost_center VARCHAR(50),

    -- Supplier info
    supplier_name VARCHAR(100),
    supplier_code VARCHAR(50),
    supplier_part_number VARCHAR(50),
    lead_time_days INTEGER,

    -- Shelf life
    has_expiry BOOLEAN DEFAULT FALSE,
    shelf_life_days INTEGER,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bom_protocol_requirements table if not exists
CREATE TABLE IF NOT EXISTS bom_protocol_requirements (
    id SERIAL PRIMARY KEY,
    protocol_id INTEGER NOT NULL,
    bom_item_id INTEGER NOT NULL REFERENCES bom_items(id) ON DELETE CASCADE,

    -- Requirement details
    quantity_per_test FLOAT NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(protocol_id, bom_item_id)
);

-- Create bom_usage_log table if not exists
CREATE TABLE IF NOT EXISTS bom_usage_log (
    id SERIAL PRIMARY KEY,
    bom_item_id INTEGER NOT NULL REFERENCES bom_items(id) ON DELETE CASCADE,

    -- Usage context
    test_execution_id INTEGER,
    sample_id INTEGER,
    service_request_id INTEGER,

    -- Usage details
    quantity_used FLOAT NOT NULL,
    usage_type VARCHAR(20), -- consumed, returned, wasted

    -- User
    used_by_id INTEGER,

    -- Lot/Batch tracking
    lot_number VARCHAR(50),
    expiry_date TIMESTAMP,

    -- Notes
    notes TEXT,

    -- Timestamp
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bom_inventory_transactions table
CREATE TABLE IF NOT EXISTS bom_inventory_transactions (
    id SERIAL PRIMARY KEY,
    bom_item_id INTEGER NOT NULL REFERENCES bom_items(id) ON DELETE CASCADE,

    -- Transaction details
    transaction_type VARCHAR(20) NOT NULL, -- receipt, issue, adjustment, return, disposal
    quantity FLOAT NOT NULL,
    unit_cost FLOAT,
    total_cost FLOAT,

    -- Reference
    reference_type VARCHAR(50), -- purchase_order, test_execution, inventory_adjustment
    reference_id VARCHAR(50),

    -- Stock levels
    previous_stock FLOAT,
    new_stock FLOAT,

    -- Lot tracking
    lot_number VARCHAR(50),
    expiry_date TIMESTAMP,

    -- Location
    from_location VARCHAR(100),
    to_location VARCHAR(100),

    -- User
    performed_by_id INTEGER,
    approved_by_id INTEGER,

    -- Notes
    reason TEXT,
    notes TEXT,

    -- Timestamps
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bom_suppliers table
CREATE TABLE IF NOT EXISTS bom_suppliers (
    id SERIAL PRIMARY KEY,
    supplier_code VARCHAR(50) UNIQUE NOT NULL,
    supplier_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(50),
    address TEXT,

    -- Qualification
    is_approved BOOLEAN DEFAULT FALSE,
    approval_date TIMESTAMP,
    qualification_documents JSONB DEFAULT '[]',
    next_review_date TIMESTAMP,

    -- Performance
    quality_rating FLOAT,
    delivery_rating FLOAT,
    overall_rating FLOAT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bom_purchase_orders table
CREATE TABLE IF NOT EXISTS bom_purchase_orders (
    id SERIAL PRIMARY KEY,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INTEGER REFERENCES bom_suppliers(id),

    -- Order details
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_delivery_date TIMESTAMP,
    actual_delivery_date TIMESTAMP,

    -- Items (stored as JSON for flexibility)
    items JSONB NOT NULL DEFAULT '[]',

    -- Financials
    subtotal FLOAT DEFAULT 0,
    tax FLOAT DEFAULT 0,
    shipping FLOAT DEFAULT 0,
    total FLOAT DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',

    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- draft, submitted, approved, ordered, partial, received, cancelled

    -- Approval
    requested_by_id INTEGER,
    approved_by_id INTEGER,
    approved_at TIMESTAMP,

    -- Notes
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bom_stock_alerts table
CREATE TABLE IF NOT EXISTS bom_stock_alerts (
    id SERIAL PRIMARY KEY,
    bom_item_id INTEGER NOT NULL REFERENCES bom_items(id) ON DELETE CASCADE,
    alert_type VARCHAR(20) NOT NULL, -- low_stock, expiry_warning, reorder_point
    alert_message TEXT,
    current_stock FLOAT,
    threshold FLOAT,
    expiry_date TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by_id INTEGER,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_bom_items_code ON bom_items(item_code);
CREATE INDEX IF NOT EXISTS idx_bom_items_type ON bom_items(item_type);
CREATE INDEX IF NOT EXISTS idx_bom_items_category ON bom_items(category);
CREATE INDEX IF NOT EXISTS idx_bom_items_active ON bom_items(is_active);
CREATE INDEX IF NOT EXISTS idx_bom_protocol_req_protocol ON bom_protocol_requirements(protocol_id);
CREATE INDEX IF NOT EXISTS idx_bom_protocol_req_item ON bom_protocol_requirements(bom_item_id);
CREATE INDEX IF NOT EXISTS idx_bom_usage_log_item ON bom_usage_log(bom_item_id);
CREATE INDEX IF NOT EXISTS idx_bom_usage_log_test ON bom_usage_log(test_execution_id);
CREATE INDEX IF NOT EXISTS idx_bom_usage_log_date ON bom_usage_log(used_at);
CREATE INDEX IF NOT EXISTS idx_bom_inventory_trans_item ON bom_inventory_transactions(bom_item_id);
CREATE INDEX IF NOT EXISTS idx_bom_inventory_trans_type ON bom_inventory_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_bom_inventory_trans_date ON bom_inventory_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_bom_suppliers_code ON bom_suppliers(supplier_code);
CREATE INDEX IF NOT EXISTS idx_bom_suppliers_active ON bom_suppliers(is_active);
CREATE INDEX IF NOT EXISTS idx_bom_purchase_orders_number ON bom_purchase_orders(po_number);
CREATE INDEX IF NOT EXISTS idx_bom_purchase_orders_status ON bom_purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_bom_stock_alerts_item ON bom_stock_alerts(bom_item_id);
CREATE INDEX IF NOT EXISTS idx_bom_stock_alerts_type ON bom_stock_alerts(alert_type);

-- Create trigger to update bom_items timestamp
CREATE OR REPLACE FUNCTION update_bom_items_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS bom_items_update_timestamp ON bom_items;
CREATE TRIGGER bom_items_update_timestamp
BEFORE UPDATE ON bom_items
FOR EACH ROW
EXECUTE FUNCTION update_bom_items_timestamp();

-- Create function to check stock levels and create alerts
CREATE OR REPLACE FUNCTION check_bom_stock_levels()
RETURNS void AS $$
BEGIN
    -- Create low stock alerts
    INSERT INTO bom_stock_alerts (bom_item_id, alert_type, alert_message, current_stock, threshold)
    SELECT id, 'low_stock',
           'Stock level below minimum: ' || name,
           current_stock, minimum_stock
    FROM bom_items
    WHERE current_stock < minimum_stock
      AND is_active = TRUE
      AND id NOT IN (
          SELECT bom_item_id FROM bom_stock_alerts
          WHERE alert_type = 'low_stock' AND acknowledged = FALSE
      );

    -- Create reorder point alerts
    INSERT INTO bom_stock_alerts (bom_item_id, alert_type, alert_message, current_stock, threshold)
    SELECT id, 'reorder_point',
           'Stock at reorder point: ' || name,
           current_stock, reorder_point
    FROM bom_items
    WHERE current_stock <= reorder_point
      AND reorder_point > 0
      AND is_active = TRUE
      AND id NOT IN (
          SELECT bom_item_id FROM bom_stock_alerts
          WHERE alert_type = 'reorder_point' AND acknowledged = FALSE
      );
END;
$$ LANGUAGE plpgsql;

-- Insert sample BOM categories
INSERT INTO bom_items (item_code, name, item_type, category, unit, minimum_stock, reorder_point, is_active)
VALUES
    ('BOM-CON-001', 'Reference Cell Connector', 'consumable', 'connectors', 'piece', 10, 5, TRUE),
    ('BOM-CAL-001', 'Calibration Gas Standard', 'consumable', 'calibration', 'cylinder', 2, 1, TRUE),
    ('BOM-CLN-001', 'IPA Cleaning Solution', 'consumable', 'cleaning', 'liter', 5, 2, TRUE),
    ('BOM-SAF-001', 'Safety Glasses', 'consumable', 'safety', 'piece', 20, 10, TRUE)
ON CONFLICT (item_code) DO NOTHING;

COMMIT;
