-- Recovered Product Customizations
USE ecommerce;

INSERT INTO vendor (vendor_id, vendor_name, email, phone_number) VALUES
('VNDR01', 'AfroCentric Boutique', 'info@vndr01.com', '+233209876501'),
('VNDR02', 'Glow & Care Cosmetics', 'info@vndr02.com', '+233209876502'),
('VNDR03', 'Heritage Loom Weavers', 'info@vndr03.com', '+233209876503'),
('VNDR04', 'Organic Glow Cosmetics', 'info@vndr04.com', '+233209876504'),
('VNDR05', 'Kente Kings', 'info@vndr05.com', '+233209876505'),
('VNDR06', 'Ankara Styles House', 'info@vndr06.com', '+233209876506'),
('VNDR07', 'Shea Beauty Organic', 'info@vndr07.com', '+233209876507'),
('VNDR08', 'Nii Cosmetics Ltd', 'info@vndr08.com', '+233209876508'),
('VNDR09', 'Gold Coast Fabrics', 'info@vndr09.com', '+233209876509'),
('VNDR10', 'Akwaaba Fashion Hub', 'info@vndr10.com', '+233209876510');

INSERT INTO fashion (product_id, Color, Material, Size, Gender_category) VALUES
('PROD01', 'Red', 'Cotton', 'M', 'unisex'),('PROD03', 'Blue', 'Silk', 'L', 'unisex'),('PROD05', 'Green', 'Linen', 'XL', 'unisex'),('PROD07', 'Black', 'Polyester', 'S', 'unisex'),('PROD09', 'White', 'Kente Cotton', 'M', 'unisex'),('PROD11', 'Gold', 'Polished Cotton', 'XXL', 'unisex'),('PROD13', 'Purple', 'Cotton', 'L', 'unisex'),('PROD15', 'Yellow', 'Ankara Wax Cotton', 'S', 'unisex'),('PROD17', 'Pink', 'Linen', 'M', 'unisex'),('PROD19', 'Multicolor', 'Silk', 'XL', 'unisex'),('PROD21', 'Blue', 'Cotton', 'S', 'unisex'),('PROD23', 'Black', 'Polyester', 'M', 'unisex'),('PROD25', 'White', 'Linen', 'L', 'unisex'),('PROD27', 'Red', 'Kente Cotton', 'XL', 'unisex'),('PROD29', 'Green', 'Polished Cotton', 'XXL', 'unisex');

INSERT INTO beauty (product_id, skin_type, volume_weight, Is_organic) VALUES
('PROD02', 'Dry', '200ml', TRUE),('PROD04', 'Oily', '200ml', TRUE),('PROD06', 'Sensitive', '200ml', TRUE),('PROD08', 'Combination', '200ml', TRUE),('PROD10', 'All Skin Types', '200ml', TRUE),('PROD12', 'Dry', '200ml', TRUE),('PROD14', 'Oily', '200ml', TRUE),('PROD16', 'Sensitive', '200ml', TRUE),('PROD18', 'Combination', '200ml', TRUE),('PROD20', 'All Skin Types', '200ml', TRUE),('PROD22', 'Dry', '200ml', TRUE),('PROD24', 'Oily', '200ml', TRUE),('PROD26', 'Sensitive', '200ml', TRUE),('PROD28', 'Combination', '200ml', TRUE),('PROD30', 'All Skin Types', '200ml', TRUE);

