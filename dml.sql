use ecommercetest;

INSERT INTO customer (customer_id, f_name, l_name, phone_number, email) VALUES
('CUST00', 'Kofi', 'Mensah', '+233241234501', 'kofi.mensah1@email.com'),
('CUST02', 'Ama', 'Asante', '+233241234502', 'ama.asante2@email.com'),
('CUST03', 'John', 'Doe', '+233241234503', 'john.doe3@email.com'),
('CUST04', 'Kwame', 'Osei', '+233241234504', 'kwame.osei4@email.com'),
('CUST05', 'Esi', 'Boakye', '+233241234505', 'esi.boakye5@email.com'),
('CUST06', 'Yaw', 'Appiah', '+233241234506', 'yaw.appiah6@email.com'),
('CUST07', 'Kwaku', 'Agyemang', '+233241234507', 'kwaku.agyemang7@email.com'),
('CUST08', 'Akosua', 'Acquah', '+233241234508', 'akosua.acquah8@email.com'),
('CUST09', 'Abeiku', 'Annan', '+233241234509', 'abeiku.annan9@email.com'),
('CUST10', 'Afia', 'Benson', '+233241234510', 'afia.benson10@email.com'),
('CUST11', 'Kojo', 'Gyamfi', '+233241234511', 'kojo.gyamfi11@email.com'),
('CUST12', 'Abena', 'Koomson', '+233241234512', 'abena.koomson12@email.com'),
('CUST13', 'Ekow', 'Arthur', '+233241234513', 'ekow.arthur13@email.com'),
('CUST14', 'Akua', 'Owusu', '+233241234514', 'akua.owusu14@email.com'),
('CUST15', 'Fiifi', 'Danquah', '+233241234515', 'fiifi.danquah15@email.com'),
('CUST16', 'Yaa', 'Addison', '+233241234516', 'yaa.addison16@email.com'),
('CUST17', 'Paapa', 'Sarpong', '+233241234517', 'paapa.sarpong17@email.com'),
('CUST18', 'Amma', 'Aidoo', '+233241234518', 'amma.aidoo18@email.com'),
('CUST19', 'Nii', 'Tagoe', '+233241234519', 'nii.tagoe19@email.com'),
('CUST20', 'Naa', 'Sackey', '+233241234520', 'naa.sackey20@email.com'),
('CUST21', 'Osei', 'Quaye', '+233241234521', 'osei.quaye21@email.com'),
('CUST22', 'Maud', 'Lamptey', '+233241234522', 'maud.lamptey22@email.com'),
('CUST23', 'Emmanuel', 'Lartey', '+233241234523', 'emmanuel.lartey23@email.com'),
('CUST24', 'Grace', 'Frimpong', '+233241234524', 'grace.frimpong24@email.com'),
('CUST25', 'Samuel', 'Tetteh', '+233241234525', 'samuel.tetteh25@email.com'),
('CUST26', 'Dorothy', 'Adu', '+233241234526', 'dorothy.adu26@email.com'),
('CUST27', 'Michael', 'Baah', '+233241234527', 'michael.baah27@email.com'),
('CUST28', 'Elizabeth', 'Boateng', '+233241234528', 'elizabeth.boateng28@email.com'),
('CUST29', 'Prince', 'Donkor', '+233241234529', 'prince.donkor29@email.com'),
('CUST30', 'Rebecca', 'Eshun', '+233241234530', 'rebecca.eshun30@email.com'),
('CUST31', 'Daniel', 'Boadu', '+233241234531', 'daniel.boadu31@email.com'),
('CUST32', 'Ruth', 'Darko', '+233241234532', 'ruth.darko32@email.com'),
('CUST33', 'Joseph', 'Fosu', '+233241234533', 'joseph.fosu33@email.com'),
('CUST34', 'Sarah', 'Gallo', '+233241234534', 'sarah.gallo34@email.com'),
('CUST35', 'Isaac', 'Inkoom', '+233241234535', 'isaac.inkoom35@email.com');

