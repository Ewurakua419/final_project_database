# Marketplace REST API Reference

The backend API is implemented as a Flask service running on `http://127.0.0.1:5001`. It handles JSON requests and responses and secures operations using JWT-based token authentication.

---

## Authentication

Authentication is token-based. Upon successful login or registration, the API returns a JWT token. This token must be included in the HTTP headers of all protected requests:

```http
Authorization: Bearer <your_jwt_token_here>
```

---

## 1. Customer Endpoints

### Register Customer
* **Endpoint:** `POST /register`
* **Auth Required:** No
* **Request Body:**
  ```json
  {
    "email": "customer@email.com",
    "password": "customerpassword",
    "first_name": "Kofi",
    "last_name": "Mensah",
    "phone_number": "+233241234500"
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "message": "Account created successfully",
    "user_id": "CUST-UUID-STRING",
    "token": "JWT-TOKEN-STRING"
  }
  ```

### Login Customer
* **Endpoint:** `POST /login`
* **Auth Required:** No
* **Request Body:**
  ```json
  {
    "email": "customer@email.com",
    "password": "customerpassword"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "message": "Login successful",
    "token": "JWT-TOKEN-STRING"
  }
  ```

### Get Profile
* **Endpoint:** `GET /customer/profile`
* **Auth Required:** Yes
* **Response (200 OK):**
  ```json
  {
    "customer_id": "CUST-UUID-STRING",
    "email": "customer@email.com",
    "first_name": "Kofi",
    "last_name": "Mensah",
    "phone_number": "+233241234500",
    "addresses": [
      {
        "address_id": "ADDR-UUID-STRING",
        "city": "Accra",
        "street": "12 Boundary Road",
        "landmark": "Near Shell Station"
      }
    ]
  }
  ```

### Add Address
* **Endpoint:** `POST /customer/addresses`
* **Auth Required:** Yes
* **Request Body:**
  ```json
  {
    "city": "Accra",
    "street": "12 Boundary Road",
    "landmark": "Near Shell Station"
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "address_id": "ADDR-UUID-STRING",
    "city": "Accra",
    "street": "12 Boundary Road",
    "landmark": "Near Shell Station"
  }
  ```

### Delete Address
* **Endpoint:** `DELETE /customer/addresses/<address_id>`
* **Auth Required:** Yes
* **Response (200 OK):**
  ```json
  {
    "message": "Address removed successfully"
  }
  ```

---

## 2. Product Catalog Endpoints

### Get All Products
* **Endpoint:** `GET /product-items`
* **Auth Required:** No
* **Response (200 OK):**
  ```json
  {
    "products": [
      {
        "product_id": "PROD-UUID-1",
        "product_name": "Kente Fabric Handwoven",
        "description": "Authentic Volta Kente Cloth",
        "price": 150.00,
        "stock_quantity": 10,
        "product_type": "fashion",
        "image": "http://127.0.0.1:5001/static/uploads/image.png"
      }
    ]
  }
  ```

### Get Product Details
* **Endpoint:** `GET /product-items/<product_id>`
* **Auth Required:** No
* **Response (200 OK):**
  ```json
  {
    "product_id": "PROD-UUID-1",
    "product_name": "Kente Fabric Handwoven",
    "price": 150.00,
    "image": "http://127.0.0.1:5001/static/uploads/image.png",
    "product_type": "fashion",
    "description": "Authentic Volta Kente Cloth",
    "stock_quantity": 10,
    "attributes": {
      "Color": "Multicolor",
      "Material": "Cotton/Silk Blend",
      "Size": "L",
      "Gender_category": "unisex"
    }
  }
  ```

---

## 3. Shopping Cart & Checkout Endpoints

### Get Cart
* **Endpoint:** `GET /cart`
* **Auth Required:** Yes
* **Response (200 OK):**
  ```json
  {
    "cart": [
      {
        "product": {
          "product_id": "PROD-UUID-1",
          "product_name": "Kente Fabric",
          "price": 150.00,
          "image": "http://127.0.0.1:5001/static/uploads/image.png"
        },
        "quantity": 2,
        "added_date": "2026-08-17"
      }
    ],
    "subtotal": 300.00
  }
  ```

