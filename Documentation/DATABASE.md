# Database Schema and Logic Reference

The database is built on **MariaDB / MySQL**. It implements an e-commerce data model supporting roles, constraints, views, stored procedures, custom functions, and triggers.

---

## 1. Relational Table Schema

The tables are defined with the following column specifications, indices, and integrity constraints.

### `customer`
Tracks customer profile registration and account active status.
* **`customer_id`** (`VARCHAR(36)`): Primary Key (UUID format).
* **`f_name`** (`VARCHAR(20)`): First name.
* **`l_name`** (`VARCHAR(20)`): Last name.
* **`phone_number`** (`VARCHAR(13)`): Primary phone.
* **`email`** (`VARCHAR(100)`): Unique user email.
* **`is_active`** (`BOOLEAN`): Activation flag. Allows administrators to suspend/reactivate accounts (Default: `TRUE`).

### `customer_credentials`
Secures authentication details.
* **`customer_id`** (`VARCHAR(36)`): Primary Key & Foreign Key pointing to `customer(customer_id)` (Cascade on delete).
* **`password_hash`** (`VARCHAR(255)`): Hashed string (pre-hashed with `bcrypt`).

### `vendor`
* **`vendor_id`** (`VARCHAR(36)`): Primary Key.
* **`vendor_name`** (`VARCHAR(50)`): Company name.
* **`email`** (`VARCHAR(100)`): Unique contact email.
* **`phone_number`** (`VARCHAR(13)`): Contact number.
* **`is_active`** (`BOOLEAN`): Suspension state (Default: `TRUE`).

### `vendor_credentials`
* **`vendor_id`** (`VARCHAR(36)`): Primary & Foreign Key pointing to `vendor(vendor_id)` (Cascade on delete).
* **`password_hash`** (`VARCHAR(255)`): Pre-hashed password.

### `product`
Tracks active product listing details.
* **`product_id`** (`VARCHAR(36)`): Primary Key.
* **`vendor_id`** (`VARCHAR(36)`): Foreign Key pointing to `vendor(vendor_id)`.
* **`product_name`** (`VARCHAR(50)`): Name.
* **`description`** (`VARCHAR(200)`): Specification details.
* **`price`** (`DECIMAL(10,2)`): Must be `>= 0`.
* **`stock_quantity`** (`INT`): Real-time inventory. Must be `>= 0`.
* **`product_type`** (`VARCHAR(10)`): Constrained to `'beauty'` or `'fashion'`.
* **`image_url`** (`VARCHAR(2048)`): Path to image resource.
* **`is_active`** (`BOOLEAN`): Soft-delete indicator (Default: `TRUE`).

### Product Sub-Types
To avoid redundant fields or NULL columns, specific categories inherit from the `product` super-type via primary key relations:
* **`fashion`**: Key `product_id` (Foreign Key to `product`). Attributes: `Color`, `Material`, `Size`, `Gender_category` (must be `men`, `women`, `unisex`, `kids`).
* **`beauty`**: Key `product_id` (Foreign Key to `product`). Attributes: `skin_type`, `volume_weight`, `Is_organic` (`BOOLEAN`).

### `cart`
Enforces a strict 1-to-1 link between customers and their shopping carts.
* **`cart_id`** (`VARCHAR(36)`): Primary Key.
* **`customer_id`** (`VARCHAR(36)`): Foreign Key pointing to `customer(customer_id)`. Must be unique.

### `cart_items`
Tracks multiple items queued inside a shopping cart.
* **`product_id`**, **`cart_id`**: Composite Primary Key.
* **`quantity`** (`INT`): Items to buy. Must be `> 0`.
* **`added_date`** (`DATE`).

### `orders`
Logs final, customer checkout transactions.
* **`order_id`** (`VARCHAR(36)`): Primary Key.
* **`customer_id`** (`VARCHAR(36)`): Foreign Key pointing to `customer(customer_id)`.
* **`order_date`** (`DATETIME`).
* **`subtotal`** (`DECIMAL(10,2)`): Cost of goods.
* **`shipping_fee`** (`DECIMAL(10,2)`): Delivery cost.

### `order_items`
Tracks items in each order.
* **`product_id`**, **`order_id`**: Composite Primary Key.
* **`quantity`** (`INT`).
* **`added_date`** (`DATE`).
* **`is_dispatched`** (`BOOLEAN`): Tracks whether the individual vendor has shipped their product to the port (Default: `FALSE`).

### `payment` & Payment Sub-Types
Processes transaction records.
* **`payment`** (Supertype): tracks `payment_id`, `customer_id`, `amount`, `payment_date`, `payment_type` (`card`, `bank transfer`, `mobile money`), and `order_id`.
* **`bank_transfer`** (Subtype): stores `bank_name`, `account_number`, and `account_name`.
* **`mobile_money`** (Subtype): stores `network` (e.g. MTN, Telecel), `phone_number`, and `account_name`.
* **`card`** (Subtype): stores `token_id`, `card_num` (masked/tokenized), `card_name`, and `Expiry_date`.