INSERT INTO customer_credentials (customer_id, password_hash) VALUES
('CUST00', '$2b$12$mockhash01xxxxxxxxxxxxxxxxxxxxxx'),('CUST02', '$2b$12$mockhash02xxxxxxxxxxxxxxxxxxxxxx'),('CUST03', '$2b$12$mockhash03xxxxxxxxxxxxxxxxxxxxxx'),('CUST04', '$2b$12$mockhash04xxxxxxxxxxxxxxxxxxxxxx'),('CUST05', '$2b$12$mockhash05xxxxxxxxxxxxxxxxxxxxxx'),('CUST06', '$2b$12$mockhash06xxxxxxxxxxxxxxxxxxxxxx'),('CUST07', '$2b$12$mockhash07xxxxxxxxxxxxxxxxxxxxxx'),('CUST08', '$2b$12$mockhash08xxxxxxxxxxxxxxxxxxxxxx'),('CUST09', '$2b$12$mockhash09xxxxxxxxxxxxxxxxxxxxxx'),('CUST10', '$2b$12$mockhash10xxxxxxxxxxxxxxxxxxxxxx'),('CUST11', '$2b$12$mockhash11xxxxxxxxxxxxxxxxxxxxxx'),('CUST12', '$2b$12$mockhash12xxxxxxxxxxxxxxxxxxxxxx'),('CUST13', '$2b$12$mockhash13xxxxxxxxxxxxxxxxxxxxxx'),('CUST14', '$2b$12$mockhash14xxxxxxxxxxxxxxxxxxxxxx'),('CUST15', '$2b$12$mockhash15xxxxxxxxxxxxxxxxxxxxxx'),('CUST16', '$2b$12$mockhash16xxxxxxxxxxxxxxxxxxxxxx'),('CUST17', '$2b$12$mockhash17xxxxxxxxxxxxxxxxxxxxxx'),('CUST18', '$2b$12$mockhash18xxxxxxxxxxxxxxxxxxxxxx'),('CUST19', '$2b$12$mockhash19xxxxxxxxxxxxxxxxxxxxxx'),('CUST20', '$2b$12$mockhash20xxxxxxxxxxxxxxxxxxxxxx'),('CUST21', '$2b$12$mockhash21xxxxxxxxxxxxxxxxxxxxxx'),('CUST22', '$2b$12$mockhash22xxxxxxxxxxxxxxxxxxxxxx'),('CUST23', '$2b$12$mockhash23xxxxxxxxxxxxxxxxxxxxxx'),('CUST24', '$2b$12$mockhash24xxxxxxxxxxxxxxxxxxxxxx'),('CUST25', '$2b$12$mockhash25xxxxxxxxxxxxxxxxxxxxxx'),('CUST26', '$2b$12$mockhash26xxxxxxxxxxxxxxxxxxxxxx'),('CUST27', '$2b$12$mockhash27xxxxxxxxxxxxxxxxxxxxxx'),('CUST28', '$2b$12$mockhash28xxxxxxxxxxxxxxxxxxxxxx'),('CUST29', '$2b$12$mockhash29xxxxxxxxxxxxxxxxxxxxxx'),('CUST30', '$2b$12$mockhash30xxxxxxxxxxxxxxxxxxxxxx'),('CUST31', '$2b$12$mockhash31xxxxxxxxxxxxxxxxxxxxxx'),('CUST32', '$2b$12$mockhash32xxxxxxxxxxxxxxxxxxxxxx'),('CUST33', '$2b$12$mockhash33xxxxxxxxxxxxxxxxxxxxxx'),('CUST34', '$2b$12$mockhash34xxxxxxxxxxxxxxxxxxxxxx'),('CUST35', '$2b$12$mockhash35xxxxxxxxxxxxxxxxxxxxxx');


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

INSERT INTO vendor_credentials (vendor_id, password_hash) VALUES
('VNDR01', '$2b$12$mockvhash01xxxxxxxxxxxxxxxxxxxxx'),('VNDR02', '$2b$12$mockvhash02xxxxxxxxxxxxxxxxxxxxx'),('VNDR03', '$2b$12$mockvhash03xxxxxxxxxxxxxxxxxxxxx'),('VNDR04', '$2b$12$mockvhash04xxxxxxxxxxxxxxxxxxxxx'),('VNDR05', '$2b$12$mockvhash05xxxxxxxxxxxxxxxxxxxxx'),('VNDR06', '$2b$12$mockvhash06xxxxxxxxxxxxxxxxxxxxx'),('VNDR07', '$2b$12$mockvhash07xxxxxxxxxxxxxxxxxxxxx'),('VNDR08', '$2b$12$mockvhash08xxxxxxxxxxxxxxxxxxxxx'),('VNDR09', '$2b$12$mockvhash09xxxxxxxxxxxxxxxxxxxxx'),('VNDR10', '$2b$12$mockvhash10xxxxxxxxxxxxxxxxxxxxx');