### Add to Cart
* **Endpoint:** `POST /cart`
* **Auth Required:** Yes
* **Request Body:**
  ```json
  {
    "product_id": "PROD-UUID-1",
    "quantity": 1
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "message": "Item added to cart successfully"
  }
  ```

### Remove from Cart
* **Endpoint:** `DELETE /cart/<product_id>`
* **Auth Required:** Yes
* **Response (200 OK):**
  ```json
  {
    "message": "Item removed from cart"
  }
  ```

### Update Item Quantity
* **Endpoint:** `PUT /cart/<product_id>/quantity`
* **Auth Required:** Yes
* **Request Body:**
  ```json
  {
    "quantity": 3
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "message": "Cart updated successfully"
  }
  ```

### Checkout Cart
* **Endpoint:** `POST /checkout`
* **Auth Required:** Yes
* **Request Body:**
  ```json
  {
    "shipping_address": "ADDR-UUID-STRING",
    "shipping_id": "SHIP-COMPANY-UUID",
    "shipping_fee": 15.00,
    "payment_details": {
      "payment_type": "mobile money",
      "network": "MTN",
      "phone_number": "+233244111222",
      "account_name": "Kofi Mensah"
    }
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "order_id": "ORDER-UUID-STRING",
    "customer_id": "CUST-UUID-STRING",
    "order_date": "2026-08-17T09:21:40",
    "subtotal": 300.00,
    "shipping_fee": 15.00
  }
  ```

### Get Order History
* **Endpoint:** `GET /orders`
* **Auth Required:** Yes
* **Response (200 OK):**
  ```json
  {
    "orders": [
      {
        "order_id": "ORDER-UUID-STRING",
        "order_date": "2026-08-17T09:21:40",
        "subtotal": 300.00,
        "shipping_fee": 15.00,
        "grand_total": 315.00,
        "items": [
          {
            "product_name": "Kente Fabric",
            "quantity": 2,
            "price": 150.00,
            "is_dispatched": false
          }
        ]
      }
    ]
  }
  ```

---

## 4. Vendor Endpoints

### Register Vendor
* **Endpoint:** `POST /vendor/register`

### Login Vendor
* **Endpoint:** `POST /vendor/login`

### Add Product
* **Endpoint:** `POST /vendor/products`
* **Auth Required:** Yes
* **Request Body:**
  ```json
  {
    "product_name": "Organic Shea Butter",
    "description": "Raw, organic unrefined shea butter",
    "price": 45.00,
    "stock_quantity": 50,
    "product_type": "beauty",
    "image_url": "shea_butter.png",
    "skin_type": "dry",
    "volume_weight": "500g",
    "Is_organic": true
  }
  ```

### Update Order Item Dispatch Status
* **Endpoint:** `PUT /vendor/orders/<order_id>/items/<product_id>/status`
* **Auth Required:** Yes
* **Request Body:**
  ```json
  {
    "is_dispatched": true
  }
  ```

---

## 5. Shipping & Logistics Endpoints

### Get Assigned Deliveries
* **Endpoint:** `GET /shipping/deliveries`
* **Auth Required:** Yes (Carrier Token)

### Update Delivery Status
* **Endpoint:** `PUT /shipping/deliveries/<delivery_id>`
* **Auth Required:** Yes (Carrier Token)
* **Request Body:**
  ```json
  {
    "status": "on the way"
  }
  ```

---

## 6. Admin Endpoints

### Admin Login
* **Endpoint:** `POST /admin/login`

### Toggle User Activation Status (Suspend / Reactivate)
* **Endpoint:** `PUT /admin/users/<user_id>/toggle-status`
* **Auth Required:** Yes (Admin Token)
* **Request Body:**
  ```json
  {
    "user_type": "vendor" 
  }
  ```