INSERT INTO cart_items (product_id, cart_id, quantity, added_date) VALUES
('PROD01', 'CRT001', 1, '2026-08-01'),('PROD02', 'CRT001', 2, '2026-08-01'),('PROD03', 'CRT002', 1, '2026-08-01'),('PROD04', 'CRT002', 2, '2026-08-01'),('PROD05', 'CRT003', 1, '2026-08-01'),('PROD06', 'CRT003', 2, '2026-08-01'),('PROD07', 'CRT004', 1, '2026-08-01'),('PROD08', 'CRT004', 2, '2026-08-01'),('PROD09', 'CRT005', 1, '2026-08-01'),('PROD10', 'CRT005', 2, '2026-08-01'),('PROD11', 'CRT006', 1, '2026-08-01'),('PROD12', 'CRT006', 2, '2026-08-01'),('PROD13', 'CRT007', 1, '2026-08-01'),('PROD14', 'CRT007', 2, '2026-08-01'),('PROD15', 'CRT008', 1, '2026-08-01'),('PROD16', 'CRT008', 2, '2026-08-01'),('PROD17', 'CRT009', 1, '2026-08-01'),('PROD18', 'CRT009', 2, '2026-08-01'),('PROD19', 'CRT010', 1, '2026-08-01'),('PROD20', 'CRT010', 2, '2026-08-01'),('PROD21', 'CRT011', 1, '2026-08-01'),('PROD22', 'CRT011', 2, '2026-08-01'),('PROD23', 'CRT012', 1, '2026-08-01'),('PROD24', 'CRT012', 2, '2026-08-01'),('PROD25', 'CRT013', 1, '2026-08-01'),('PROD26', 'CRT013', 2, '2026-08-01'),('PROD27', 'CRT014', 1, '2026-08-01'),('PROD28', 'CRT014', 2, '2026-08-01'),('PROD29', 'CRT015', 1, '2026-08-01'),('PROD30', 'CRT015', 2, '2026-08-01'),('PROD01', 'CRT016', 1, '2026-08-01'),('PROD02', 'CRT016', 2, '2026-08-01'),('PROD03', 'CRT017', 1, '2026-08-01'),('PROD04', 'CRT017', 2, '2026-08-01'),('PROD05', 'CRT018', 1, '2026-08-01'),('PROD06', 'CRT018', 2, '2026-08-01'),('PROD07', 'CRT019', 1, '2026-08-01'),('PROD08', 'CRT019', 2, '2026-08-01'),('PROD09', 'CRT020', 1, '2026-08-01'),('PROD10', 'CRT020', 2, '2026-08-01'),('PROD11', 'CRT021', 1, '2026-08-01'),('PROD12', 'CRT021', 2, '2026-08-01'),('PROD13', 'CRT022', 1, '2026-08-01'),('PROD14', 'CRT022', 2, '2026-08-01'),('PROD15', 'CRT023', 1, '2026-08-01'),('PROD16', 'CRT023', 2, '2026-08-01'),('PROD17', 'CRT024', 1, '2026-08-01'),('PROD18', 'CRT024', 2, '2026-08-01'),('PROD19', 'CRT025', 1, '2026-08-01'),('PROD20', 'CRT025', 2, '2026-08-01'),('PROD21', 'CRT026', 1, '2026-08-01'),('PROD22', 'CRT026', 2, '2026-08-01'),('PROD23', 'CRT027', 1, '2026-08-01'),('PROD24', 'CRT027', 2, '2026-08-01'),('PROD25', 'CRT028', 1, '2026-08-01'),('PROD26', 'CRT028', 2, '2026-08-01'),('PROD27', 'CRT029', 1, '2026-08-01'),('PROD28', 'CRT029', 2, '2026-08-01'),('PROD29', 'CRT030', 1, '2026-08-01'),('PROD30', 'CRT030', 2, '2026-08-01');

