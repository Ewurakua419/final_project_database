

USE ecommerce;

DELIMITER //

-- trg_check_initial_stock_before_insert
-- Enforces that a product must have at least 1 unit of stock when it is initially created.
DROP TRIGGER IF EXISTS trg_check_initial_stock_before_insert //
CREATE TRIGGER trg_check_initial_stock_before_insert
BEFORE INSERT ON product
FOR EACH ROW
BEGIN
    IF NEW.stock_quantity < 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Initial stock quantity must be at least 1 unit';
    END IF;
END //

-- trg_reduce_stock_after_order_item
-- Deducts stock from Product table automatically after an order item is created.
DROP TRIGGER IF EXISTS trg_reduce_stock_after_order_item //
CREATE TRIGGER trg_reduce_stock_after_order_item
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE product
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END //

-- trg_check_stock
-- Prevents users from adding quantities to cart that exceed available stock.
DROP TRIGGER IF EXISTS trg_check_stock //
CREATE TRIGGER trg_check_stock
BEFORE INSERT ON cart_items
FOR EACH ROW
BEGIN
    DECLARE v_stock INT;
    SELECT stock_quantity INTO v_stock FROM product WHERE product_id = NEW.product_id;

    IF v_stock IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product does not exist';
    END IF;

    IF NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be greater than zero';
    END IF;

    IF NEW.quantity > v_stock THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient product stock';
    END IF;
END //

-- trg_check_stock_onupdate
-- Checks stock limit before updating cart item quantity.
DROP TRIGGER IF EXISTS trg_check_stock_onupdate //
CREATE TRIGGER trg_check_stock_onupdate
BEFORE UPDATE ON cart_items
FOR EACH ROW
BEGIN
    DECLARE v_stock INT;
    SELECT stock_quantity INTO v_stock FROM product WHERE product_id = NEW.product_id;

    IF v_stock IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product does not exist';
    END IF;

    IF NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be greater than zero';
    END IF;

    IF NEW.quantity > v_stock THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient product stock';
    END IF;
END //

-- trg_set_review_date
-- Set review date to current timestamp automatically.
DROP TRIGGER IF EXISTS trg_set_review_date //
CREATE TRIGGER trg_set_review_date
BEFORE INSERT ON review
FOR EACH ROW
BEGIN
    SET NEW.review_date = CURRENT_DATE;
END //

-- trg_auto_update_delivery_status_to_port
-- Automatically transitions delivery status from 'pending' to 'in port' once all vendors dispatch items.
DROP TRIGGER IF EXISTS trg_auto_update_delivery_status_to_port //
CREATE TRIGGER trg_auto_update_delivery_status_to_port
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
    DECLARE v_pending_dispatches INT DEFAULT 0;
    
    -- Count items not yet dispatched in this order
    SELECT COUNT(*) INTO v_pending_dispatches
    FROM order_items
    WHERE order_id = NEW.order_id AND is_dispatched = FALSE;
    
    -- If all items are dispatched, update delivery status to 'in port'
    IF v_pending_dispatches = 0 THEN
        UPDATE delivery 
        SET delivery_status = 'in port' 
        WHERE order_id = NEW.order_id AND delivery_status = 'pending';
    END IF;
END //

-- trg_evict_cart_items_on_soft_delete
-- Automatically evicts items from shopping carts when a product is soft-deleted.
DROP TRIGGER IF EXISTS trg_evict_cart_items_on_soft_delete //
CREATE TRIGGER trg_evict_cart_items_on_soft_delete
AFTER UPDATE ON product
FOR EACH ROW
BEGIN
    IF NEW.is_active = FALSE AND OLD.is_active = TRUE THEN
        DELETE FROM cart_items WHERE product_id = NEW.product_id;
    END IF;
END //

-- trg_on_vendor_status_change
-- Soft-deactivates all vendor products when the vendor is suspended, and reactivates them when the vendor is reactivated.
DROP TRIGGER IF EXISTS trg_on_vendor_status_change //
CREATE TRIGGER trg_on_vendor_status_change
AFTER UPDATE ON vendor
FOR EACH ROW
BEGIN
    IF NEW.is_active = FALSE AND OLD.is_active = TRUE THEN
        UPDATE product SET is_active = FALSE WHERE vendor_id = NEW.vendor_id;
    ELSEIF NEW.is_active = TRUE AND OLD.is_active = FALSE THEN
        UPDATE product SET is_active = TRUE WHERE vendor_id = NEW.vendor_id;
    END IF;
END //

DELIMITER ;

