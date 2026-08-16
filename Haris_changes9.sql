-- Haris_changes9.sql
-- Database migration to remove cart_id redundancy in orders and enforce 1-to-1 cart-customer uniqueness

USE ecommerce;

-- 1. Enforce unique constraint on cart.customer_id to guarantee 1-to-1 relationship
ALTER TABLE cart ADD CONSTRAINT uq_cart_customer UNIQUE (customer_id);

-- 2. Drop the redundant cart_id foreign key constraint and column from the orders table
-- Dropping foreign key constraint '1' (which was defined for cart_id)
ALTER TABLE orders DROP FOREIGN KEY `1`;

-- Drop the redundant cart_id column
ALTER TABLE orders DROP COLUMN cart_id;
