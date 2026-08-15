-- final_changes.sql
-- Safely migrates historical cart items into Order_Items without deducting current active stock.

-- 1. Drop the stock trigger temporarily
DROP TRIGGER IF EXISTS trg_reduce_stock_after_order_item;

-- 2. Explicitly insert the 60 historical Order_Items
INSERT IGNORE INTO Order_Items (product_id, order_id, quantity, added_date) VALUES
    ('PROD01', 'ORD01', 1, '2026-08-01'),
    ('PROD02', 'ORD01', 2, '2026-08-01'),
    ('PROD03', 'ORD02', 1, '2026-08-01'),
    ('PROD04', 'ORD02', 2, '2026-08-01'),
    ('PROD05', 'ORD03', 1, '2026-08-01'),
    ('PROD06', 'ORD03', 2, '2026-08-01'),
    ('PROD07', 'ORD04', 1, '2026-08-01'),
    ('PROD08', 'ORD04', 2, '2026-08-01'),
    ('PROD09', 'ORD05', 1, '2026-08-01'),
    ('PROD10', 'ORD05', 2, '2026-08-01'),
    ('PROD11', 'ORD06', 1, '2026-08-01'),
    ('PROD12', 'ORD06', 2, '2026-08-01'),
    ('PROD13', 'ORD07', 1, '2026-08-01'),
    ('PROD14', 'ORD07', 2, '2026-08-01'),
    ('PROD15', 'ORD08', 1, '2026-08-01'),
    ('PROD16', 'ORD08', 2, '2026-08-01'),
    ('PROD17', 'ORD09', 1, '2026-08-01'),
    ('PROD18', 'ORD09', 2, '2026-08-01'),
    ('PROD19', 'ORD10', 1, '2026-08-01'),
    ('PROD20', 'ORD10', 2, '2026-08-01'),
    ('PROD21', 'ORD11', 1, '2026-08-01'),
    ('PROD22', 'ORD11', 2, '2026-08-01'),
    ('PROD23', 'ORD12', 1, '2026-08-01'),
    ('PROD24', 'ORD12', 2, '2026-08-01'),
    ('PROD25', 'ORD13', 1, '2026-08-01'),
    ('PROD26', 'ORD13', 2, '2026-08-01'),
    ('PROD27', 'ORD14', 1, '2026-08-01'),
    ('PROD28', 'ORD14', 2, '2026-08-01'),
    ('PROD29', 'ORD15', 1, '2026-08-01'),
    ('PROD30', 'ORD15', 2, '2026-08-01'),
    ('PROD01', 'ORD16', 1, '2026-08-01'),
    ('PROD02', 'ORD16', 2, '2026-08-01'),
    ('PROD03', 'ORD17', 1, '2026-08-01'),
    ('PROD04', 'ORD17', 2, '2026-08-01'),
    ('PROD05', 'ORD18', 1, '2026-08-01'),
    ('PROD06', 'ORD18', 2, '2026-08-01'),
    ('PROD07', 'ORD19', 1, '2026-08-01'),
    ('PROD08', 'ORD19', 2, '2026-08-01'),
    ('PROD09', 'ORD20', 1, '2026-08-01'),
    ('PROD10', 'ORD20', 2, '2026-08-01'),
    ('PROD11', 'ORD21', 1, '2026-08-01'),
    ('PROD12', 'ORD21', 2, '2026-08-01'),
    ('PROD13', 'ORD22', 1, '2026-08-01'),
    ('PROD14', 'ORD22', 2, '2026-08-01'),
    ('PROD15', 'ORD23', 1, '2026-08-01'),
    ('PROD16', 'ORD23', 2, '2026-08-01'),
    ('PROD17', 'ORD24', 1, '2026-08-01'),
    ('PROD18', 'ORD24', 2, '2026-08-01'),
    ('PROD19', 'ORD25', 1, '2026-08-01'),
    ('PROD20', 'ORD25', 2, '2026-08-01'),
    ('PROD21', 'ORD26', 1, '2026-08-01'),
    ('PROD22', 'ORD26', 2, '2026-08-01'),
    ('PROD23', 'ORD27', 1, '2026-08-01'),
    ('PROD24', 'ORD27', 2, '2026-08-01'),
    ('PROD25', 'ORD28', 1, '2026-08-01'),
    ('PROD26', 'ORD28', 2, '2026-08-01'),
    ('PROD27', 'ORD29', 1, '2026-08-01'),
    ('PROD28', 'ORD29', 2, '2026-08-01'),
    ('PROD29', 'ORD30', 1, '2026-08-01'),
    ('PROD30', 'ORD30', 2, '2026-08-01');

-- 3. DO NOT modify Product.stock_quantity (handled implicitly by dropping trigger)
-- 4. DO NOT delete ambiguous Cart_Items

-- 5. Recreate stock trigger exactly as in Haris_changes.sql
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
