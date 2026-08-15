-- ==============================================================================
-- update_passwords.sql
-- Purpose: Update all initial mock passwords to valid bcrypt hashes so users can log in
-- ==============================================================================

USE ecommerce;

-- 1. Update all vendors to have the password 'vendor123'
UPDATE vendor_credentials 
SET password_hash = '$2b$12$FOlLPYxyeH1gdQ0dxeN7W.fLeXCTYAnLhFTGxkxcQ3Xbdk2MZar.y';

-- 2. Update all customers/users to have the password 'password123'
UPDATE customer_credentials 
SET password_hash = '$2b$12$B8.v.r62otrYMGilnKwopuc1h/NWlKK00e6LEjxLQ8hf9IICnW1p.';

-- 3. Update all shipping companies to have the password 'password123'
UPDATE shipping_credentials 
SET password_hash = '$2b$12$B8.v.r62otrYMGilnKwopuc1h/NWlKK00e6LEjxLQ8hf9IICnW1p.';

-- Note: The admin portal does not store its credentials in the DB; 
-- login is handled directly with email 'admin' and password 'admin'.