INSERT INTO product (product_id, vendor_id, product_name, description, price, stock_quantity, product_type) VALUES
('PROD01', 'VNDR02', 'Product Item 1', 'High quality platform item', 112.50, 45, 'fashion'),
('PROD02', 'VNDR03', 'Cosmetic Cream 2', 'High quality platform item', 545.22, 12, 'beauty'),
('PROD03', 'VNDR04', 'Product Item 3', 'High quality platform item', 234.12, 114, 'fashion'),
('PROD04', 'VNDR05', 'Cosmetic Cream 4', 'High quality platform item', 99.99, 87, 'beauty'),
('PROD05', 'VNDR06', 'Product Item 5', 'High quality platform item', 412.35, 65, 'fashion'),
('PROD06', 'VNDR07', 'Cosmetic Cream 6', 'High quality platform item', 150.00, 142, 'beauty'),
('PROD07', 'VNDR08', 'Product Item 7', 'High quality platform item', 85.00, 93, 'fashion'),
('PROD08', 'VNDR09', 'Cosmetic Cream 8', 'High quality platform item', 310.20, 54, 'beauty'),
('PROD09', 'VNDR10', 'Product Item 9', 'High quality platform item', 195.00, 22, 'fashion'),
('PROD10', 'VNDR01', 'Cosmetic Cream 10', 'High quality platform item', 75.50, 110, 'beauty'),
('PROD11', 'VNDR02', 'Product Item 11', 'High quality platform item', 320.00, 40, 'fashion'),
('PROD12', 'VNDR03', 'Cosmetic Cream 12', 'High quality platform item', 185.00, 95, 'beauty'),
('PROD13', 'VNDR04', 'Product Item 13', 'High quality platform item', 290.00, 77, 'fashion'),
('PROD14', 'VNDR05', 'Cosmetic Cream 14', 'High quality platform item', 65.00, 130, 'beauty'),
('PROD15', 'VNDR06', 'Product Item 15', 'High quality platform item', 480.00, 18, 'fashion'),
('PROD16', 'VNDR07', 'Cosmetic Cream 16', 'High quality platform item', 220.00, 62, 'beauty'),
('PROD17', 'VNDR08', 'Product Item 17', 'High quality platform item', 135.00, 88, 'fashion'),
('PROD18', 'VNDR09', 'Cosmetic Cream 18', 'High quality platform item', 140.00, 105, 'beauty'),
('PROD19', 'VNDR10', 'Product Item 19', 'High quality platform item', 510.00, 29, 'fashion'),
('PROD20', 'VNDR01', 'Cosmetic Cream 20', 'High quality platform item', 95.00, 125, 'beauty'),
('PROD21', 'VNDR02', 'Product Item 21', 'High quality platform item', 165.00, 74, 'fashion'),
('PROD22', 'VNDR03', 'Cosmetic Cream 22', 'High quality platform item', 275.00, 48, 'beauty'),
('PROD23', 'VNDR04', 'Product Item 23', 'High quality platform item', 340.00, 36, 'fashion'),
('PROD24', 'VNDR05', 'Cosmetic Cream 24', 'High quality platform item', 55.00, 140, 'beauty'),
('PROD25', 'VNDR06', 'Product Item 25', 'High quality platform item', 425.00, 52, 'fashion'),
('PROD26', 'VNDR07', 'Cosmetic Cream 26', 'High quality platform item', 190.00, 81, 'beauty'),
('PROD27', 'VNDR08', 'Product Item 27', 'High quality platform item', 115.00, 99, 'fashion'),
('PROD28', 'VNDR09', 'Cosmetic Cream 28', 'High quality platform item', 230.00, 66, 'beauty'),
('PROD29', 'VNDR10', 'Product Item 29', 'High quality platform item', 380.00, 25, 'fashion'),
('PROD30', 'VNDR01', 'Cosmetic Cream 30', 'High quality platform item', 125.00, 115, 'beauty');

-- Subtype Distributing
INSERT INTO fashion (product_id, Color, Material, Size, Gender_category) VALUES
('PROD01', 'Red', 'Cotton', 'M', 'unisex'),('PROD03', 'Blue', 'Silk', 'L', 'unisex'),('PROD05', 'Green', 'Linen', 'XL', 'unisex'),('PROD07', 'Black', 'Polyester', 'S', 'unisex'),('PROD09', 'White', 'Kente Cotton', 'M', 'unisex'),('PROD11', 'Gold', 'Polished Cotton', 'XXL', 'unisex'),('PROD13', 'Purple', 'Cotton', 'L', 'unisex'),('PROD15', 'Yellow', 'Ankara Wax Cotton', 'S', 'unisex'),('PROD17', 'Pink', 'Linen', 'M', 'unisex'),('PROD19', 'Multicolor', 'Silk', 'XL', 'unisex'),('PROD21', 'Blue', 'Cotton', 'S', 'unisex'),('PROD23', 'Black', 'Polyester', 'M', 'unisex'),('PROD25', 'White', 'Linen', 'L', 'unisex'),('PROD27', 'Red', 'Kente Cotton', 'XL', 'unisex'),('PROD29', 'Green', 'Polished Cotton', 'XXL', 'unisex');

INSERT INTO beauty (product_id, skin_type, volume_weight, Is_organic) VALUES
('PROD02', 'Dry', '200ml', TRUE),('PROD04', 'Oily', '200ml', TRUE),('PROD06', 'Sensitive', '200ml', TRUE),('PROD08', 'Combination', '200ml', TRUE),('PROD10', 'All Skin Types', '200ml', TRUE),('PROD12', 'Dry', '200ml', TRUE),('PROD14', 'Oily', '200ml', TRUE),('PROD16', 'Sensitive', '200ml', TRUE),('PROD18', 'Combination', '200ml', TRUE),('PROD20', 'All Skin Types', '200ml', TRUE),('PROD22', 'Dry', '200ml', TRUE),('PROD24', 'Oily', '200ml', TRUE),('PROD26', 'Sensitive', '200ml', TRUE),('PROD28', 'Combination', '200ml', TRUE),('PROD30', 'All Skin Types', '200ml', TRUE);




