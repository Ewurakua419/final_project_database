show databases;
use ecommerce;




CREATE ROLE marketplace_admin;
CREATE ROLE marketplace_vendor;
CREATE ROLE marketplace_customer;
CREATE ROLE marketplace_shipping_company;


GRANT USAGE ON ecommerce.*
TO marketplace_admin;

GRANT SELECT, INSERT, UPDATE, DELETE
ON  ecommerce.*
TO marketplace_admin;



GRANT USAGE ON ecommerce.*
TO marketplace_vendor;

GRANT SELECT ON Product TO marketplace_vendor;
GRANT SELECT ON Fashion TO marketplace_vendor;
GRANT SELECT ON Beauty TO marketplace_vendor;


GRANT INSERT, UPDATE ON Product TO marketplace_vendor;

GRANT INSERT, UPDATE ON Fashion TO marketplace_vendor;

GRANT INSERT, UPDATE ON Beauty TO marketplace_vendor;

GRANT SELECT
ON Order_Items
TO marketplace_vendor;

GRANT SELECT
ON Orders
TO marketplace_vendor;


GRANT USAGE ON ecommerce.*
TO marketplace_customer;



GRANT SELECT, INSERT, UPDATE
ON Cart_Items
TO marketplace_customer;

GRANT SELECT, INSERT, UPDATE
ON Cart
TO marketplace_customer;

GRANT SELECT, INSERT
ON Orders
TO marketplace_customer;

GRANT SELECT, INSERT
ON Order_Items
TO marketplace_customer;

GRANT SELECT, INSERT
ON Review
TO marketplace_customer;

GRANT SELECT, INSERT, UPDATE
ON Address
TO marketplace_customer;




GRANT USAGE ON ecommerce.*
TO marketplace_shipping_company;


CREATE VIEW Shipping_Delivery_Address AS
SELECT
    address_id,
    city , 
	Landmark, street_address

FROM Address;

GRANT SELECT
ON Shipping_Delivery_Address
TO marketplace_shipping_company;







ALTER TABLE cart_items ADD CONSTRAINT uq_cartitem_pk UNIQUE (cart_id, product_id);


show tables;



SELECT
    p.product_id,
    p.product_name,
    SUM(ci.quantity) AS total_units_sold
FROM orders o
JOIN cart_items ci
    ON o.cart_id = ci.cart_id
JOIN product p
    ON ci.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name
ORDER BY total_units_sold DESC;



SELECT
    c.customer_id,
    c.f_name,
    c.l_name,
    SUM(o.subtotal + o.shipping_fee) AS total_spent
FROM Customer c
JOIN Orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.f_name,
    c.l_name
ORDER BY total_spent DESC
LIMIT 1;

SELECT
    v.vendor_id,
    v.vendor_name,
    SUM(ci.quantity * p.price) AS total_revenue
FROM Vendor v
JOIN Product p
    ON v.vendor_id = p.vendor_id
JOIN Cart_Items ci
    ON p.product_id = ci.product_id
JOIN Orders o
    ON ci.cart_id = o.cart_id
GROUP BY
    v.vendor_id,
    v.vendor_name
ORDER BY total_revenue DESC;



SELECT
    p.product_id,
    p.product_name
FROM Product p
WHERE NOT EXISTS (
    SELECT 1
    FROM Cart_Items ci
    JOIN Orders o
        ON ci.cart_id = o.cart_id
    WHERE ci.product_id = p.product_id
);




WITH ProductCategories AS (
    SELECT product_id, 'Fashion' AS category
    FROM Fashion

    UNION ALL

    SELECT product_id, 'Beauty' AS category
    FROM Beauty
)


SELECT
    pc.category,
    SUM(oi.quantity) AS units_sold
FROM ProductCategories pc
JOIN Order_Items oi
    ON pc.product_id = oi.product_id
GROUP BY pc.category
ORDER BY units_sold DESC;


DELIMITER //

CREATE PROCEDURE sp_add_to_cart(
    IN p_customer_id INT,
    IN p_product_id INT,
    IN p_quantity INT
)
BEGIN
    DECLARE v_cart_id INT;
    DECLARE v_stock INT;
    DECLARE v_existing_quantity INT DEFAULT 0;

    IF p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be greater than zero';
    END IF;

    SELECT stock_quantity
    INTO v_stock
    FROM Product
    WHERE product_id = p_product_id;

    IF v_stock IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product does not exist';
    END IF;

    SELECT cart_id
    INTO v_cart_id
    FROM Cart
    WHERE customer_id = p_customer_id
    LIMIT 1;

    IF v_cart_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer cart does not exist';
    END IF;

    SELECT COALESCE(quantity, 0)
    INTO v_existing_quantity
    FROM Cart_Items
    WHERE cart_id = v_cart_id
      AND product_id = p_product_id;

    IF (v_existing_quantity + p_quantity) > v_stock THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient stock';
    END IF;

    INSERT INTO Cart_Items (
        cart_id,
        product_id,
        quantity,
        added_date
    )
    VALUES (
        v_cart_id,
        p_product_id,
        p_quantity,
        CURRENT_TIMESTAMP
    )
    ON DUPLICATE KEY UPDATE
        quantity = quantity + p_quantity;

END //

DELIMITER ;



DELIMITER //

