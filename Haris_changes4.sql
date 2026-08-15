-- ==============================================================================
-- Haris_changes4.sql
-- Purpose: Enforce Vendor-to-Courier fulfillment business rules at the Database Level
-- 
-- Business Rules:
-- 1. Vendors must mark each order item as 'sent to port'.
-- 2. If any vendor item in an order is still 'pending', the courier cannot update
--    the delivery status to 'on the way' or 'delivered'.
-- ==============================================================================

USE ecommerce;

-- 1. Add item_status column (defaults to 'sent to port' for all existing rows)
ALTER TABLE order_items 
ADD COLUMN IF NOT EXISTS item_status VARCHAR(20) NOT NULL DEFAULT 'sent to port';

-- 2. Set default for all FUTURE order items to 'pending'
ALTER TABLE order_items 
ALTER COLUMN item_status SET DEFAULT 'pending';

-- 3. Add CHECK constraint on item_status (drop first if already created)
ALTER TABLE order_items 
DROP CONSTRAINT IF EXISTS chk_order_item_status;

ALTER TABLE order_items 
ADD CONSTRAINT chk_order_item_status 
CHECK (item_status IN ('pending', 'sent to port', 'on the way', 'delivered'));

-- 4. Database Trigger: Block Courier from dispatching or delivering until all vendors have sent items to port
DELIMITER //

DROP TRIGGER IF EXISTS trg_check_vendor_fulfillment_before_delivery_update//

CREATE TRIGGER trg_check_vendor_fulfillment_before_delivery_update
BEFORE UPDATE ON delivery
FOR EACH ROW
BEGIN
    DECLARE pending_items_count INT DEFAULT 0;

    -- If courier attempts to move status to 'on the way' or 'delivered'
    IF NEW.delivery_status IN ('on the way', 'delivered') THEN
        SELECT COUNT(*) INTO pending_items_count
        FROM order_items
        WHERE order_id = NEW.order_id 
          AND item_status = 'pending';

        IF pending_items_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Dispatch blocked: One or more vendor items in this order have not been sent to the port yet.';
        END IF;
    END IF;
END//

DELIMITER ;
