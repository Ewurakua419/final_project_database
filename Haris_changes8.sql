-- Haris_changes8.sql
-- Database migration to support customer/vendor deactivation and suspension cascade

USE ecommerce;

-- 1. Add is_active flag to customer table (default is active)
ALTER TABLE customer ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- 2. Add is_active flag to vendor table (default is active)
ALTER TABLE vendor ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- 3. Drop existing trigger if it exists
DROP TRIGGER IF EXISTS trg_on_vendor_status_change;

-- 4. Create trigger to automatically toggle product active status when vendor is suspended/reactivated
DELIMITER //

CREATE TRIGGER trg_on_vendor_status_change
AFTER UPDATE ON vendor
FOR EACH ROW
BEGIN
    -- If a vendor is suspended, deactivate all their products
    -- (This automatically triggers trg_evict_cart_items_on_soft_delete to remove their items from customer carts)
    IF NEW.is_active = FALSE AND OLD.is_active = TRUE THEN
        UPDATE product SET is_active = FALSE WHERE vendor_id = NEW.vendor_id;
        
    -- If a vendor is reactivated, reactivate all their products so they show in catalog again
    ELSEIF NEW.is_active = TRUE AND OLD.is_active = FALSE THEN
        UPDATE product SET is_active = TRUE WHERE vendor_id = NEW.vendor_id;
    END IF;
END//

DELIMITER ;
