-- ==============================================================================
-- Haris_changes5.sql
-- Purpose: Database Refactoring - Advanced Views, Stored Functions, and Procedures
-- Description: Encapsulates complex joins, business logic, revenue calculations,
--              and transactional operations directly inside the MariaDB Engine.
-- ==============================================================================

USE ecommerce;

-- ==============================================================================
-- SECTION 1: DATABASE VIEWS
-- ==============================================================================

-- 1.1 Carrier Performance View
-- Aggregates delivery volume, active shipments, completed shipments, and revenue per carrier.
DROP VIEW IF EXISTS vw_carrier_performance;

CREATE VIEW vw_carrier_performance AS
SELECT 
    sc.shipping_id,
    sc.name AS carrier_name,
    sc.email AS carrier_email,
    sc.contact_phone,
    COUNT(d.delivery_id) AS total_deliveries,
    COUNT(CASE WHEN d.delivery_status = 'delivered' THEN 1 END) AS completed_deliveries,
    COUNT(CASE WHEN d.delivery_status != 'delivered' THEN 1 END) AS active_deliveries,
    COALESCE(SUM(o.shipping_fee), 0.00) AS total_shipping_revenue,
    COALESCE(SUM(CASE WHEN d.delivery_status = 'delivered' THEN o.shipping_fee ELSE 0 END), 0.00) AS completed_shipping_revenue
FROM shipping_company sc
LEFT JOIN delivery d ON sc.shipping_id = d.shipping_id
LEFT JOIN orders o ON d.order_id = o.order_id
GROUP BY sc.shipping_id, sc.name, sc.email, sc.contact_phone;


-- 1.2 Full Canonical Order Details View
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
    oi.item_status,
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


-- 1.3 Admin Global Platform Summary View
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


-- 1.4 Vendor Order Fulfillment View
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
    oi.item_status,
    d.delivery_status AS courier_delivery_status
FROM order_items oi
JOIN product p ON oi.product_id = p.product_id
JOIN vendor v ON p.vendor_id = v.vendor_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN delivery d ON o.order_id = d.order_id;


-- ==============================================================================
-- SECTION 2: STORED FUNCTIONS
-- ==============================================================================

DELIMITER //

-- 2.1 Calculate Total Revenue Earned by a Specific Vendor
DROP FUNCTION IF EXISTS fn_get_vendor_revenue//

CREATE FUNCTION fn_get_vendor_revenue(
    p_vendor_id VARCHAR(6)
)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_revenue DECIMAL(12,2) DEFAULT 0.00;

    SELECT COALESCE(SUM(oi.quantity * p.price), 0.00)
    INTO v_revenue
    FROM order_items oi
    JOIN product p ON oi.product_id = p.product_id
    WHERE p.vendor_id = p_vendor_id;

    RETURN v_revenue;
END//


-- 2.2 Calculate Total Shipping Earnings for a Logistics Partner
DROP FUNCTION IF EXISTS fn_get_carrier_revenue//

CREATE FUNCTION fn_get_carrier_revenue(
    p_shipping_id VARCHAR(6)
)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_carrier_rev DECIMAL(12,2) DEFAULT 0.00;

    SELECT COALESCE(SUM(o.shipping_fee), 0.00)
    INTO v_carrier_rev
    FROM delivery d
    JOIN orders o ON d.order_id = o.order_id
    WHERE d.shipping_id = p_shipping_id;

    RETURN v_carrier_rev;
END//


-- 2.3 Calculate Total Lifetime Spend for a Customer
DROP FUNCTION IF EXISTS fn_customer_lifetime_spend//

CREATE FUNCTION fn_customer_lifetime_spend(
    p_customer_id VARCHAR(6)
)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_spend DECIMAL(12,2) DEFAULT 0.00;

    SELECT COALESCE(SUM(subtotal + shipping_fee), 0.00)
    INTO v_spend
    FROM orders
    WHERE customer_id = p_customer_id;

    RETURN v_spend;
END//


-- 2.4 Get Human-Readable Stock Status of a Product
DROP FUNCTION IF EXISTS fn_product_stock_status//

