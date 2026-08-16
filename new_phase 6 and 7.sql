-- new_phase 6 and 7.sql
-- Unified Database Roles, Views, Procedures, Functions, and Triggers

USE ecommerce;

-- ==============================================================================
-- 1. ROLES AND PRIVILEGES
-- ==============================================================================

CREATE ROLE IF NOT EXISTS marketplace_admin;
CREATE ROLE IF NOT EXISTS marketplace_vendor;
CREATE ROLE IF NOT EXISTS marketplace_customer;
CREATE ROLE IF NOT EXISTS marketplace_shipping_company;

-- Admin Privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON ecommerce.* TO marketplace_admin;

-- Vendor Privileges
GRANT SELECT ON Product TO marketplace_vendor;
GRANT SELECT ON Fashion TO marketplace_vendor;
GRANT SELECT ON Beauty TO marketplace_vendor;
GRANT INSERT, UPDATE ON Product TO marketplace_vendor;
GRANT INSERT, UPDATE ON Fashion TO marketplace_vendor;
GRANT INSERT, UPDATE ON Beauty TO marketplace_vendor;
GRANT SELECT ON Order_Items TO marketplace_vendor;
GRANT SELECT ON Orders TO marketplace_vendor;

-- Customer Privileges
GRANT SELECT, INSERT, UPDATE ON Cart_Items TO marketplace_customer;
GRANT SELECT, INSERT, UPDATE ON Cart TO marketplace_customer;
GRANT SELECT, INSERT ON Orders TO marketplace_customer;
GRANT SELECT, INSERT ON Order_Items TO marketplace_customer;
GRANT SELECT, INSERT ON Review TO marketplace_customer;
GRANT SELECT, INSERT, UPDATE ON Address TO marketplace_customer;

-- Shipping Company Privileges
-- Address View (restricted column access for delivery privacy)
DROP VIEW IF EXISTS Shipping_Delivery_Address;
CREATE VIEW Shipping_Delivery_Address AS
SELECT address_id, city, Landmark, street_address
FROM Address;

GRANT SELECT ON Shipping_Delivery_Address TO marketplace_shipping_company;
GRANT SELECT, UPDATE ON Delivery TO marketplace_shipping_company;


-- ==============================================================================
-- 2. REPORTING & ANALYTICS VIEWS
-- ==============================================================================

-- 2.1 Carrier Performance View
-- Aggregates delivery volume, active shipments, completed shipments, and revenue per carrier.
DROP VIEW IF EXISTS vw_carrier_performance;
CREATE VIEW vw_carrier_performance AS
SELECT 
    sc.shipping_id,
    sc.name AS carrier_name,
    sc.contact_phone,
    COUNT(d.delivery_id) AS total_deliveries,
    COUNT(CASE WHEN d.delivery_status = 'delivered' THEN 1 END) AS completed_deliveries,
    COUNT(CASE WHEN d.delivery_status != 'delivered' THEN 1 END) AS active_deliveries,
    COALESCE(SUM(o.shipping_fee), 0.00) AS total_shipping_revenue,
    COALESCE(SUM(CASE WHEN d.delivery_status = 'delivered' THEN o.shipping_fee ELSE 0 END), 0.00) AS completed_shipping_revenue
FROM shipping_company sc
LEFT JOIN delivery d ON sc.shipping_id = d.shipping_id
LEFT JOIN orders o ON d.order_id = o.order_id
GROUP BY sc.shipping_id, sc.name, sc.contact_phone;