INSERT INTO review (review_id, product_id, customer_id, rating, review_date, comment) VALUES
('REV01', 'PROD01', 'CUST00', 5, '2026-08-05', 'Highly functional product'),('REV02', 'PROD03', 'CUST02', 5, '2026-08-05', 'Highly functional product'),('REV03', 'PROD05', 'CUST03', 5, '2026-08-05', 'Highly functional product'),('REV04', 'PROD07', 'CUST04', 5, '2026-08-05', 'Highly functional product'),('REV05', 'PROD09', 'CUST05', 5, '2026-08-05', 'Highly functional product'),('REV06', 'PROD11', 'CUST06', 5, '2026-08-05', 'Highly functional product'),('REV07', 'PROD13', 'CUST07', 5, '2026-08-05', 'Highly functional product'),('REV08', 'PROD15', 'CUST08', 5, '2026-08-05', 'Highly functional product'),('REV09', 'PROD17', 'CUST09', 5, '2026-08-05', 'Highly functional product'),('REV10', 'PROD19', 'CUST10', 5, '2026-08-05', 'Highly functional product'),('REV11', 'PROD21', 'CUST11', 5, '2026-08-05', 'Highly functional product'),('REV12', 'PROD23', 'CUST12', 5, '2026-08-05', 'Highly functional product'),('REV13', 'PROD25', 'CUST13', 5, '2026-08-05', 'Highly functional product'),('REV14', 'PROD27', 'CUST14', 5, '2026-08-05', 'Highly functional product'),('REV15', 'PROD29', 'CUST15', 5, '2026-08-05', 'Highly functional product'),('REV16', 'PROD01', 'CUST16', 5, '2026-08-05', 'Highly functional product'),('REV17', 'PROD03', 'CUST17', 5, '2026-08-05', 'Highly functional product'),('REV18', 'PROD05', 'CUST18', 5, '2026-08-05', 'Highly functional product'),('REV19', 'PROD07', 'CUST19', 5, '2026-08-05', 'Highly functional product'),('REV20', 'PROD09', 'CUST20', 5, '2026-08-05', 'Highly functional product'),('REV21', 'PROD11', 'CUST21', 5, '2026-08-05', 'Highly functional product'),('REV22', 'PROD13', 'CUST22', 5, '2026-08-05', 'Highly functional product'),('REV23', 'PROD15', 'CUST23', 5, '2026-08-05', 'Highly functional product'),('REV24', 'PROD17', 'CUST24', 5, '2026-08-05', 'Highly functional product'),('REV25', 'PROD19', 'CUST25', 5, '2026-08-05', 'Highly functional product'),('REV26', 'PROD21', 'CUST26', 5, '2026-08-05', 'Highly functional product'),('REV27', 'PROD23', 'CUST27', 5, '2026-08-05', 'Highly functional product'),('REV28', 'PROD25', 'CUST28', 5, '2026-08-05', 'Highly functional product'),('REV29', 'PROD27', 'CUST29', 5, '2026-08-05', 'Highly functional product'),('REV30', 'PROD29', 'CUST30', 5, '2026-08-05', 'Highly functional product');

GRANT INSERT, UPDATE ON Product TO marketplace_vendor;

GRANT INSERT, UPDATE ON Fashion TO marketplace_vendor;

GRANT INSERT, UPDATE ON Beauty TO marketplace_vendor;

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

END;

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

END;

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
END;

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

END;

UPDATE product
SET
    vendor_id = 'VNDR06',
    product_name = 'African Print Maxi Dress',
    description = 'Elegant African print maxi dress with a vibrant traditional pattern.',
    price = 280.00,
    stock_quantity = 35,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/1200x/a7/ff/d9/a7ffd957dc9b2933d0c294c5344b1775.jpg'
WHERE product_id = 'PROD01';

UPDATE fashion
SET
    Color = 'Multicolor',
    Material = 'Ankara Wax Cotton',
    Size = 'M',
    Gender_category = 'women'
WHERE product_id = 'PROD01';

UPDATE product
SET
    vendor_id = 'VNDR07',
    product_name = 'Organic Shea Body Cream',
    description = 'Rich moisturizing body cream made with nourishing organic ingredients.',
    price = 95.00,
    stock_quantity = 45,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/736x/a5/37/b9/a537b90cdd4e4f9e51ac8feae6551f45.jpg'
WHERE product_id = 'PROD02';

UPDATE beauty
SET
    skin_type = 'Dry',
    volume_weight = '200ml',
    Is_organic = TRUE
WHERE product_id = 'PROD02';

UPDATE product
SET
    vendor_id = 'VNDR05',
    product_name = 'Royal Kente Fashion Set',
    description = 'Traditional-inspired fashion piece featuring a bold Ghanaian kente pattern.',
    price = 420.00,
    stock_quantity = 20,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/736x/63/8c/35/638c352be65e93ce2ead838b9b371846.jpg'
WHERE product_id = 'PROD03';

UPDATE fashion
SET
    Color = 'Gold',
    Material = 'Kente Cotton',
    Size = 'L',
    Gender_category = 'unisex'
WHERE product_id = 'PROD03';

UPDATE product
SET
    vendor_id = 'VNDR04',
    product_name = 'Glow Facial Moisturizer',
    description = 'Lightweight facial moisturizer designed to leave skin smooth and refreshed.',
    price = 110.00,
    stock_quantity = 60,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/1200x/41/e0/b0/41e0b0e08892590b04d1cc856ce003bd.jpg'
WHERE product_id = 'PROD04';

UPDATE beauty
SET
    skin_type = 'Combination',
    volume_weight = '200ml',
    Is_organic = TRUE
WHERE product_id = 'PROD04';

