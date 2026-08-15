-- my changes (Haris)

-- 1
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
FROM Product p
LEFT JOIN Order_Items oi
    ON p.product_id = oi.product_id
GROUP BY
    p.product_id,
    p.vendor_id,
    p.product_name,
    p.price,
    p.stock_quantity;
    
-- 2

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

FROM Product p

JOIN Vendor v
    ON p.vendor_id = v.vendor_id

LEFT JOIN (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * p.price) AS total_revenue
    FROM Order_Items oi
    JOIN Product p
        ON oi.product_id = p.product_id
    GROUP BY oi.product_id
) s
    ON p.product_id = s.product_id

LEFT JOIN (
    SELECT
        product_id,
        ROUND(AVG(rating), 2) AS average_rating,
        COUNT(review_id) AS number_of_reviews
    FROM Review
    GROUP BY product_id
) r
    ON p.product_id = r.product_id;
    
-- 3
DROP TRIGGER IF EXISTS trg_reduce_stock_after_order;
DROP TRIGGER IF EXISTS trg_reduce_stock_after_order_item;

DELIMITER //

CREATE TRIGGER trg_reduce_stock_after_order_item
AFTER INSERT ON Order_Items
FOR EACH ROW
BEGIN

    UPDATE Product
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;

END //

DELIMITER ;


-- 3
DROP PROCEDURE IF EXISTS sp_place_order;

DELIMITER //

CREATE PROCEDURE sp_place_order(
    IN p_order_id VARCHAR(6),
    IN p_customer_id VARCHAR(6)
)
BEGIN
    DECLARE v_cart_id VARCHAR(6);
    DECLARE v_subtotal DECIMAL(10,2);

    -- Check that the order ID is provided
    IF p_order_id IS NULL OR p_order_id = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order ID is required';
    END IF;

    -- Check that the customer cart exists
    SELECT cart_id
    INTO v_cart_id
    FROM Cart
    WHERE customer_id = p_customer_id
    LIMIT 1;

    IF v_cart_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer cart does not exist';
    END IF;

    -- Check that the cart is not empty
    IF NOT EXISTS (
        SELECT 1
        FROM Cart_Items
        WHERE cart_id = v_cart_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot place an order with an empty cart';
    END IF;
    
    -- Check for duplicate order id
    
    IF EXISTS (
		SELECT 1
		FROM Orders
		WHERE order_id = p_order_id
	) THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Order ID already exists';
	END IF;

    -- Calculate subtotal
    SELECT
        COALESCE(SUM(ci.quantity * p.price), 0)
    INTO v_subtotal
    FROM Cart_Items ci
    JOIN Product p
        ON ci.product_id = p.product_id
    WHERE ci.cart_id = v_cart_id;

    -- Create the order
    INSERT INTO Orders (
        order_id,
        customer_id,
        cart_id,
        order_date,
        subtotal,
        shipping_fee
    )
    VALUES (
        p_order_id,
        p_customer_id,
        v_cart_id,
        CURRENT_TIMESTAMP,
        v_subtotal,
        0
    );

    -- Save the purchased products
    INSERT INTO Order_Items (
        product_id,
        order_id,
        quantity,
        added_date
    )
    SELECT
        product_id,
        p_order_id,
        quantity,
        added_date
    FROM Cart_Items
    WHERE cart_id = v_cart_id;
    
    -- Clear the cart after successfully placing the order
    DELETE FROM Cart_Items
    WHERE cart_id = v_cart_id;

END //

DELIMITER ;


-- 4
ALTER TABLE Delivery
DROP CONSTRAINT chk_delivery_status;

ALTER TABLE Delivery
ADD CONSTRAINT chk_delivery_status
CHECK (
    delivery_status IN (
        'pending',
        'sent to port',
        'on the way',
        'delivered',
        'cancelled'
    )
);


DROP PROCEDURE IF EXISTS sp_update_delivery_status;

DELIMITER //

CREATE PROCEDURE sp_update_delivery_status(
    IN p_delivery_id VARCHAR(6),
    IN p_new_status VARCHAR(20)
)
BEGIN

    IF LOWER(p_new_status) NOT IN (
        'pending',
        'sent to port',
        'on the way',
        'delivered',
        'cancelled'
    ) THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery status';

    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM Delivery
        WHERE delivery_id = p_delivery_id
    ) THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery does not exist';

    END IF;

    UPDATE Delivery
    SET delivery_status = LOWER(p_new_status)
    WHERE delivery_id = p_delivery_id;

END //

DELIMITER ;

-- 5

GRANT SELECT
ON ecommerce.vw_vendor_product_performance
TO marketplace_vendor;

GRANT SELECT
ON ecommerce.vw_product_sales
TO marketplace_vendor;