CREATE PROCEDURE sp_place_order(
    IN p_customer_id INT
)
BEGIN
    DECLARE v_cart_id INT;
    DECLARE v_subtotal DECIMAL(12,2);

    SELECT cart_id
    INTO v_cart_id
    FROM Cart
    WHERE customer_id = p_customer_id
    LIMIT 1;

    IF v_cart_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer cart does not exist';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM Cart_Items
        WHERE cart_id = v_cart_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot place an order with an empty cart';
    END IF;

    SELECT
        COALESCE(SUM(ci.quantity * p.price), 0)
    INTO v_subtotal
    FROM Cart_Items ci
    JOIN Product p
        ON ci.product_id = p.product_id
    WHERE ci.cart_id = v_cart_id;

    INSERT INTO Orders (
        customer_id,
        cart_id,
        order_date,
        subtotal,
        shipping_fee
    )
    VALUES (
        p_customer_id,
        v_cart_id,
        CURRENT_TIMESTAMP,
        v_subtotal,
        0
    );

END //
DELIMITER ;


DELIMITER //

CREATE PROCEDURE sp_update_delivery_status(
    IN p_delivery_id INT,
    IN p_new_status VARCHAR(30)
)
BEGIN

    IF UPPER(p_new_status) NOT IN (
        'PENDING',
        'SHIPPED',
        'IN_TRANSIT',
        'DELIVERED',
        'CANCELLED'
    ) THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery status';

    END IF;

       IF NOT EXISTS( SELECT * FROM DELIVERY WHERE delivery_id = p_delivery_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery does not exist';
    END IF;


    UPDATE delivery
    SET delivery_status = UPPER(p_new_status)
    WHERE delivery_id = p_delivery_id;

  

END //

DELIMITER ;


DELIMITER //

CREATE FUNCTION fn_calculate_order_total(
    p_order_id INT
)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(12,2);

    SELECT
        COALESCE(subtotal, 0) + COALESCE(shipping_fee, 0)
    INTO v_total
    FROM Orders
    WHERE order_id = p_order_id;

    RETURN COALESCE(v_total, 0);
END //

DELIMITER ;

DELIMITER //

CREATE FUNCTION fn_get_product_average_rating(
    p_product_id INT
)
RETURNS DECIMAL(3,2)
NOT DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_rating DECIMAL(3,2) ;

    SELECT
        ROUND(AVG(rating), 2)
    INTO v_rating
    FROM Review
    WHERE product_id = p_product_id;

    RETURN COALESCE(v_rating, 0);
END //

DELIMITER ;




DELIMITER //

CREATE TRIGGER trg_check_stock
BEFORE INSERT ON Cart_Items
FOR EACH ROW
BEGIN
    DECLARE v_stock INT ;

    SELECT stock_quantity
    INTO v_stock
    FROM Product
    WHERE product_id = NEW.product_id;

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

DELIMITER ;

DELIMITER //;
CREATE TRIGGER trg_check_stock_onupdate
BEFORE UPDATE ON Cart_Items
FOR EACH ROW
BEGIN
    DECLARE v_stock INT ;

    SELECT stock_quantity
    INTO v_stock
    FROM Product
    WHERE product_id = NEW.product_id;

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

DELIMITER ;



DELIMITER //

CREATE TRIGGER trg_reduce_stock_after_order
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN

    UPDATE Product p
    JOIN Cart_Items ci
        ON p.product_id = ci.product_id
    SET p.stock_quantity =
        p.stock_quantity - ci.quantity
    WHERE ci.cart_id = NEW.cart_id;

END //

DELIMITER ;




DELIMITER //

CREATE TRIGGER trg_set_review_date
BEFORE INSERT ON Review
FOR EACH ROW
BEGIN
    SET NEW.review_date = CURRENT_TIMESTAMP;
END //

DELIMITER ;



CREATE VIEW vw_customer_order_history AS
SELECT
    c.customer_id,
    c.f_name,
    c.l_name,
    o.order_id,
    o.order_date,
    o.subtotal,
    o.shipping_fee
FROM Customer c
JOIN Orders o
    ON c.customer_id = o.customer_id;



CREATE VIEW vw_product_sales AS
SELECT
    p.product_id,
    p.product_name,
    COALESCE(SUM(ci.quantity), 0) AS units_sold,
    COALESCE(
        SUM(ci.quantity * p.price),
        0
    ) AS total_revenue
FROM Product p
JOIN Cart_Items ci
    ON p.product_id = ci.product_id
JOIN Orders o
    ON ci.cart_id = o.cart_id
GROUP BY
    p.product_id,
    p.product_name;



CREATE VIEW vw_vendor_sales AS
SELECT
    v.vendor_id,
    v.vendor_name,
    COUNT(DISTINCT p.product_id) AS number_of_products,
    COALESCE(SUM(ci.quantity), 0) AS units_sold,
    COALESCE(
        SUM(ci.quantity * p.price),
        0
    ) AS total_revenue
FROM Vendor v
LEFT JOIN Product p
    ON v.vendor_id = p.vendor_id
JOIN Cart_Items ci
    ON p.product_id = ci.product_id
JOIN Orders o
    ON ci.cart_id = o.cart_id
GROUP BY
    v.vendor_id,
    v.vendor_name;


CREATE VIEW vw_product_ratings AS
SELECT
    p.product_id,
    p.product_name,
    COALESCE(ROUND(AVG(r.rating), 2), 0) AS average_rating,
    COUNT(r.review_id) AS number_of_reviews
FROM Product p
LEFT JOIN Review r
    ON p.product_id = r.product_id
GROUP BY
    p.product_id,
    p.product_name;



CREATE VIEW vw_delivery_status AS
SELECT
    d.delivery_id,
    o.order_id,
    c.customer_id,
    c.f_name,
    c.l_name,
    sc.shipping_id,
    sc.name,
    d.delivery_status,
    d.estimated_delivery_date
FROM Delivery d
JOIN Orders o
    ON d.order_id = o.order_id
JOIN Customer c
    ON o.customer_id = c.customer_id
JOIN Shipping_Company sc
    ON d.shipping_id = sc.shipping_id;
