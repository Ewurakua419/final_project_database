-- new_ddl.sql
-- Unified Database Schema Definition

CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

-- 1. Customer table (supporting suspension status and full UUIDs)
CREATE TABLE customer (
    customer_id VARCHAR(36) PRIMARY KEY,
    f_name VARCHAR(20),
    l_name VARCHAR(20),
    phone_number VARCHAR(13),
    email VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_customer_email UNIQUE (email)
);

-- 2. Customer Credentials
CREATE TABLE customer_credentials (
    customer_id VARCHAR(36) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE
);

-- 3. Vendor table (supporting suspension status and full UUIDs)
CREATE TABLE vendor (
    vendor_id VARCHAR(36) PRIMARY KEY,
    vendor_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone_number VARCHAR(13),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_vendor_email UNIQUE (email)
);

-- 4. Vendor Credentials
CREATE TABLE vendor_credentials (
    vendor_id VARCHAR(36) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id) ON DELETE CASCADE
);

-- 5. Product table (supporting soft delete, stock checks, and image URLs)
CREATE TABLE product (
    product_id VARCHAR(36) PRIMARY KEY,
    vendor_id VARCHAR(36) NOT NULL,
    product_name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL,
    product_type VARCHAR(10) NOT NULL,
    image_url VARCHAR(2048),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id),
    CONSTRAINT chk_product_type CHECK (product_type IN ('beauty', 'fashion')),
    CONSTRAINT chk_price CHECK (price >= 0),
    CONSTRAINT chk_product_stock CHECK (stock_quantity >= 0)
);

-- 6. Review table
CREATE TABLE review (
    review_id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36),
    customer_id VARCHAR(36) NOT NULL,
    rating INT NOT NULL,
    review_date DATE NOT NULL,
    comment TEXT,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE,
    CONSTRAINT chk_review_rating CHECK (rating BETWEEN 1 AND 5)
);

-- 7. Cart table (enforcing strict 1-to-1 relationship with customer)
CREATE TABLE cart (
    cart_id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE,
    CONSTRAINT uq_cart_customer UNIQUE (customer_id)
);

-- 8. Cart Items (supporting primary key constraint and check stock checks)
CREATE TABLE cart_items (
    product_id VARCHAR(36) NOT NULL,
    cart_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL,
    added_date DATE NOT NULL,
    PRIMARY KEY (product_id, cart_id),
    FOREIGN KEY (cart_id) REFERENCES cart(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    CONSTRAINT chk_cart_quantity CHECK (quantity > 0)
);

-- 9. Orders table (decoupled from cart_id redundancy)
CREATE TABLE orders (
    order_id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    order_date DATETIME NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    shipping_fee DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT chk_order_subtotal CHECK (subtotal >= 0.00),
    CONSTRAINT chk_order_shipping CHECK (shipping_fee >= 0.00)
);

-- 10. Payment Supertype
CREATE TABLE payment (
    payment_id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    order_id VARCHAR(36) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT chk_payment_type CHECK (payment_type IN ('card','bank transfer', 'mobile money')),
    CONSTRAINT chk_payment_amount CHECK (amount >= 0.00)
);

-- 11. Address book
CREATE TABLE address (
    address_id VARCHAR(36) PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    Landmark VARCHAR(100),
    street_address VARCHAR(255) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE
);

-- 12. Shipping Company carriers
CREATE TABLE shipping_company (
    shipping_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(30),
    CONSTRAINT uq_shipping_company_email UNIQUE (email)
);

-- 12b. Shipping Credentials
CREATE TABLE shipping_credentials (
    shipping_id VARCHAR(36) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    FOREIGN KEY (shipping_id) REFERENCES shipping_company(shipping_id) ON DELETE CASCADE
);

-- 13. Delivery shipment routing (defaulting status to pending)
CREATE TABLE delivery (
    delivery_id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    delivery_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    estimated_delivery_date DATE,
    address_id VARCHAR(36),
    shipping_id VARCHAR(36),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (address_id) REFERENCES address(address_id) ON DELETE SET NULL,
    FOREIGN KEY (shipping_id) REFERENCES shipping_company(shipping_id),
    CONSTRAINT chk_delivery_status CHECK (delivery_status IN ('pending', 'in port', 'on the way', 'delivered'))
);

-- 14. Bank Transfer details
CREATE TABLE bank_transfer (
    payment_id VARCHAR(36) PRIMARY KEY,
    bank_name VARCHAR(60) NOT NULL,
    account_number VARCHAR(30) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (payment_id) REFERENCES payment(payment_id) ON DELETE CASCADE
);

-- 15. Mobile Money details
CREATE TABLE mobile_money (
    payment_id VARCHAR(36) PRIMARY KEY,
    network VARCHAR(60) NOT NULL,
    phone_number VARCHAR(13) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (payment_id) REFERENCES payment(payment_id) ON DELETE CASCADE
);

-- 16. Card details (supporting CVV and proper token sizes)
CREATE TABLE card (
    payment_id VARCHAR(36) PRIMARY KEY,
    token_id VARCHAR(36) NOT NULL,
    card_num VARCHAR(19) NOT NULL,
    card_name VARCHAR(100) NOT NULL,
    Expiry_date DATE NOT NULL,
    FOREIGN KEY (payment_id) REFERENCES payment(payment_id) ON DELETE CASCADE
);

-- 17. Fashion subtype
CREATE TABLE fashion (
    product_id VARCHAR(36) PRIMARY KEY,
    Color VARCHAR(40),
    Material VARCHAR(100),
    Size VARCHAR(5),
    Gender_category VARCHAR(15),
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE,
    CONSTRAINT chk_fashion_gender CHECK (gender_category IN ('men', 'women', 'unisex', 'kids'))
);

-- 18. Beauty subtype
CREATE TABLE beauty (
    product_id VARCHAR(36) PRIMARY KEY,
    skin_type VARCHAR(40),
    volume_weight VARCHAR(100),
    Is_organic BOOLEAN,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
);

-- 19. Order Items (supporting boolean vendor is_dispatched states)
CREATE TABLE order_items (
    product_id VARCHAR(36) NOT NULL,
    order_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL,
    added_date DATE NOT NULL,
    is_dispatched BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (product_id, order_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    CONSTRAINT chk_orderitems_quantity CHECK (quantity > 0)
);
