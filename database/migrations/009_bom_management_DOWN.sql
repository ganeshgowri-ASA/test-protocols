-- =================================================================
-- Migration 009: BOM Management - DOWN Migration
-- Description: Rollback bill of materials and inventory tracking
-- Created: 2025-12-17
-- Author: Claude Assistant
-- Version: 1.0.0
-- =================================================================

-- Drop triggers and functions
DROP TRIGGER IF EXISTS bom_items_update_timestamp ON bom_items;
DROP FUNCTION IF EXISTS update_bom_items_timestamp() CASCADE;
DROP FUNCTION IF EXISTS check_bom_stock_levels() CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_bom_stock_alerts_type;
DROP INDEX IF EXISTS idx_bom_stock_alerts_item;
DROP INDEX IF EXISTS idx_bom_purchase_orders_status;
DROP INDEX IF EXISTS idx_bom_purchase_orders_number;
DROP INDEX IF EXISTS idx_bom_suppliers_active;
DROP INDEX IF EXISTS idx_bom_suppliers_code;
DROP INDEX IF EXISTS idx_bom_inventory_trans_date;
DROP INDEX IF EXISTS idx_bom_inventory_trans_type;
DROP INDEX IF EXISTS idx_bom_inventory_trans_item;
DROP INDEX IF EXISTS idx_bom_usage_log_date;
DROP INDEX IF EXISTS idx_bom_usage_log_test;
DROP INDEX IF EXISTS idx_bom_usage_log_item;
DROP INDEX IF EXISTS idx_bom_protocol_req_item;
DROP INDEX IF EXISTS idx_bom_protocol_req_protocol;
DROP INDEX IF EXISTS idx_bom_items_active;
DROP INDEX IF EXISTS idx_bom_items_category;
DROP INDEX IF EXISTS idx_bom_items_type;
DROP INDEX IF EXISTS idx_bom_items_code;

-- Drop tables
DROP TABLE IF EXISTS bom_stock_alerts CASCADE;
DROP TABLE IF EXISTS bom_purchase_orders CASCADE;
DROP TABLE IF EXISTS bom_suppliers CASCADE;
DROP TABLE IF EXISTS bom_inventory_transactions CASCADE;
DROP TABLE IF EXISTS bom_usage_log CASCADE;
DROP TABLE IF EXISTS bom_protocol_requirements CASCADE;
DROP TABLE IF EXISTS bom_items CASCADE;

COMMIT;