UPDATE product
SET
    vendor_id = 'VNDR06',
    product_name = 'Ankara Casual Shirt',
    description = 'Stylish casual shirt featuring a colorful Ankara print.',
    price = 185.00,
    stock_quantity = 42,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/1200x/a1/60/f2/a160f2855696ab3b9cdf82391e6c46f9.jpg'
WHERE product_id = 'PROD05';

UPDATE fashion
SET
    Color = 'Blue',
    Material = 'Ankara Wax Cotton',
    Size = 'L',
    Gender_category = 'men'
WHERE product_id = 'PROD05';

UPDATE product
SET
    vendor_id = 'VNDR07',
    product_name = 'Shea Radiance Face Cream',
    description = 'Nourishing facial cream formulated to improve skin moisture and radiance.',
    price = 125.00,
    stock_quantity = 70,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/736x/f9/93/3e/f9933e0f2b0518fb81d4d9b8c7995c8c.jpg'
WHERE product_id = 'PROD06';

UPDATE beauty
SET
    skin_type = 'Sensitive',
    volume_weight = '100ml',
    Is_organic = TRUE
WHERE product_id = 'PROD06';

UPDATE product
SET
    vendor_id = 'VNDR01',
    product_name = 'African Print Casual Wear',
    description = 'Comfortable everyday fashion piece inspired by African patterns.',
    price = 160.00,
    stock_quantity = 55,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/736x/9f/06/b3/9f06b362ed7737fad690f8d33fd23650.jpg'
WHERE product_id = 'PROD07';

UPDATE fashion
SET
    Color = 'Red',
    Material = 'Cotton',
    Size = 'M',
    Gender_category = 'unisex'
WHERE product_id = 'PROD07';

UPDATE product
SET
    vendor_id = 'VNDR08',
    product_name = 'Natural Glow Skin Lotion',
    description = 'Hydrating skin lotion designed for everyday use and a natural glow.',
    price = 90.00,
    stock_quantity = 80,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/736x/32/be/27/32be27daf1cb64aa834b06b883f66191.jpg'
WHERE product_id = 'PROD08';

UPDATE beauty
SET
    skin_type = 'All Skin Types',
    volume_weight = '250ml',
    Is_organic = TRUE
WHERE product_id = 'PROD08';

UPDATE product
SET
    vendor_id = 'VNDR09',
    product_name = 'Gold Coast Traditional Fabric',
    description = 'Premium traditional-inspired fabric suitable for custom clothing.',
    price = 350.00,
    stock_quantity = 28,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/736x/63/94/cd/6394cdacefb4921041077ed7dc797fa1.jpg'
WHERE product_id = 'PROD09';

UPDATE fashion
SET
    Color = 'Gold',
    Material = 'Kente Cotton',
    Size = 'XL',
    Gender_category = 'unisex'
WHERE product_id = 'PROD09';

UPDATE product
SET
    vendor_id = 'VNDR04',
    product_name = 'Organic Beauty Facial Cream',
    description = 'Gentle organic facial cream suitable for daily skincare routines.',
    price = 105.00,
    stock_quantity = 65,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/1200x/d0/3f/97/d03f9758f128ffd3237106f32b3595ff.jpg'
WHERE product_id = 'PROD10';

UPDATE beauty
SET
    skin_type = 'All Skin Types',
    volume_weight = '150ml',
    Is_organic = TRUE
WHERE product_id = 'PROD10';

UPDATE product
SET
    vendor_id = 'VNDR02',
    product_name = 'Modern African Print Outfit',
    description = 'Modern fashion outfit combining traditional African patterns with contemporary styling.',
    price = 295.00,
    stock_quantity = 30,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/1200x/34/c9/3c/34c93cb7b8bf1dd24ff7f33230f49aed.jpg'
WHERE product_id = 'PROD11';

UPDATE fashion
SET
    Color = 'Purple',
    Material = 'Cotton',
    Size = 'L',
    Gender_category = 'women'
WHERE product_id = 'PROD11';

UPDATE product
SET
    vendor_id = 'VNDR08',
    product_name = 'Herbal Skin Repair Cream',
    description = 'Moisturizing herbal cream designed to support healthy-looking skin.',
    price = 115.00,
    stock_quantity = 50,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/1200x/47/2e/6b/472e6b5b5bcfe31e3ecfaa32c8090fda.jpg'
WHERE product_id = 'PROD12';

UPDATE beauty
SET
    skin_type = 'Dry',
    volume_weight = '200ml',
    Is_organic = TRUE