-- 2.2 Full Canonical Order Details View
-- Consolidates orders, items, products, customers, deliveries, carriers, and payments.
DROP VIEW IF EXISTS vw_order_details_full;
CREATE VIEW vw_order_details_full AS
SELECT 
    o.order_id,
    o.customer_id,
    CONCAT(c.f_name, ' ', c.l_name) AS customer_name,
    c.email AS customer_email,
    c.phone_number AS customer_phone,
    o.order_date,
    o.subtotal AS order_subtotal,
    o.shipping_fee AS order_shipping_fee,
    (o.subtotal + o.shipping_fee) AS order_grand_total,
    
    -- Item Details
    oi.product_id,
    p.product_name,
    p.price AS item_price,
    oi.quantity AS item_quantity,
    (oi.quantity * p.price) AS item_total,
    CASE WHEN oi.is_dispatched THEN 'sent to port' ELSE 'pending' END AS item_status,
    p.vendor_id,
    v.vendor_name,
    
    -- Delivery Details
    d.delivery_id,
    d.delivery_status,
    d.estimated_delivery_date,
    d.shipping_id,
    sc.name AS shipping_company_name,
    
    -- Address Details
    a.address_id,
    a.street_address,
    a.city AS address_city,
    a.Landmark AS address_landmark,
    
    -- Payment Details
    pay.payment_id,
    pay.amount AS payment_amount,
    pay.payment_type,
    pay.payment_date
FROM orders o
JOIN customer c ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN product p ON oi.product_id = p.product_id
LEFT JOIN vendor v ON p.vendor_id = v.vendor_id
LEFT JOIN delivery d ON o.order_id = d.order_id
LEFT JOIN shipping_company sc ON d.shipping_id = sc.shipping_id
LEFT JOIN address a ON d.address_id = a.address_id
LEFT JOIN payment pay ON o.order_id = pay.order_id;

-- 2.3 Admin Global Platform Summary View
-- Single-query KPI overview for platform health and executive metrics.
DROP VIEW IF EXISTS vw_admin_platform_summary;
CREATE VIEW vw_admin_platform_summary AS
SELECT 
    (SELECT COALESCE(SUM(subtotal), 0.00) FROM orders) AS total_gmv,
    (SELECT COUNT(*) FROM orders) AS total_orders,
    (SELECT COUNT(*) FROM customer) AS total_customers,
    (SELECT COUNT(*) FROM vendor) AS total_vendors,
    (SELECT COUNT(*) FROM shipping_company) AS total_carriers,
    (SELECT COUNT(*) FROM delivery WHERE delivery_status = 'delivered') AS total_completed_deliveries;

-- 2.4 Vendor Order Fulfillment View
-- Granular fulfillment tracker for vendor-specific line items.
DROP VIEW IF EXISTS vw_vendor_order_fulfillment;
CREATE VIEW vw_vendor_order_fulfillment AS
SELECT 
    p.vendor_id,
    v.vendor_name,
    o.order_id,
    o.order_date,
    oi.product_id,
    p.product_name,
    p.price AS unit_price,
    oi.quantity,
    (oi.quantity * p.price) AS total_price,
    CASE WHEN oi.is_dispatched THEN 'sent to port' ELSE 'pending' END AS item_status,
    d.delivery_status AS courier_delivery_status
FROM order_items oi
JOIN product p ON oi.product_id = p.product_id
JOIN vendor v ON p.vendor_id = v.vendor_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN delivery d ON o.order_id = d.order_id;

-- 2.5 Customer Order History View
DROP VIEW IF EXISTS vw_customer_order_history;
CREATE VIEW vw_customer_order_history AS
SELECT
    c.customer_id,
    c.f_name,
    c.l_name,
    o.order_id,
    o.order_date,
    o.subtotal,
    o.shipping_fee
FROM customer c
JOIN orders o ON c.customer_id = o.customer_id;

-- 2.6 Product Ratings View
DROP VIEW IF EXISTS vw_product_ratings;
CREATE VIEW vw_product_ratings AS
SELECT
    p.product_id,
    p.product_name,
    COALESCE(ROUND(AVG(r.rating), 2), 0) AS average_rating,
    COUNT(r.review_id) AS number_of_reviews
FROM product p
LEFT JOIN review r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name;

-- 2.7 Product Sales View (reporting from order_items instead of cart_items)
DROP VIEW IF EXISTS vw_product_sales;
CREATE VIEW vw_product_sales AS
SELECT
    p.product_id,
    p.vendor_id,
    p.product_name,
    p.price,
    p.stock_quantity,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(SUM(oi.quantity * p.price), 0) AS total_revenue
FROM product p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.vendor_id, p.product_name, p.price, p.stock_quantity;