INSERT INTO cart (cart_id, customer_id) VALUES
('CRT001', 'CUST00'),('CRT002', 'CUST02'),('CRT003', 'CUST03'),('CRT004', 'CUST04'),('CRT005', 'CUST05'),('CRT006', 'CUST06'),('CRT007', 'CUST07'),('CRT008', 'CUST08'),('CRT009', 'CUST09'),('CRT010', 'CUST10'),('CRT011', 'CUST11'),('CRT012', 'CUST12'),('CRT013', 'CUST13'),('CRT014', 'CUST14'),('CRT015', 'CUST15'),('CRT016', 'CUST16'),('CRT017', 'CUST17'),('CRT018', 'CUST18'),('CRT019', 'CUST19'),('CRT020', 'CUST20'),('CRT021', 'CUST21'),('CRT022', 'CUST22'),('CRT023', 'CUST23'),('CRT024', 'CUST24'),('CRT025', 'CUST25'),('CRT026', 'CUST26'),('CRT027', 'CUST27'),('CRT028', 'CUST28'),('CRT029', 'CUST29'),('CRT030', 'CUST30'),('CRT031', 'CUST31'),('CRT032', 'CUST32'),('CRT033', 'CUST33'),('CRT034', 'CUST34'),('CRT035', 'CUST35');

-- Connects 2 products systematically to each active cart profile container
INSERT INTO cart_items (product_id, cart_id, quantity, added_date) VALUES
('PROD01', 'CRT001', 1, '2026-08-01'),('PROD02', 'CRT001', 2, '2026-08-01'),('PROD03', 'CRT002', 1, '2026-08-01'),('PROD04', 'CRT002', 2, '2026-08-01'),('PROD05', 'CRT003', 1, '2026-08-01'),('PROD06', 'CRT003', 2, '2026-08-01'),('PROD07', 'CRT004', 1, '2026-08-01'),('PROD08', 'CRT004', 2, '2026-08-01'),('PROD09', 'CRT005', 1, '2026-08-01'),('PROD10', 'CRT005', 2, '2026-08-01'),('PROD11', 'CRT006', 1, '2026-08-01'),('PROD12', 'CRT006', 2, '2026-08-01'),('PROD13', 'CRT007', 1, '2026-08-01'),('PROD14', 'CRT007', 2, '2026-08-01'),('PROD15', 'CRT008', 1, '2026-08-01'),('PROD16', 'CRT008', 2, '2026-08-01'),('PROD17', 'CRT009', 1, '2026-08-01'),('PROD18', 'CRT009', 2, '2026-08-01'),('PROD19', 'CRT010', 1, '2026-08-01'),('PROD20', 'CRT010', 2, '2026-08-01'),('PROD21', 'CRT011', 1, '2026-08-01'),('PROD22', 'CRT011', 2, '2026-08-01'),('PROD23', 'CRT012', 1, '2026-08-01'),('PROD24', 'CRT012', 2, '2026-08-01'),('PROD25', 'CRT013', 1, '2026-08-01'),('PROD26', 'CRT013', 2, '2026-08-01'),('PROD27', 'CRT014', 1, '2026-08-01'),('PROD28', 'CRT014', 2, '2026-08-01'),('PROD29', 'CRT015', 1, '2026-08-01'),('PROD30', 'CRT015', 2, '2026-08-01'),('PROD01', 'CRT016', 1, '2026-08-01'),('PROD02', 'CRT016', 2, '2026-08-01'),('PROD03', 'CRT017', 1, '2026-08-01'),('PROD04', 'CRT017', 2, '2026-08-01'),('PROD05', 'CRT018', 1, '2026-08-01'),('PROD06', 'CRT018', 2, '2026-08-01'),('PROD07', 'CRT019', 1, '2026-08-01'),('PROD08', 'CRT019', 2, '2026-08-01'),('PROD09', 'CRT020', 1, '2026-08-01'),('PROD10', 'CRT020', 2, '2026-08-01'),('PROD11', 'CRT021', 1, '2026-08-01'),('PROD12', 'CRT021', 2, '2026-08-01'),('PROD13', 'CRT022', 1, '2026-08-01'),('PROD14', 'CRT022', 2, '2026-08-01'),('PROD15', 'CRT023', 1, '2026-08-01'),('PROD16', 'CRT023', 2, '2026-08-01'),('PROD17', 'CRT024', 1, '2026-08-01'),('PROD18', 'CRT024', 2, '2026-08-01'),('PROD19', 'CRT025', 1, '2026-08-01'),('PROD20', 'CRT025', 2, '2026-08-01'),('PROD21', 'CRT026', 1, '2026-08-01'),('PROD22', 'CRT026', 2, '2026-08-01'),('PROD23', 'CRT027', 1, '2026-08-01'),('PROD24', 'CRT027', 2, '2026-08-01'),('PROD25', 'CRT028', 1, '2026-08-01'),('PROD26', 'CRT028', 2, '2026-08-01'),('PROD27', 'CRT029', 1, '2026-08-01'),('PROD28', 'CRT029', 2, '2026-08-01'),('PROD29', 'CRT030', 1, '2026-08-01'),('PROD30', 'CRT030', 2, '2026-08-01');