WHERE product_id = 'PROD12';

UPDATE product
SET
    vendor_id = 'VNDR03',
    product_name = 'Heritage Woven Fashion',
    description = 'Handcrafted fashion piece inspired by Ghanaian weaving traditions.',
    price = 375.00,
    stock_quantity = 25,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/1200x/8f/36/b3/8f36b35d87ca11d8fc042ef2ff3e2433.jpg'
WHERE product_id = 'PROD13';

UPDATE fashion
SET
    Color = 'Green',
    Material = 'Linen',
    Size = 'M',
    Gender_category = 'unisex'
WHERE product_id = 'PROD13';

UPDATE product
SET
    vendor_id = 'VNDR04',
    product_name = 'Organic Beauty Moisturizer',
    description = 'Organic moisturizer designed to hydrate and refresh the skin.',
    price = 120.00,
    stock_quantity = 75,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/1200x/a5/86/a1/a586a1f8fb928c02914bfbe4a7953df3.jpg'
WHERE product_id = 'PROD14';

UPDATE beauty
SET
    skin_type = 'Oily',
    volume_weight = '200ml',
    Is_organic = TRUE
WHERE product_id = 'PROD14';

UPDATE product
SET
    vendor_id = 'VNDR05',
    product_name = 'Kente Statement Outfit',
    description = 'Bold statement outfit featuring premium Ghanaian-inspired kente fabric.',
    price = 520.00,
    stock_quantity = 18,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/736x/92/a6/c6/92a6c64e1998ca586a8549b06f732832.jpg'
WHERE product_id = 'PROD15';

UPDATE fashion
SET
    Color = 'Yellow',
    Material = 'Kente Cotton',
    Size = 'XL',
    Gender_category = 'women'
WHERE product_id = 'PROD15';

UPDATE product
SET
    vendor_id = 'VNDR07',
    product_name = 'Shea Butter Beauty Cream',
    description = 'Organic shea butter cream for deep skin nourishment and hydration.',
    price = 135.00,
    stock_quantity = 85,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/736x/c9/a7/03/c9a70383b81ffe9aca59709dec0d296d.jpg'
WHERE product_id = 'PROD16';

UPDATE beauty
SET
    skin_type = 'Sensitive',
    volume_weight = '200ml',
    Is_organic = TRUE
WHERE product_id = 'PROD16';

UPDATE product
SET
    vendor_id = 'VNDR01',
    product_name = 'Contemporary African Top',
    description = 'Stylish contemporary top with a colorful African-inspired design.',
    price = 175.00,
    stock_quantity = 40,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/1200x/2c/10/b8/2c10b8f3b6ef9fcdfcd3b0c28f42db81.jpg'
WHERE product_id = 'PROD17';

UPDATE fashion
SET
    Color = 'Multicolor',
    Material = 'Silk',
    Size = 'M',
    Gender_category = 'women'
WHERE product_id = 'PROD17';

UPDATE product
SET
    vendor_id = 'VNDR08',
    product_name = 'Natural Skin Care Lotion',
    description = 'Gentle natural lotion formulated for everyday skin hydration.',
    price = 100.00,
    stock_quantity = 60,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/1200x/b0/67/98/b067981a3f2f7d4fbaa9c2f1a893615b.jpg'
WHERE product_id = 'PROD18';

UPDATE beauty
SET
    skin_type = 'Combination',
    volume_weight = '250ml',
    Is_organic = TRUE
WHERE product_id = 'PROD18';

UPDATE product
SET
    vendor_id = 'VNDR10',
    product_name = 'Premium African Fashion Set',
    description = 'Premium fashion set combining contemporary style with African-inspired patterns.',
    price = 450.00,
    stock_quantity = 22,
    product_type = 'fashion',
    image_url = 'https://i.pinimg.com/736x/80/20/f5/8020f51ce3800c16a0d70e7d4131d633.jpg'
WHERE product_id = 'PROD19';

UPDATE fashion
SET
    Color = 'Black',
    Material = 'Polished Cotton',
    Size = 'L',
    Gender_category = 'unisex'
WHERE product_id = 'PROD19';

UPDATE product
SET
    vendor_id = 'VNDR01',
    product_name = 'Organic Radiance Cream',
    description = 'Organic beauty cream designed to moisturize and improve skin radiance.',
    price = 115.00,
    stock_quantity = 70,
    product_type = 'beauty',
    image_url = 'https://i.pinimg.com/1200x/64/5f/c5/645fc5ad7eefd8e461b01f0f6ebf6e2a.jpg'
