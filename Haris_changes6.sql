-- Haris_changes6.sql
-- Database migration to simplify vendor/shipping status workflow

USE ecommerce;

-- 1. Clean up old constraints/triggers if they exist
DROP TRIGGER IF EXISTS trg_check_vendor_fulfillment_before_delivery_update;
DROP TRIGGER IF EXISTS trg_sync_item_status_after_delivery_update;
DROP TRIGGER IF EXISTS trg_auto_update_delivery_status_to_port;

-- 2. Modify order_items table: add boolean is_dispatched and migrate data
ALTER TABLE order_items ADD COLUMN IF NOT EXISTS is_dispatched BOOLEAN NOT NULL DEFAULT FALSE;

-- Fix data collision/inconsistencies:
-- If an order is already completed or in transit, make sure all items are marked dispatched
UPDATE order_items oi
JOIN delivery d ON oi.order_id = d.order_id
SET oi.is_dispatched = TRUE
WHERE d.delivery_status IN ('sent to port', 'on the way', 'delivered');

-- Migrate remaining status text data to the new boolean column based on previous state
UPDATE order_items SET is_dispatched = TRUE WHERE item_status = 'sent to port';
UPDATE order_items SET is_dispatched = FALSE WHERE item_status = 'pending';

-- Drop the old item_status column
ALTER TABLE order_items DROP COLUMN IF EXISTS item_status;

-- 3. Update delivery table constraints: restrict delivery_status options
-- Drop existing constraint check first
ALTER TABLE delivery DROP CONSTRAINT IF EXISTS chk_delivery_status;

-- Migrate existing delivery statuses to the new states
UPDATE delivery SET delivery_status = 'in port' WHERE delivery_status = 'sent to port';

-- Set default delivery status for new rows
ALTER TABLE delivery ALTER COLUMN delivery_status SET DEFAULT 'pending';

-- Add check constraint
ALTER TABLE delivery ADD CONSTRAINT chk_delivery_status 
CHECK (delivery_status IN ('pending', 'in port', 'on the way', 'delivered'));

-- 4. Recreate Courier Validation Trigger (BEFORE UPDATE ON delivery)
DELIMITER //

CREATE TRIGGER trg_check_vendor_fulfillment_before_delivery_update
BEFORE UPDATE ON delivery
FOR EACH ROW
BEGIN
    DECLARE pending_items_count INT DEFAULT 0;

    -- Enforce sequential state transitions
    IF NEW.delivery_status = 'delivered' AND OLD.delivery_status != 'on the way' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid sequence: Delivery must be "on the way" before being marked "delivered".';
    END IF;

    -- Block courier transit if any vendor item is not yet dispatched to the port
    IF NEW.delivery_status IN ('on the way', 'delivered') THEN
        SELECT COUNT(*) INTO pending_items_count
        FROM order_items
        WHERE order_id = NEW.order_id 
          AND is_dispatched = FALSE;

        IF pending_items_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Courier blocked: One or more vendor items in this order are still pending dispatch to the port.';
        END IF;
    END IF;
END//

DELIMITER ;

-- 5. Create Auto-sync Trigger (AFTER UPDATE ON order_items)
-- Automatically moves delivery status to 'in port' when all items are dispatched
DELIMITER //

CREATE TRIGGER trg_auto_update_delivery_status_to_port
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
    DECLARE pending_count INT DEFAULT 0;
    
    -- Count pending items for this order
    SELECT COUNT(*) INTO pending_count
    FROM order_items
    WHERE order_id = NEW.order_id AND is_dispatched = FALSE;
    
    -- If all items are dispatched, move delivery from 'pending' to 'in port' (courier pickup ready)
    IF pending_count = 0 THEN
        UPDATE delivery
        SET delivery_status = 'in port'
        WHERE order_id = NEW.order_id AND delivery_status = 'pending';
    END IF;
END//

DELIMITER ;
