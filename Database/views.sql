

USE ecommerce;

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
    CASE WHEN oi.is_dispatched THEN 'in port' ELSE 'pending' END AS item_status,
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
    CASE WHEN oi.is_dispatched THEN 'in port' ELSE 'pending' END AS item_status,
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