WHERE product_id = 'PROD20';

UPDATE beauty
SET
    skin_type = 'All Skin Types',
    volume_weight = '200ml',
    Is_organic = TRUE
WHERE product_id = 'PROD20';

UPDATE product
SET vendor_id = 'VNDR02',
    product_name = 'Sweet Tooth Scented Bar',
    description = 'Sweet-scented solid bar product in pink packaging.',
    product_type = 'beauty'
WHERE product_id = 'PROD01';

INSERT INTO beauty (product_id, skin_type, volume_weight, Is_organic)
VALUES ('PROD01', 'All Skin Types', '50g', FALSE);

UPDATE product
SET vendor_id = 'VNDR04',
    product_name = 'Signature Fragrance Perfume',
    description = 'Boxed fragrance perfume in a glass bottle.'
WHERE product_id = 'PROD02';

UPDATE beauty
SET skin_type = 'All Skin Types', volume_weight = '50ml', Is_organic = FALSE
WHERE product_id = 'PROD02';

UPDATE product
SET vendor_id = 'VNDR07',
    product_name = 'Everyday Body Lotion',
    description = 'Pump-bottle body lotion for daily hydration.',
    product_type = 'beauty'
WHERE product_id = 'PROD03';

INSERT INTO beauty (product_id, skin_type, volume_weight, Is_organic)
VALUES ('PROD03', 'All Skin Types', '400ml', FALSE);

UPDATE product
SET vendor_id = 'VNDR08',
    product_name = 'Nourishing Body Lotion',
    description = 'Body lotion in a spray-top bottle for smooth skin.'
WHERE product_id = 'PROD04';

UPDATE beauty
SET skin_type = 'All Skin Types', volume_weight = '250ml', Is_organic = FALSE
WHERE product_id = 'PROD04';

UPDATE product
SET vendor_id = 'VNDR02',
    product_name = 'Tinted Lip Gloss',
    description = 'Glossy pink lip gloss with doe-foot applicator.',
    product_type = 'beauty'
WHERE product_id = 'PROD05';

INSERT INTO beauty (product_id, skin_type, volume_weight, Is_organic)
VALUES ('PROD05', 'All Skin Types', '5ml', FALSE);

UPDATE product
SET vendor_id = 'VNDR04',
    product_name = 'Powder Blush Compact',
    description = 'Pressed powder blush in a mirrored compact case.'
WHERE product_id = 'PROD06';

UPDATE beauty
SET skin_type = 'All Skin Types', volume_weight = '10g', Is_organic = FALSE
WHERE product_id = 'PROD06';

UPDATE product
SET vendor_id = 'VNDR07',
    product_name = 'Concealer with Applicator',
    description = 'Liquid concealer stick with built-in blending applicator.',
    product_type = 'beauty'
WHERE product_id = 'PROD07';

INSERT INTO beauty (product_id, skin_type, volume_weight, Is_organic)
VALUES ('PROD07', 'All Skin Types', '15ml', FALSE);

UPDATE product
SET vendor_id = 'VNDR01',
    product_name = 'Brown Co-ord Set',
    description = 'Matching short-sleeve top and shorts co-ord outfit.',
    product_type = 'fashion'
WHERE product_id = 'PROD08';

INSERT INTO fashion (product_id, Color, Material, Size, Gender_category)
VALUES ('PROD08', 'Brown', 'Cotton Blend', 'M', 'women');

UPDATE product
SET vendor_id = 'VNDR03',
    product_name = 'Blue Quarter-Zip Pullover',
    description = 'Casual fleece pullover with quarter-zip collar and pocket.'
WHERE product_id = 'PROD09';

UPDATE fashion
SET Color = 'Blue', Material = 'Fleece', Size = 'M', Gender_category = 'unisex'
WHERE product_id = 'PROD09';

UPDATE product
SET vendor_id = 'VNDR05',
    product_name = 'Color-Block Kids Tee',
    description = 'Light blue short-sleeve tee with contrast sleeve panels.',
    product_type = 'fashion'
WHERE product_id = 'PROD10';

INSERT INTO fashion (product_id, Color, Material, Size, Gender_category)
VALUES ('PROD10', 'Light Blue', 'Cotton', 'S', 'unisex');