INSERT INTO address (address_id, city, Landmark, street_address, customer_id) VALUES
('ADR001', 'Accra', 'Opposite Bank', '43 Liberation Road', 'CUST00'),('ADR002', 'Kumasi', 'Near Market', '52 Kufuor Avenue', 'CUST02'),('ADR003', 'Tema', 'Near Roundabout', '17 Meridian Street', 'CUST03'),('ADR004', 'Takoradi', 'Behind Station', '96 Harbor Road', 'CUST04'),('ADR005', 'Tamale', 'Near Mall', '56 Gbewaa Palace Lane', 'CUST05'),('ADR006', 'Ho', 'Close to School', '24 Mawuli School Road', 'CUST06'),('ADR007', 'Koforidua', 'Opposite Hospital', '8 Spintex Road', 'CUST07'),('ADR008', 'Cape Coast', 'Opposite Bank', '48 Ring Road Central', 'CUST08'),('ADR009', 'Sunyani', 'Near Roundabout', '51 Anaji Highway', 'CUST09'),('ADR010', 'Bolgatanga', 'Close to School', '38 Ahodwo Avenue', 'CUST10'),('ADR011', 'Wa', 'Near Roundabout', '97 Liberation Road', 'CUST11'),('ADR012', 'Obuasi', 'Behind Station', '13 Kufuor Avenue', 'CUST12'),('ADR013', 'Techiman', 'Behind Station', '79 Meridian Street', 'CUST13'),('ADR014', 'Kasoa', 'Near Mall', '50 Harbor Road', 'CUST14'),('ADR015', 'Ashaiman', 'Near Mall', '69 Gbewaa Palace Lane', 'CUST15'),('ADR016', 'Accra', 'Opposite Hospital', '30 Mawuli School Road', 'CUST16'),('ADR017', 'Kumasi', 'Near Market', '58 Spintex Road', 'CUST17'),('ADR018', 'Tema', 'Behind Station', '56 Ring Road Central', 'CUST18'),('ADR019', 'Takoradi', 'Opposite Hospital', '76 Anaji Highway', 'CUST19'),('ADR020', 'Tamale', 'Near Roundabout', '69 Ahodwo Avenue', 'CUST20'),('ADR021', 'Ho', 'Near Roundabout', '37 Liberation Road', 'CUST21'),('ADR022', 'Koforidua', 'Near Mall', '95 Kufuor Avenue', 'CUST22'),('ADR023', 'Cape Coast', 'Opposite Hospital', '14 Meridian Street', 'CUST23'),('ADR024', 'Sunyani', 'Near Roundabout', '57 Harbor Road', 'CUST24'),('ADR025', 'Bolgatanga', 'Opposite Hospital', '39 Gbewaa Palace Lane', 'CUST25'),('ADR026', 'Wa', 'Near Market', '3 Mawuli School Road', 'CUST26'),('ADR027', 'Obuasi', 'Opposite Bank', '80 Spintex Road', 'CUST27'),('ADR028', 'Techiman', 'Near Roundabout', '68 Ring Road Central', 'CUST28'),('ADR029', 'Kasoa', 'Near Roundabout', '39 Anaji Highway', 'CUST29'),('ADR030', 'Ashaiman', 'Behind Station', '82 Ahodwo Avenue', 'CUST30'),('ADR031', 'Accra', 'Opposite Bank', '84 Liberation Road', 'CUST31'),('ADR032', 'Kumasi', 'Close to School', '76 Kufuor Avenue', 'CUST32'),('ADR033', 'Tema', 'Close to School', '13 Meridian Street', 'CUST33'),('ADR034', 'Takoradi', 'Behind Station', '14 Harbor Road', 'CUST34'),('ADR035', 'Tamale', 'Close to School', '7 Gbewaa Palace Lane', 'CUST35');