CREATE FUNCTION fn_product_stock_status(
    p_product_id VARCHAR(6)
)
RETURNS VARCHAR(20)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_stock INT DEFAULT 0;

    SELECT stock_quantity INTO v_stock
    FROM product
    WHERE product_id = p_product_id
    LIMIT 1;

    IF v_stock IS NULL OR v_stock <= 0 THEN
        RETURN 'Out of Stock';
    ELSEIF v_stock <= 5 THEN
        RETURN 'Low Stock';
    ELSE
        RETURN 'In Stock';
    END IF;
END//


-- 2.5 Check if All Items in an Order are Ready at Port
DROP FUNCTION IF EXISTS fn_is_order_ready_for_dispatch//

CREATE FUNCTION fn_is_order_ready_for_dispatch(
    p_order_id VARCHAR(6)
)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_pending_count INT DEFAULT 0;

    SELECT COUNT(*) INTO v_pending_count
    FROM order_items
    WHERE order_id = p_order_id
      AND item_status = 'pending';

    IF v_pending_count = 0 THEN
        RETURN 1; -- Ready for courier dispatch
    ELSE
        RETURN 0; -- Still preparing at vendor
    END IF;
END//

DELIMITER ;


-- ==============================================================================
-- SECTION 3: STORED PROCEDURES
-- ==============================================================================

DELIMITER //

-- 3.1 Update Order Item Fulfillment Status
-- Transitions item_status with constraint validation
DROP PROCEDURE IF EXISTS sp_update_order_item_status//

CREATE PROCEDURE sp_update_order_item_status(
    IN p_order_id VARCHAR(6),
    IN p_product_id VARCHAR(6),
    IN p_new_status VARCHAR(20)
)
BEGIN
    -- Validate status value
    IF LOWER(p_new_status) NOT IN ('pending', 'sent to port', 'on the way', 'delivered') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid item status. Allowed: pending, sent to port, on the way, delivered';
    END IF;

    -- Validate order item existence
    IF NOT EXISTS (
        SELECT 1 FROM order_items 
        WHERE order_id = p_order_id AND product_id = p_product_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order item not found';
    END IF;

    -- Update item status
    UPDATE order_items
    SET item_status = LOWER(p_new_status)
    WHERE order_id = p_order_id AND product_id = p_product_id;
END//


-- 3.2 Secure Customer Address Deletion
-- Verifies ownership and cleans foreign key references safely
DROP PROCEDURE IF EXISTS sp_delete_customer_address//

CREATE PROCEDURE sp_delete_customer_address(
    IN p_address_id VARCHAR(6),
    IN p_customer_id VARCHAR(6)
)
BEGIN
    -- Verify address ownership
    IF NOT EXISTS (
        SELECT 1 FROM address 
        WHERE address_id = p_address_id AND customer_id = p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address not found or does not belong to this customer';
    END IF;

    -- Nullify any historical delivery foreign key references
    UPDATE delivery
    SET address_id = NULL
    WHERE address_id = p_address_id;

    -- Delete address
    DELETE FROM address
    WHERE address_id = p_address_id AND customer_id = p_customer_id;
END//


-- 3.3 Add Product Review
-- Validates rating score (1-5) and records customer review atomically
DROP PROCEDURE IF EXISTS sp_add_product_review//

CREATE PROCEDURE sp_add_product_review(
    IN p_review_id VARCHAR(6),
    IN p_product_id VARCHAR(6),
    IN p_customer_id VARCHAR(6),
    IN p_rating INT,
    IN p_comment TEXT
)
BEGIN
    -- Validate rating range
    IF p_rating < 1 OR p_rating > 5 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Rating must be between 1 and 5 stars';
    END IF;

    -- Validate product existence
    IF NOT EXISTS (SELECT 1 FROM product WHERE product_id = p_product_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product does not exist';
    END IF;

    -- Validate customer existence
    IF NOT EXISTS (SELECT 1 FROM customer WHERE customer_id = p_customer_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer does not exist';
    END IF;

    -- Insert Review
    INSERT INTO review (review_id, product_id, customer_id, rating, comment, review_date)
    VALUES (p_review_id, p_product_id, p_customer_id, p_rating, p_comment, CURRENT_DATE);
END//

DELIMITER ;
