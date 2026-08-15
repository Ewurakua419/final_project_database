-- ==============================================================================
-- Haris_changes3.sql
-- Purpose: Add email & credentials support for Shipping Companies (Logistics)
-- ==============================================================================

USE ecommerce;

-- 1. Add email column to shipping_company
ALTER TABLE shipping_company 
ADD COLUMN IF NOT EXISTS email VARCHAR(100) NULL AFTER name;

-- 2. Populate default emails for existing shipping companies
UPDATE shipping_company SET email = 'speedy@shipping.gh' WHERE shipping_id = 'SHIP01';
UPDATE shipping_company SET email = 'ecotransit@shipping.gh' WHERE shipping_id = 'SHIP02';
UPDATE shipping_company SET email = 'dropx@shipping.gh' WHERE shipping_id = 'SHIP03';
UPDATE shipping_company SET email = 'aramex@shipping.gh' WHERE shipping_id = 'SHIP04';
UPDATE shipping_company SET email = 'dhl@shipping.gh' WHERE shipping_id = 'SHIP05';

-- 3. Enforce NOT NULL and UNIQUE constraints on shipping email
ALTER TABLE shipping_company 
MODIFY COLUMN email VARCHAR(100) NOT NULL;

ALTER TABLE shipping_company 
ADD CONSTRAINT uq_shipping_company_email UNIQUE (email);

-- 4. Create shipping_credentials table
CREATE TABLE IF NOT EXISTS shipping_credentials (
    shipping_id VARCHAR(6) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    FOREIGN KEY (shipping_id) REFERENCES shipping_company(shipping_id) ON DELETE CASCADE
);

-- 5. Insert default credentials for existing couriers (Default password: password123)
INSERT INTO shipping_credentials (shipping_id, password_hash) VALUES
('SHIP01', 'password123'),
('SHIP02', 'password123'),
('SHIP03', 'password123'),
('SHIP04', 'password123'),
('SHIP05', 'password123')
ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash);