-- Orders Generation
INSERT INTO orders (order_id, customer_id, cart_id, order_date, subtotal, shipping_fee) VALUES
('ORD01', 'CUST00', 'CRT001', '2026-08-02', 300.00, 30.00),('ORD02', 'CUST02', 'CRT002', '2026-08-02', 300.00, 30.00),('ORD03', 'CUST03', 'CRT003', '2026-08-02  ', 300.00, 30.00),('ORD04', 'CUST04', 'CRT004', '2026-08-02', 300.00, 30.00),('ORD05', 'CUST05', 'CRT005', '2026-08-02  ', 300.00, 30.00),('ORD06', 'CUST06', 'CRT006', '2026-08-02  ', 300.00, 30.00),('ORD07', 'CUST07', 'CRT007', '2026-08-02  ', 300.00, 30.00),('ORD08', 'CUST08', 'CRT008', '2026-08-02  ', 300.00, 30.00),('ORD09', 'CUST09', 'CRT009', '2026-08-02  ', 300.00, 30.00),('ORD10', 'CUST10', 'CRT010', '2026-08-02  ', 300.00, 30.00),('ORD11', 'CUST11', 'CRT011', '2026-08-02  ', 300.00, 30.00),('ORD12', 'CUST12', 'CRT012', '2026-08-02  ', 300.00, 30.00),('ORD13', 'CUST13', 'CRT013', '2026-08-02  ', 300.00, 30.00),('ORD14', 'CUST14', 'CRT014', '2026-08-02  ', 300.00, 30.00),('ORD15', 'CUST15', 'CRT015', '2026-08-02  ', 300.00, 30.00),('ORD16', 'CUST16', 'CRT016', '2026-08-02 ', 300.00, 30.00),('ORD17', 'CUST17', 'CRT017', '2026-08-02  ', 300.00, 30.00),('ORD18', 'CUST18', 'CRT018', '2026-08-02  ', 300.00, 30.00),('ORD19', 'CUST19', 'CRT019', '2026-08-02', 300.00, 30.00),('ORD20', 'CUST20', 'CRT020', '2026-08-02  ', 300.00, 30.00),('ORD21', 'CUST21', 'CRT021', '2026-08-02  ', 300.00, 30.00),('ORD22', 'CUST22', 'CRT022', '2026-08-02  ', 300.00, 30.00),('ORD23', 'CUST23', 'CRT023', '2026-08-02  ', 300.00, 30.00),('ORD24', 'CUST24', 'CRT024', '2026-08-02  ', 300.00, 30.00),('ORD25', 'CUST25', 'CRT025', '2026-08-02  ', 300.00, 30.00),('ORD26', 'CUST26', 'CRT026', '2026-08-02  ', 300.00, 30.00),('ORD27', 'CUST27', 'CRT027', '2026-08-02  ', 300.00, 30.00),('ORD28', 'CUST28', 'CRT028', '2026-08-02  ', 300.00, 30.00),('ORD29', 'CUST29', 'CRT029', '2026-08-02  ', 300.00, 30.00),('ORD30', 'CUST30', 'CRT030', '2026-08-02  ', 300.00, 30.00);

-- Payments Supertype (Splitting exactly into 3 types across constraints)
INSERT INTO payment (payment_id, customer_id, amount, payment_date, payment_type, order_id) VALUES
('PAY01', 'CUST00', 330.00, '2026-08-02', 'bank transfer', 'ORD01'),('PAY02', 'CUST02', 330.00, '2026-08-02', 'mobile money', 'ORD02'),('PAY03', 'CUST03', 330.00, '2026-08-02', 'card', 'ORD03'),('PAY04', 'CUST04', 330.00, '2026-08-02', 'bank transfer', 'ORD04'),('PAY05', 'CUST05', 330.00, '2026-08-02', 'mobile money', 'ORD05'),('PAY06', 'CUST06', 330.00, '2026-08-02', 'card', 'ORD06'),('PAY07', 'CUST07', 330.00, '2026-08-02', 'bank transfer', 'ORD07'),('PAY08', 'CUST08', 330.00, '2026-08-02', 'mobile money', 'ORD08'),('PAY09', 'CUST09', 330.00, '2026-08-02', 'card', 'ORD09'),('PAY10', 'CUST10', 330.00, '2026-08-02', 'bank transfer', 'ORD10'),('PAY11', 'CUST11', 330.00, '2026-08-02', 'mobile money', 'ORD11'),('PAY12', 'CUST12', 330.00, '2026-08-02', 'card', 'ORD12'),('PAY13', 'CUST13', 330.00, '2026-08-02', 'bank transfer', 'ORD13'),('PAY14', 'CUST14', 330.00, '2026-08-02', 'mobile money', 'ORD14'),('PAY15', 'CUST15', 330.00, '2026-08-02', 'card', 'ORD15'),('PAY16', 'CUST16', 330.00, '2026-08-02', 'bank transfer', 'ORD16'),('PAY17', 'CUST17', 330.00, '2026-08-02', 'mobile money', 'ORD17'),('PAY18', 'CUST18', 330.00, '2026-08-02', 'card', 'ORD18'),('PAY19', 'CUST19', 330.00, '2026-08-02', 'bank transfer', 'ORD19'),('PAY20', 'CUST20', 330.00, '2026-08-02', 'mobile money', 'ORD20'),('PAY21', 'CUST21', 330.00, '2026-08-02', 'card', 'ORD21'),('PAY22', 'CUST22', 330.00, '2026-08-02', 'bank transfer', 'ORD22'),('PAY23', 'CUST23', 330.00, '2026-08-02', 'mobile money', 'ORD23'),('PAY24', 'CUST24', 330.00, '2026-08-02', 'card', 'ORD24'),('PAY25', 'CUST25', 330.00, '2026-08-02', 'bank transfer', 'ORD25'),('PAY26', 'CUST26', 330.00, '2026-08-02', 'mobile money', 'ORD26'),('PAY27', 'CUST27', 330.00, '2026-08-02', 'card', 'ORD27'),('PAY28', 'CUST28', 330.00, '2026-08-02', 'bank transfer', 'ORD28'),('PAY29', 'CUST29', 330.00, '2026-08-02', 'mobile money', 'ORD29'),('PAY30', 'CUST30', 330.00, '2026-08-02', 'card', 'ORD30');