UPDATE product
SET vendor_id = 'VNDR06',
    product_name = 'Grey Sweatpants',
    description = 'Relaxed-fit fleece sweatpants in grey.'
WHERE product_id = 'PROD11';

UPDATE fashion
SET Color = 'Grey', Material = 'Cotton Fleece', Size = 'L', Gender_category = 'unisex'
WHERE product_id = 'PROD11';

UPDATE product
SET vendor_id = 'VNDR09',
    product_name = 'Ruffle-Sleeve Kids Top',
    description = 'Light blue top with ruffled short sleeves.',
    product_type = 'fashion'
WHERE product_id = 'PROD12';

INSERT INTO fashion (product_id, Color, Material, Size, Gender_category)
VALUES ('PROD12', 'Light Blue', 'Cotton', 'S', 'women');

UPDATE product
SET vendor_id = 'VNDR10',
    product_name = 'Beige Zip Jacket',
    description = 'Lightweight beige zip-up jacket.'
WHERE product_id = 'PROD13';

UPDATE fashion
SET Color = 'Beige', Material = 'Cotton Blend', Size = 'M', Gender_category = 'unisex'
WHERE product_id = 'PROD13';

UPDATE product
SET vendor_id = 'VNDR01',
    product_name = 'Brown Polo Sweater',
    description = 'Knit polo-collar sweater in brown.',
    product_type = 'fashion'
WHERE product_id = 'PROD14';

INSERT INTO fashion (product_id, Color, Material, Size, Gender_category)
VALUES ('PROD14', 'Brown', 'Wool Blend', 'M', 'men');

UPDATE product
SET vendor_id = 'VNDR03',
    product_name = 'Black Wide-Leg Trousers',
    description = 'Tailored wide-leg trousers in black.'
WHERE product_id = 'PROD15';

UPDATE fashion
SET Color = 'Black', Material = 'Polyester', Size = 'L', Gender_category = 'women'
WHERE product_id = 'PROD15';

UPDATE product
SET vendor_id = 'VNDR05',
    product_name = 'Camisole Tank Top Set',
    description = 'Set of fitted camisole tank tops in assorted colors.',
    product_type = 'fashion'
WHERE product_id = 'PROD16';

INSERT INTO fashion (product_id, Color, Material, Size, Gender_category)
VALUES ('PROD16', 'Multicolor', 'Cotton', 'S', 'women');

UPDATE product
SET vendor_id = 'VNDR06',
    product_name = 'Polka Dot Tie-Front Top',
    description = 'Brown polka-dot top with tie-front detail.'
WHERE product_id = 'PROD17';

UPDATE fashion
SET Color = 'Brown', Material = 'Cotton', Size = 'M', Gender_category = 'women'
WHERE product_id = 'PROD17';

UPDATE product
SET vendor_id = 'VNDR09',
    product_name = 'Kids Sneakers',
    description = 'Lace-up sneakers with striped side detail, kids sizing.',
    product_type = 'fashion'
WHERE product_id = 'PROD18';

INSERT INTO fashion (product_id, Color, Material, Size, Gender_category)
VALUES ('PROD18', 'Navy/White', 'Canvas', 'M', 'unisex');

UPDATE product
SET vendor_id = 'VNDR08',
    product_name = 'Lip & Eye Pencil Duo',
    description = 'Set of two precision pencils for lip and eye use.',
    product_type = 'beauty'
WHERE product_id = 'PROD19';

INSERT INTO beauty (product_id, skin_type, volume_weight, Is_organic)
VALUES ('PROD19', 'All Skin Types', '5g', FALSE);

UPDATE product
SET vendor_id = 'VNDR10',
    product_name = 'Polka Dot Kids Romper',
    description = 'Pink polka-dot romper with ruffled straps, kids sizing.',
    product_type = 'fashion'
WHERE product_id = 'PROD20';

INSERT INTO fashion (product_id, Color, Material, Size, Gender_category)
VALUES ('PROD20', 'Pink', 'Cotton', 'S', 'women');

CREATE TRIGGER trg_reduce_stock_after_order_item
AFTER INSERT ON Order_Items
FOR EACH ROW
BEGIN

    UPDATE Product
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;

END;

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

END;

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

CREATE TRIGGER trg_reduce_stock_after_order_item
AFTER INSERT ON Order_Items
FOR EACH ROW
BEGIN
    UPDATE Product
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END;