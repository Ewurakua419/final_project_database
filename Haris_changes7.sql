-- Haris_changes7.sql
-- Database migration to implement product soft delete and active cart cleanup

USE ecommerce;

-- 1. Add is_active column to the product table
ALTER TABLE product ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- 2. Drop the trigger if it exists
DROP TRIGGER IF EXISTS trg_evict_cart_items_on_soft_delete;

-- 3. Create a trigger to automatically evict items from customer carts upon soft deletion
DELIMITER //

CREATE TRIGGER trg_evict_cart_items_on_soft_delete
AFTER UPDATE ON product
FOR EACH ROW
BEGIN
    -- If the product is deactivated (soft deleted), delete it from all customer carts
    IF NEW.is_active = FALSE AND OLD.is_active = TRUE THEN
        DELETE FROM cart_items WHERE product_id = NEW.product_id;
    END IF;
END//

DELIMITER ;
