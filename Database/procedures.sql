

USE ecommerce;


DELIMITER //

-- Function: fn_calculate_order_total
-- Returns the subtotal + shipping fee for a given order ID.
DROP FUNCTION IF EXISTS fn_calculate_order_total //
CREATE FUNCTION fn_calculate_order_total(
    p_order_id VARCHAR(36)
)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(12,2);
    SELECT COALESCE(subtotal, 0) + COALESCE(shipping_fee, 0)
    INTO v_total
    FROM orders
    WHERE order_id = p_order_id;
    RETURN COALESCE(v_total, 0);
END //

-- Function: fn_get_product_average_rating
-- Returns the average rating for a given product ID.
DROP FUNCTION IF EXISTS fn_get_product_average_rating //
CREATE FUNCTION fn_get_product_average_rating(
    p_product_id VARCHAR(36)
)
RETURNS DECIMAL(3,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_rating DECIMAL(3,2);
    SELECT ROUND(AVG(rating), 2)
    INTO v_rating
    FROM review
    WHERE product_id = p_product_id;
    RETURN COALESCE(v_rating, 0);
END //

DELIMITER ;



DELIMITER //

-- Procedure: sp_add_to_cart
-- Safeguards item quantity insertions relative to real-time warehouse inventory.
DROP PROCEDURE IF EXISTS sp_add_to_cart //
CREATE PROCEDURE sp_add_to_cart(
    IN p_customer_id VARCHAR(36),
    IN p_product_id VARCHAR(36),
    IN p_quantity INT
)
BEGIN
    DECLARE v_cart_id VARCHAR(36);
    DECLARE v_stock INT;
    DECLARE v_existing_quantity INT DEFAULT 0;

    -- Exit handler to rollback transaction on failure
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction failed: sp_add_to_cart aborted';
    END;

    IF p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be greater than zero';
    END IF;

    START TRANSACTION;

    -- Lock the product stock row (Pessimistic Lock)
    SELECT stock_quantity INTO v_stock FROM product WHERE product_id = p_product_id FOR UPDATE;
    IF v_stock IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product does not exist';
    END IF;

    SELECT cart_id INTO v_cart_id FROM cart WHERE customer_id = p_customer_id LIMIT 1;
    IF v_cart_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer cart does not exist';
    END IF;

    SELECT COALESCE(quantity, 0) INTO v_existing_quantity
    FROM cart_items WHERE cart_id = v_cart_id AND product_id = p_product_id;

    IF (v_existing_quantity + p_quantity) > v_stock THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient stock';
    END IF;

    INSERT INTO cart_items (cart_id, product_id, quantity, added_date)
    VALUES (v_cart_id, p_product_id, p_quantity, CURRENT_TIMESTAMP)
    ON DUPLICATE KEY UPDATE quantity = quantity + p_quantity;

    COMMIT;
END //

-- Procedure: sp_place_order
-- Places an order, copies cart items to order items, and clears the cart.
DROP PROCEDURE IF EXISTS sp_place_order //
CREATE PROCEDURE sp_place_order(
    IN p_order_id VARCHAR(36),
    IN p_customer_id VARCHAR(36)
)
BEGIN
    DECLARE v_cart_id VARCHAR(36);
    DECLARE v_subtotal DECIMAL(10,2);

    -- Exit handler to rollback transaction on failure
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction failed: sp_place_order aborted';
    END;

    IF p_order_id IS NULL OR p_order_id = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order ID is required';
    END IF;

    START TRANSACTION;

    -- Lock the customer cart row
    SELECT cart_id INTO v_cart_id FROM cart WHERE customer_id = p_customer_id LIMIT 1 FOR UPDATE;
    IF v_cart_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer cart does not exist';
    END IF;

    -- Lock the cart items to prevent modifications while checkout is in progress
    SELECT product_id FROM cart_items WHERE cart_id = v_cart_id FOR UPDATE;

    IF NOT EXISTS (SELECT 1 FROM cart_items WHERE cart_id = v_cart_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot place an order with an empty cart';
    END IF;
    
    IF EXISTS (SELECT 1 FROM orders WHERE order_id = p_order_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order ID already exists';
    END IF;

    SELECT COALESCE(SUM(ci.quantity * p.price), 0) INTO v_subtotal
    FROM cart_items ci
    JOIN product p ON ci.product_id = p.product_id
    WHERE ci.cart_id = v_cart_id;

    -- Create order
    INSERT INTO orders (order_id, customer_id, order_date, subtotal, shipping_fee)
    VALUES (p_order_id, p_customer_id, CURRENT_TIMESTAMP, v_subtotal, 0);

    -- Copy items to order_items
    INSERT INTO order_items (product_id, order_id, quantity, added_date, is_dispatched)
    SELECT product_id, p_order_id, quantity, added_date, FALSE
    FROM cart_items
    WHERE cart_id = v_cart_id;
    
    -- Clear the cart
    DELETE FROM cart_items WHERE cart_id = v_cart_id;

    COMMIT;
END //

-- Procedure: sp_update_delivery_status
-- Restricts status updates to valid workflow steps.
DROP PROCEDURE IF EXISTS sp_update_delivery_status //
CREATE PROCEDURE sp_update_delivery_status(
    IN p_delivery_id VARCHAR(36),
    IN p_new_status VARCHAR(20)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction failed: sp_update_delivery_status aborted';
    END;

    IF LOWER(p_new_status) NOT IN ('pending', 'in port', 'on the way', 'delivered') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery status';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM delivery WHERE delivery_id = p_delivery_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery does not exist';
    END IF;

    START TRANSACTION;

    UPDATE delivery
    SET delivery_status = LOWER(p_new_status)
    WHERE delivery_id = p_delivery_id;

    COMMIT;
END //

-- Procedure: sp_update_order_item_status
-- Re-mapped to update boolean is_dispatched state in the unified schema.
DROP PROCEDURE IF EXISTS sp_update_order_item_status //
CREATE PROCEDURE sp_update_order_item_status(
    IN p_order_id VARCHAR(36),
    IN p_product_id VARCHAR(36),
    IN p_new_status VARCHAR(20)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction failed: sp_update_order_item_status aborted';
    END;

    IF LOWER(p_new_status) NOT IN ('pending', 'sent to port') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid item status. Allowed: pending, sent to port';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM order_items 
        WHERE order_id = p_order_id AND product_id = p_product_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order item not found';
    END IF;

    START TRANSACTION;

    UPDATE order_items
    SET is_dispatched = (LOWER(p_new_status) = 'sent to port')
    WHERE order_id = p_order_id AND product_id = p_product_id;

    COMMIT;
END //

-- Procedure: sp_delete_customer_address
-- Secure address cleanup checking ownership and resetting delivery historical pointers.
DROP PROCEDURE IF EXISTS sp_delete_customer_address //
CREATE PROCEDURE sp_delete_customer_address(
    IN p_address_id VARCHAR(36),
    IN p_customer_id VARCHAR(36)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction failed: sp_delete_customer_address aborted';
    END;

    IF NOT EXISTS (
        SELECT 1 FROM address 
        WHERE address_id = p_address_id AND customer_id = p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address not found or does not belong to this customer';
    END IF;

    START TRANSACTION;

    UPDATE delivery
    SET address_id = NULL
    WHERE address_id = p_address_id;

    DELETE FROM address
    WHERE address_id = p_address_id AND customer_id = p_customer_id;

    COMMIT;
END //

-- Procedure: sp_add_product_review
-- Secure review submission with rating verification.
DROP PROCEDURE IF EXISTS sp_add_product_review //
CREATE PROCEDURE sp_add_product_review(
    IN p_review_id VARCHAR(36),
    IN p_product_id VARCHAR(36),
    IN p_customer_id VARCHAR(36),
    IN p_rating INT,
    IN p_comment TEXT
)
BEGIN
    IF p_rating < 1 OR p_rating > 5 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Rating must be between 1 and 5 stars';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM product WHERE product_id = p_product_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product does not exist';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM customer WHERE customer_id = p_customer_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer does not exist';
    END IF;

    INSERT INTO review (review_id, product_id, customer_id, rating, comment, review_date)
    VALUES (p_review_id, p_product_id, p_customer_id, p_rating, p_comment, CURRENT_DATE);
END //

DELIMITER ;