### `shipping_company` & `shipping_credentials`
Defines carrier firms.
* `shipping_company`: tracks `shipping_id`, `name`, `email`, and `contact_phone`.
* `shipping_credentials`: tracks `shipping_id` and `password_hash`.

### `delivery`
Logs logistics routing paths.
* **`delivery_id`** (`VARCHAR(36)`): Primary Key.
* **`order_id`** (`VARCHAR(36)`): Foreign Key.
* **`delivery_status`** (`VARCHAR(50)`): Default `'pending'`. Allowed states: `pending`, `in port`, `on the way`, `delivered`.
* **`estimated_delivery_date`** (`DATE`).
* **`address_id`** (`VARCHAR(36)`): Shipping location.
* **`shipping_id`** (`VARCHAR(36)`): Carrier assigned.

---

## 2. Views (Reporting & Analytics)

To protect sensitive core tables and simplify aggregate dashboard routines:

1. **`vw_carrier_performance`**:
   Aggregates delivery stats: volume, active shipments, completed deliveries, and total vs. completed logistics revenues.
2. **`vw_order_details_full`**:
   Consolidates customer profiles, product specifications, quantities, carrier companies, dispatch statuses, and payment modes into a single canonical query.
3. **`vw_admin_platform_summary`**:
   Presents single-row metrics: total customers, vendors, overall platform orders, active suspended metrics, and Gross Merchandise Value (GMV).
4. **`vw_vendor_order_fulfillment`**:
   Helps vendors monitor pending orders, item specifications, customer details, and dispatch statuses.
5. **`vw_customer_order_history`**:
   Exposes customer checkout listings, shipping carrier names, tracking numbers, and delivery statuses.
6. **`vw_product_ratings`**:
   Aggregates review counts and product average ratings.
7. **`vw_product_sales`**:
   Summarizes total unit sales volumes and gross revenue generated per product.

---

## 3. Stored Procedures & Stored Functions

### Custom Functions
- **`fn_calculate_order_total(order_id)`**:
  Combines the order `subtotal` and `shipping_fee` to return the grand billing total.
- **`fn_get_product_average_rating(product_id)`**:
  Computes the average rating (`ROUND(AVG, 2)`) for any product using `review` entries.

### Stored Procedures
- **`sp_add_to_cart(customer_id, product_id, quantity)`**:
  Validates inventory and inserts/updates items in the shopping cart.
- **`sp_place_order(order_id, customer_id, shipping_fee, shipping_id, address_id, payment_id, payment_type, ...)`**:
  Transitions a customer's active shopping cart items into an official order, generates a shipping delivery tracking entry, creates a matching payment record, and clears the cart items.
- **`sp_update_delivery_status(delivery_id, status)`**:
  Updates the delivery tracking status securely with strict check constraints.
- **`sp_update_order_item_status(order_id, product_id, is_dispatched)`**:
  Allows vendors to toggle order item dispatch statuses.
- **`sp_delete_customer_address(address_id, customer_id)`**:
  Allows customers to remove addresses from their profile address book safely.
- **`sp_add_product_review(review_id, product_id, customer_id, rating, comment)`**:
  Allows customers to review products with rating boundaries (1–5).

---

## 4. Automated Database Triggers

These triggers enforce strict transactional integrity rules:

- **`trg_check_initial_stock_before_insert`** (`BEFORE INSERT ON product`):
  Guarantees that a product must have at least 1 unit of stock when it is initially created.
- **`trg_reduce_stock_after_order_item`** (`AFTER INSERT ON order_items`):
  Deducts purchased quantities from the `product` stock catalog.
- **`trg_check_stock` & `trg_check_stock_onupdate`** (`BEFORE INSERT/UPDATE ON cart_items`):
  Ensures customer cart requests do not exceed available product inventory.
- **`trg_set_review_date`** (`BEFORE INSERT ON review`):
  Automatically populates review timestamps with the current database date.
- **`trg_auto_update_delivery_status_to_port`** (`AFTER UPDATE ON order_items`):
  Checks if all items in an order are marked `is_dispatched = TRUE`. Once fulfilled by all vendors, the order's `delivery_status` is automatically promoted from `pending` to `in port` (ready for courier collection).
- **`trg_evict_cart_items_on_soft_delete`** (`AFTER UPDATE ON product`):
  If a product is deactivated (`is_active = FALSE`), it is automatically deleted from all active shopping carts.
- **`trg_on_vendor_status_change`** (`AFTER UPDATE ON vendor`):
  Handles account suspensions. If a vendor is suspended (`is_active = FALSE`), all their products are deactivated and evited from carts. If reactivated, their catalog is restored.

---

## 5. Security (Roles & Privileges)

Access to database schemas is structured around role-based privileges:
- **`marketplace_admin`**: Full `SELECT`, `INSERT`, `UPDATE`, `DELETE` access to all database tables.
- **`marketplace_vendor`**: Select on order items, insert/update on products/subtypes, and write privileges to update order dispatch statuses.
- **`marketplace_customer`**: Access restricted to cart management, profile settings, reviews, and reading product lists.
- **`marketplace_shipping_company`**: Restricted to reading delivery routes (using a secure column view `Shipping_Delivery_Address` to preserve customer address detail privacy) and updating delivery tracking statuses.