-- 2.8 Vendor Sales View
DROP VIEW IF EXISTS vw_vendor_sales;
CREATE VIEW vw_vendor_sales AS
SELECT
    v.vendor_id,
    v.vendor_name,
    COUNT(DISTINCT p.product_id) AS number_of_products,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(SUM(oi.quantity * p.price), 0) AS total_revenue
FROM vendor v
LEFT JOIN product p ON v.vendor_id = p.vendor_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY v.vendor_id, v.vendor_name;

-- 2.9 Delivery Status View
DROP VIEW IF EXISTS vw_delivery_status;
CREATE VIEW vw_delivery_status AS
SELECT
    d.delivery_id,
    o.order_id,
    c.customer_id,
    c.f_name,
    c.l_name,
    sc.shipping_id,
    sc.name AS shipping_company_name,
    d.delivery_status,
    d.estimated_delivery_date
FROM delivery d
JOIN orders o ON d.order_id = o.order_id
JOIN customer c ON o.customer_id = c.customer_id
JOIN shipping_company sc ON d.shipping_id = sc.shipping_id;


-- 2.10 Vendor Product Performance View
-- Consolidates products, vendors, sales units, revenue, average ratings, and review counts.
DROP VIEW IF EXISTS vw_vendor_product_performance;
CREATE VIEW vw_vendor_product_performance AS
SELECT
    p.vendor_id,
    v.vendor_name,
    p.product_id,
    p.product_name,
    p.price,
    p.stock_quantity,
    COALESCE(s.units_sold, 0) AS units_sold,
    COALESCE(s.total_revenue, 0) AS total_revenue,
    COALESCE(r.average_rating, 0) AS average_rating,
    COALESCE(r.number_of_reviews, 0) AS number_of_reviews
FROM product p
JOIN vendor v ON p.vendor_id = v.vendor_id
LEFT JOIN (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * prod.price) AS total_revenue
    FROM order_items oi
    JOIN product prod ON oi.product_id = prod.product_id
    GROUP BY oi.product_id
) s ON p.product_id = s.product_id
LEFT JOIN (
    SELECT
        product_id,
        ROUND(AVG(rating), 2) AS average_rating,
        COUNT(review_id) AS number_of_reviews
    FROM review
    GROUP BY product_id
) r ON p.product_id = r.product_id;


-- Grant View Permissions to Vendor Role
GRANT SELECT ON ecommerce.vw_vendor_product_performance TO marketplace_vendor;
GRANT SELECT ON ecommerce.vw_product_sales TO marketplace_vendor;


-- ==============================================================================
-- 3. STORED FUNCTIONS
-- ==============================================================================

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


-- ==============================================================================
-- 4. STORED PROCEDURES
-- ==============================================================================

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
-- Places an order, copies cart items to order items, and clears the cart (decoupled from redundant cart_id inside orders table).
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

    -- Create order (without cart_id column)
    INSERT INTO orders (order_id, customer_id, order_date, subtotal, shipping_fee)
    VALUES (p_order_id, p_customer_id, CURRENT_TIMESTAMP, v_subtotal, 0);

    -- Copy items to order_items (automatically fires trigger to check stock limits and reduce stock!)
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


-- ==============================================================================
-- 5. DATABASE TRIGGERS
-- ==============================================================================

DELIMITER //

-- Trigger: trg_check_initial_stock_before_insert
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

-- Trigger: trg_reduce_stock_after_order_item
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

-- Trigger: trg_check_stock
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

-- Trigger: trg_check_stock_onupdate
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

-- Trigger: trg_set_review_date
-- Set review date to current timestamp automatically.
DROP TRIGGER IF EXISTS trg_set_review_date //
CREATE TRIGGER trg_set_review_date
BEFORE INSERT ON review
FOR EACH ROW
BEGIN
    SET NEW.review_date = CURRENT_DATE;
END //

-- Trigger: trg_auto_update_delivery_status_to_port
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

-- Trigger: trg_evict_cart_items_on_soft_delete
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

-- Trigger: trg_on_vendor_status_change
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
