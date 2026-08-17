-- queries.sql
-- Key Sample Queries for E-commerce Platform

USE ecommerce;

-- 1. Search for a customer by email
SELECT c.customer_id, c.f_name, c.l_name, c.phone_number, c.email, cc.password_hash, c.is_active
FROM customer c 
JOIN customer_credentials cc ON c.customer_id = cc.customer_id 
WHERE LOWER(c.email) = LOWER('kofi.mensah1@email.com');

-- 2. Fetch all active products
SELECT product_id, vendor_id, product_name, description, price, stock_quantity, product_type, image_url 
FROM product
WHERE is_active = TRUE;

-- 3. Retrieve specific fashion attributes for a product
SELECT Color, Material, Size, Gender_category 
FROM fashion 
WHERE product_id = 'some-product-id';

-- 4. Retrieve average rating and review list for a product
SELECT rating, comment, review_date, customer_id 
FROM review 
WHERE product_id = 'some-product-id' 
ORDER BY review_date DESC;

-- 5. Query aggregate delivery statistics from the carrier performance view
SELECT carrier_name, total_deliveries, completed_deliveries, total_shipping_revenue
FROM vw_carrier_performance
WHERE active_deliveries > 0;

-- 6. Monitor platform-wide stats from the admin view
SELECT total_customers, total_vendors, total_orders, platform_gross_merchandise_value
FROM vw_admin_platform_summary;