-- Payment Subtypes Distribution (10 Bank, 10 Momo, 10 Card)
INSERT INTO bank_transfer (payment_id, bank_name, account_number, account_name) VALUES
('PAY01', 'GCB Bank', '102030405060', 'Mock Account'),('PAY04', 'Ecobank', '102030405060', 'Mock Account'),('PAY07', 'Standard Chartered', '102030405060', 'Mock Account'),('PAY10', 'Absa Bank', '102030405060', 'Mock Account'),('PAY13', 'Zenith Bank', '102030405060', 'Mock Account'),('PAY16', 'GCB Bank', '102030405060', 'Mock Account'),('PAY19', 'Ecobank', '102030405060', 'Mock Account'),('PAY22', 'Standard Chartered', '102030405060', 'Mock Account'),('PAY25', 'Absa Bank', '102030405060', 'Mock Account'),('PAY28', 'Zenith Bank', '102030405060', 'Mock Account');

INSERT INTO mobile_money (payment_id, network, phone_number, account_name) VALUES
('PAY02', 'MTN', '0241002003', 'Mock Account'),('PAY05', 'Telecel', '0241002003', 'Mock Account'),('PAY08', 'AT', '0241002003', 'Mock Account'),('PAY11', 'MTN', '0241002003', 'Mock Account'),('PAY14', 'Telecel', '0241002003', 'Mock Account'),('PAY17', 'AT', '0241002003', 'Mock Account'),('PAY20', 'MTN', '0241002003', 'Mock Account'),('PAY23', 'Telecel', '0241002003', 'Mock Account'),('PAY26', 'AT', '0241002003', 'Mock Account'),('PAY29', 'MTN', '0241002003', 'Mock Account');

INSERT INTO card (payment_id, token_id, card_num, card_name, Expiry_date) VALUES
('PAY03', '003', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY06', '006', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY09', '009', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY12', '012', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY15', '015', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY18', '018', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY21', '021', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY24', '024', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY27', '027', '4111XXXXXXXX123', 'Mock Name', '2029-12-31'),('PAY30', '030', '4111XXXXXXXX123', 'Mock Name', '2029-12-31');


INSERT INTO shipping_company (shipping_id, name, contact_phone) VALUES
('SHIP01', 'Speedy Delivery Ghana', '+233302000001'),
('SHIP02', 'EcoTransit Logistics', '+233302000002'),
('SHIP03', 'DropX Africa', '+233302000003'),
('SHIP04', 'Aramex Ghana', '+233302000004'),
('SHIP05', 'DHL Express Local', '+233302000005');

