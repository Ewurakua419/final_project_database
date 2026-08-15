DROP VIEW IF EXISTS vw_vendor_sales;

CREATE VIEW vw_vendor_sales AS
SELECT
    v.vendor_id,
    v.vendor_name,
    COUNT(DISTINCT p.product_id) AS number_of_products,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(SUM(oi.quantity * p.price), 0) AS total_revenue
FROM Vendor v
LEFT JOIN Product p
    ON v.vendor_id = p.vendor_id
LEFT JOIN Order_Items oi
    ON p.product_id = oi.product_id
LEFT JOIN Orders o
    ON oi.order_id = o.order_id
GROUP BY
    v.vendor_id,
    v.vendor_name;