INSERT INTO delivery (delivery_id, order_id, delivery_status, estimated_delivery_date, address_id, shipping_id) VALUES
('DEL01', 'ORD01', 'delivered', '2026-08-06', 'ADR001', 'SHIP01'),('DEL02', 'ORD02', 'sent to port', '2026-08-06', 'ADR002', 'SHIP02'),('DEL03', 'ORD03', 'on the way', '2026-08-06', 'ADR003', 'SHIP03'),('DEL04', 'ORD04', 'delivered', '2026-08-06', 'ADR004', 'SHIP04'),('DEL05', 'ORD05', 'sent to port', '2026-08-06', 'ADR005', 'SHIP05'),('DEL06', 'ORD06', 'on the way', '2026-08-06', 'ADR006', 'SHIP01'),('DEL07', 'ORD07', 'delivered', '2026-08-06', 'ADR007', 'SHIP02'),('DEL08', 'ORD08', 'sent to port', '2026-08-06', 'ADR008', 'SHIP03'),('DEL09', 'ORD09', 'on the way', '2026-08-06', 'ADR009', 'SHIP04'),('DEL10', 'ORD10', 'delivered', '2026-08-06', 'ADR010', 'SHIP05'),('DEL11', 'ORD11', 'sent to port', '2026-08-06', 'ADR011', 'SHIP01'),('DEL12', 'ORD12', 'on the way', '2026-08-06', 'ADR012', 'SHIP02'),('DEL13', 'ORD13', 'delivered', '2026-08-06', 'ADR013', 'SHIP03'),('DEL14', 'ORD14', 'sent to port', '2026-08-06', 'ADR014', 'SHIP04'),('DEL15', 'ORD15', 'on the way', '2026-08-06', 'ADR015', 'SHIP05'),('DEL16', 'ORD16', 'delivered', '2026-08-06', 'ADR016', 'SHIP01'),('DEL17', 'ORD17', 'sent to port', '2026-08-06', 'ADR017', 'SHIP02'),('DEL18', 'ORD18', 'on the way', '2026-08-06', 'ADR018', 'SHIP03'),('DEL19', 'ORD19', 'delivered', '2026-08-06', 'ADR019', 'SHIP04'),('DEL20', 'ORD20', 'sent to port', '2026-08-06', 'ADR020', 'SHIP05'),('DEL21', 'ORD21', 'on the way', '2026-08-06', 'ADR021', 'SHIP01'),('DEL22', 'ORD22', 'delivered', '2026-08-06', 'ADR022', 'SHIP02'),('DEL23', 'ORD23', 'sent to port', '2026-08-06', 'ADR023', 'SHIP03'),('DEL24', 'ORD24', 'on the way', '2026-08-06', 'ADR024', 'SHIP04'),('DEL25', 'ORD25', 'delivered', '2026-08-06', 'ADR025', 'SHIP05'),('DEL26', 'ORD26', 'sent to port', '2026-08-06', 'ADR026', 'SHIP01'),('DEL27', 'ORD27', 'on the way', '2026-08-06', 'ADR027', 'SHIP02'),('DEL28', 'ORD28', 'delivered', '2026-08-06', 'ADR028', 'SHIP03'),('DEL29', 'ORD29', 'sent to port', '2026-08-06', 'ADR029', 'SHIP04'),('DEL30', 'ORD30', 'on the way', '2026-08-06', 'ADR030', 'SHIP05');



INSERT INTO review (review_id, product_id, customer_id, rating, review_date, comment) VALUES
('REV01', 'PROD01', 'CUST00', 5, '2026-08-05', 'Highly functional product'),('REV02', 'PROD03', 'CUST02', 5, '2026-08-05', 'Highly functional product'),('REV03', 'PROD05', 'CUST03', 5, '2026-08-05', 'Highly functional product'),('REV04', 'PROD07', 'CUST04', 5, '2026-08-05', 'Highly functional product'),('REV05', 'PROD09', 'CUST05', 5, '2026-08-05', 'Highly functional product'),('REV06', 'PROD11', 'CUST06', 5, '2026-08-05', 'Highly functional product'),('REV07', 'PROD13', 'CUST07', 5, '2026-08-05', 'Highly functional product'),('REV08', 'PROD15', 'CUST08', 5, '2026-08-05', 'Highly functional product'),('REV09', 'PROD17', 'CUST09', 5, '2026-08-05', 'Highly functional product'),('REV10', 'PROD19', 'CUST10', 5, '2026-08-05', 'Highly functional product'),('REV11', 'PROD21', 'CUST11', 5, '2026-08-05', 'Highly functional product'),('REV12', 'PROD23', 'CUST12', 5, '2026-08-05', 'Highly functional product'),('REV13', 'PROD25', 'CUST13', 5, '2026-08-05', 'Highly functional product'),('REV14', 'PROD27', 'CUST14', 5, '2026-08-05', 'Highly functional product'),('REV15', 'PROD29', 'CUST15', 5, '2026-08-05', 'Highly functional product'),('REV16', 'PROD01', 'CUST16', 5, '2026-08-05', 'Highly functional product'),('REV17', 'PROD03', 'CUST17', 5, '2026-08-05', 'Highly functional product'),('REV18', 'PROD05', 'CUST18', 5, '2026-08-05', 'Highly functional product'),('REV19', 'PROD07', 'CUST19', 5, '2026-08-05', 'Highly functional product'),('REV20', 'PROD09', 'CUST20', 5, '2026-08-05', 'Highly functional product'),('REV21', 'PROD11', 'CUST21', 5, '2026-08-05', 'Highly functional product'),('REV22', 'PROD13', 'CUST22', 5, '2026-08-05', 'Highly functional product'),('REV23', 'PROD15', 'CUST23', 5, '2026-08-05', 'Highly functional product'),('REV24', 'PROD17', 'CUST24', 5, '2026-08-05', 'Highly functional product'),('REV25', 'PROD19', 'CUST25', 5, '2026-08-05', 'Highly functional product'),('REV26', 'PROD21', 'CUST26', 5, '2026-08-05', 'Highly functional product'),('REV27', 'PROD23', 'CUST27', 5, '2026-08-05', 'Highly functional product'),('REV28', 'PROD25', 'CUST28', 5, '2026-08-05', 'Highly functional product'),('REV29', 'PROD27', 'CUST29', 5, '2026-08-05', 'Highly functional product'),('REV30', 'PROD29', 'CUST30', 5, '2026-08-05', 'Highly functional product');


