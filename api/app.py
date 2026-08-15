"""
==============================================================================
Marketplace Mock API (Refactored)
==============================================================================
Provides RESTful API endpoints for Customers, Vendors, Logistics Partners,
and Administrators. Powered by Flask, MariaDB, and JWT Authentication.
==============================================================================
"""

import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt

# Include root directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import auth
from auth import SECRET_KEY
import database
from service.marketplace import Marketplace
from model.address import Address

# ------------------------------------------------------------------------------
# App Initialization & Configuration
# ------------------------------------------------------------------------------
marketplace = Marketplace(name="Ashesi E-Commerce Marketplace")

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "http://127.0.0.1:5001",
            "http://localhost:5001",
            "http://127.0.0.1:8000",
            "http://localhost:8000"
        ]
    }
})


# ==============================================================================
# SECTION 1: AUTHENTICATION DECORATORS & UTILITIES
# ==============================================================================

def token_required(f):
    """Protects customer-facing endpoints requiring a valid customer JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication token missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data["user_id"][:6]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired. Please log in again."}), 401
        except (jwt.InvalidTokenError, KeyError):
            return jsonify({"error": "Invalid authentication token"}), 401
            
        return f(current_user_id, *args, **kwargs)
    return decorated


def vendor_token_required(f):
    """Protects vendor-facing endpoints requiring a valid vendor JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication token missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_vendor_id = data["vendor_id"][:6]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            return jsonify({"error": "Unauthorized: Invalid or expired vendor session"}), 401
            
        return f(current_vendor_id, *args, **kwargs)
    return decorated


def shipping_token_required(f):
    """Protects logistics partner endpoints requiring a valid courier JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication token missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_shipping_id = data["shipping_id"][:6]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            return jsonify({"error": "Unauthorized: Invalid or expired shipping session"}), 401
            
        return f(current_shipping_id, *args, **kwargs)
    return decorated


def admin_token_required(f):
    """Protects executive endpoints requiring admin privilege."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication token missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if data.get("admin_id") != "SYS_ADMIN":
                return jsonify({"error": "Forbidden: Admin privileges required"}), 403
        except Exception:
            return jsonify({"error": "Unauthorized: Invalid admin session"}), 401
            
        return f(*args, **kwargs)
    return decorated


def get_image_url(image_path):
    """Formats relative or local image paths to absolute URLs."""
    if not image_path:
        return ""
    if image_path.startswith(("http://", "https://", "data:image")):
        return image_path
    base_url = request.host_url
    return f"{base_url}static/{image_path}"


# ==============================================================================
# SECTION 2: CUSTOMER AUTHENTICATION & PROFILE
# ==============================================================================

@app.route("/register", methods=["POST"])
def register_customer():
    """Register a new customer account."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    phone_number = data.get("phone_number", "")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    name = f"{first_name} {last_name}".strip() or email.split("@")[0]
    user = marketplace.registerCustomer(
        name, password, email,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number
    )
    
    if user is None:
        return jsonify({"error": "An account with this email already exists"}), 409
    
    payload = {
        "user_id": user.unique_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Account created successfully", "user_id": user.unique_id, "token": token}), 201


@app.route("/login", methods=["POST"])
def login_customer():
    """Customer authentication."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    customer = marketplace.login(email, password)
    if not customer:
        return jsonify({"error": "Invalid email or password"}), 401
        
    payload = {
        "user_id": customer.unique_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Login successful", "token": token}), 200


@app.route("/customer/profile", methods=["GET"])
@token_required
def get_customer_profile(current_user_id):
    """Retrieve customer details and saved address book."""
    customer = marketplace.finduser_by_id(current_user_id)
    if not customer:
        return jsonify({"error": "Customer account not found"}), 404
        
    addr_list = database.get_addresses_by_customer(current_user_id)
    return jsonify({
        "customer_id": customer.unique_id,
        "email": customer.email,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone_number": customer.phone_number,
        "addresses": addr_list
    }), 200


@app.route("/customer/profile", methods=["PUT"])
@token_required
def update_customer_profile(current_user_id):
    """Update customer profile information."""
    data = request.get_json() or {}
    profile = marketplace.update_customer_profile(current_user_id, data)
    return jsonify(profile), 200


@app.route("/customer/addresses", methods=["POST"])
@token_required
def add_customer_address(current_user_id):
    """Add a new delivery address to the customer's address book."""
    data = request.get_json() or {}
    addr_obj = Address(
        city=data.get("city", ""),
        street_address=data.get("street", ""),
        landmark=data.get("landmark"),
        customer_id=current_user_id
    )
    database.add_address(addr_obj.to_dict())
    return jsonify(addr_obj.to_dict()), 201


@app.route("/customer/addresses/<address_id>", methods=["DELETE"])
@token_required
def delete_customer_address(current_user_id, address_id):
    """Delete an address securely with foreign key safety."""
    success = database.delete_address(address_id, current_user_id)
    if success:
        return jsonify({"message": "Address removed successfully"}), 200
    return jsonify({"error": "Address not found or does not belong to you"}), 404


# ==============================================================================
# SECTION 3: PRODUCT CATALOG & REVIEWS
# ==============================================================================

@app.route("/product-items", methods=["GET"])
def get_products():
    """Retrieve full catalog of marketplace products."""
    products = marketplace.get_all_products()
    processed = []
    for p in products:
        d = p.to_dict()
        d['image'] = get_image_url(d.get('image', ''))
        processed.append(d)
    return jsonify({"products": processed}), 200


@app.route("/product-items/<product_id>", methods=["GET"])
def get_product(product_id):
    """Retrieve detailed product specifications and attributes."""
    product = marketplace.findproduct(product_id)
    if product:
        d = product.to_dict()
        d['image'] = get_image_url(d.get('image', ''))
        return jsonify(d), 200
    return jsonify({"error": "Product not found"}), 404


@app.route("/product-items/<product_id>/reviews", methods=["GET"])
@app.route("/products/<product_id>/reviews", methods=["GET"])
def get_product_reviews(product_id):
    """Retrieve all verified customer reviews for a product."""
    reviews = marketplace.get_product_reviews(product_id)
    return jsonify({"reviews": [r.to_dict() for r in reviews]}), 200


@app.route("/product-items/<product_id>/reviews", methods=["POST"])
@app.route("/products/<product_id>/reviews", methods=["POST"])
@token_required
def add_product_review(current_user_id, product_id):
    """Add a customer review and rating (1-5 stars) for a product."""
    data = request.get_json() or {}
    rating = data.get("rating")
    comment = data.get("text") or data.get("comment", "")
    
    if not rating or not comment:
        return jsonify({"error": "Rating and comment are required"}), 400

    try:
        review = marketplace.add_product_review(product_id, current_user_id, comment, int(rating))
        return jsonify(review.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==============================================================================
# SECTION 4: CART, CHECKOUT & CUSTOMER ORDERS
# ==============================================================================

@app.route("/cart", methods=["GET"])
@token_required
def get_cart(current_user_id):
    """Retrieve current customer cart items and subtotal."""
    result = marketplace.get_cart(current_user_id)
    for item in result.get("cart", []):
        if "product" in item and "image" in item["product"]:
            item["product"]["image"] = get_image_url(item["product"]["image"])
    return jsonify(result), 200


@app.route("/cart", methods=["POST"])
@token_required
def add_to_cart(current_user_id):
    """Add an item to customer cart with stock availability validation."""
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id or quantity <= 0:
        return jsonify({"error": "Valid product ID and positive quantity are required"}), 400

    try:
        marketplace.add_to_cart(product_id, current_user_id, quantity)
        return jsonify({"message": "Item added to cart successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/cart/<product_id>", methods=["DELETE"])
@token_required
def remove_cart_item(current_user_id, product_id):
    """Remove a product from the customer's cart."""
    marketplace.remove_from_cart(product_id, current_user_id)
    return jsonify({"message": "Item removed from cart"}), 200


@app.route("/cart/<product_id>/quantity", methods=["PUT"])
@token_required
def update_cart_item_qty(current_user_id, product_id):
    """Update item quantity in cart."""
    data = request.get_json() or {}
    qty = int(data.get("quantity", 0))
    marketplace.remove_from_cart(product_id, current_user_id)
    if qty > 0:
        marketplace.add_to_cart(product_id, current_user_id, qty)
    return jsonify({"message": "Cart updated successfully"}), 200


@app.route("/checkout", methods=["POST"])
@token_required
def process_checkout(current_user_id):
    """Process customer order checkout, create delivery record and record payment."""
    data = request.get_json() or {}
    order = marketplace.checkout(
        current_user_id,
        shipping_address=data.get("shipping_address"),
        payment_details=data.get("payment_details"),
        shipping_fee=float(data.get("shipping_fee", 5.00)),
        shipping_id=data.get("shipping_id")
    )
    if order is None:
        return jsonify({"error": "Cart is empty or order could not be placed"}), 400
    return jsonify(order.to_dict()), 201


@app.route("/orders", methods=["GET"])
@token_required
def get_customer_orders(current_user_id):
    """Retrieve full order history for the logged-in customer."""
    orders = marketplace.get_customer_orders(current_user_id)
    return jsonify({"orders": orders}), 200


# ==============================================================================
# SECTION 5: VENDOR OPERATIONS & FULFILLMENT
# ==============================================================================

@app.route("/vendor/register", methods=["POST"])
def register_vendor():
    """Register a new vendor store."""
    data = request.get_json() or {}
    vendor = marketplace.registerVendor(
        data.get("vendor_name"),
        data.get("password"),
        data.get("email"),
        data.get("address", ""),
        phone_number=data.get("phone_number")
    )
    payload = {
        "vendor_id": vendor.unique_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Vendor registered successfully", "token": token}), 201


@app.route("/vendor/login", methods=["POST"])
def login_vendor():
    """Vendor store authentication."""
    data = request.get_json() or {}
    vendor = marketplace.loginVendor(data.get("email"), data.get("password"))
    if not vendor:
        return jsonify({"error": "Invalid email or password"}), 401
        
    payload = {
        "vendor_id": vendor.unique_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Login successful", "token": token}), 200


@app.route("/vendor/products", methods=["GET"])
@vendor_token_required
def get_vendor_products(current_vendor_id):
    """Retrieve all catalog products owned by the vendor."""
    products = marketplace.get_all_products()
    processed = []
    for p in products:
        if p.vendor_id == current_vendor_id:
            d = p.to_dict()
            d['image'] = get_image_url(d.get('image', ''))
            processed.append(d)
    return jsonify({"products": processed}), 200


@app.route("/vendor/products", methods=["POST"])
@vendor_token_required
def add_vendor_product(current_vendor_id):
    """Create a new product listing."""
    data = request.get_json() or {}
    new_product = marketplace.add_product(current_vendor_id, data)
    return jsonify({"message": "Product created successfully", "product": new_product.to_dict()}), 201


@app.route("/vendor/products/<product_id>", methods=["PUT"])
@vendor_token_required
def update_vendor_product(current_vendor_id, product_id):
    """Update product details, price, description, or stock inventory."""
    updates = request.get_json() or {}
    updated = marketplace.update_product(current_vendor_id, product_id, updates)
    return jsonify({"message": "Product updated successfully", "product": updated.to_dict()}), 200


@app.route("/vendor/products/<product_id>", methods=["DELETE"])
@vendor_token_required
def delete_vendor_product(current_vendor_id, product_id):
    """Delete a product listing."""
    marketplace.deleteproduct(product_id, current_vendor_id)
    return jsonify({"message": "Product removed successfully"}), 200


@app.route("/vendor/orders", methods=["GET"])
@vendor_token_required
def get_vendor_orders(current_vendor_id):
    """Retrieve all customer orders containing items from this vendor."""
    vendor_orders = marketplace.get_vendor_orders(current_vendor_id)
    return jsonify({"orders": vendor_orders}), 200


@app.route("/vendor/orders/<order_id>", methods=["PUT"])
@vendor_token_required
def update_vendor_order_status(current_vendor_id, order_id):
    """Legacy order status updater."""
    data = request.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    success = marketplace.update_order_status(order_id, new_status)
    if success:
        return jsonify({"message": "Order status updated"}), 200
    return jsonify({"error": "Order not found or update failed"}), 404


@app.route("/vendor/orders/<order_id>/items/<product_id>/status", methods=["PUT"])
@vendor_token_required
def update_vendor_item_status(current_vendor_id, order_id, product_id):
    """Vendor marks an individual order item as 'sent to port'."""
    data = request.get_json() or {}
    new_status = data.get("item_status", "sent to port")
    if new_status not in ("pending", "sent to port"):
        return jsonify({"error": "Invalid item status. Allowed: 'pending', 'sent to port'"}), 400
        
    product = marketplace.findproduct(product_id)
    if not product or product.vendor_id != current_vendor_id:
        return jsonify({"error": "Product not found or does not belong to you"}), 403
        
    success = database.update_order_item_status(order_id, product_id, new_status)
    if success:
        return jsonify({"message": "Item status updated successfully", "item_status": new_status}), 200
    return jsonify({"error": "Order item not found"}), 404


@app.route("/vendor/stats", methods=["GET"])
@vendor_token_required
def get_vendor_stats(current_vendor_id):
    """Retrieve vendor high-level KPI cards (sales, active products, pending orders)."""
    stats = marketplace.get_vendor_stats(current_vendor_id)
    return jsonify(stats), 200


@app.route("/vendor/analytics", methods=["GET"])
@vendor_token_required
def get_vendor_analytics(current_vendor_id):
    """Retrieve per-product sales performance and ratings analytics."""
    analytics = database.get_vendor_product_analytics(current_vendor_id)
    return jsonify({"analytics": analytics}), 200


# ==============================================================================
# SECTION 6: LOGISTICS & COURIER PARTNERS
# ==============================================================================

@app.route("/shipping-companies", methods=["GET"])
def get_public_shipping_companies():
    """Public carrier lookup for customer checkout selection."""
    carriers = database.get_all_shipping_companies()
    return jsonify({"shipping_companies": carriers}), 200


@app.route("/shipping/login", methods=["POST"])
def login_shipping():
    """Logistics partner authentication."""
    data = request.get_json() or {}
    identifier = data.get("email") or data.get("shipping_id") or ""
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "Email/ID and password are required"}), 400

    carrier = database.searchshipping(identifier)
    if not carrier:
        return jsonify({"error": "Invalid carrier email/ID or password"}), 401

    stored_pw = carrier["password_hash"]
    valid = (stored_pw == password) or auth.decodere(password, stored_pw)

    if not valid:
        return jsonify({"error": "Invalid carrier email/ID or password"}), 401

    payload = {
        "shipping_id": carrier["shipping_id"],
        "name": carrier["name"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({
        "message": "Login successful",
        "token": token,
        "shipping_id": carrier["shipping_id"],
        "name": carrier["name"],
        "email": carrier["email"]
    }), 200


@app.route("/shipping/deliveries", methods=["GET"])
@shipping_token_required
def get_shipping_deliveries(current_shipping_id):
    """Retrieve all deliveries assigned to this logistics carrier with earnings."""
    result = database.get_deliveries_by_shipping_company(current_shipping_id)
    return jsonify(result), 200


@app.route("/shipping/deliveries/<delivery_id>", methods=["PUT"])
@shipping_token_required
def update_shipping_delivery(current_shipping_id, delivery_id):
    """
    Update delivery status ('on the way', 'delivered').
    Triggers database constraint checks to ensure all vendor items are at port.
    """
    new_status = request.get_json().get("status")
    try:
        updated = database.update_delivery_status(delivery_id, new_status)
        if updated:
            return jsonify({"message": "Delivery status updated successfully"}), 200
        return jsonify({"error": "Delivery not found"}), 404
    except Exception as e:
        err_msg = str(e)
        if "Dispatch blocked" in err_msg:
            clean_msg = err_msg.split("Dispatch blocked:")[-1].strip()
            return jsonify({"error": f"Dispatch blocked: {clean_msg}"}), 400
        return jsonify({"error": err_msg}), 500


# ==============================================================================
# SECTION 7: ADMIN CONTROL & PLATFORM ANALYTICS
# ==============================================================================

@app.route("/admin/login", methods=["POST"])
def login_admin():
    """Platform administrator authentication."""
    data = request.get_json() or {}
    if data.get("email") == "admin" and data.get("password") == "admin":
        payload = {
            "admin_id": "SYS_ADMIN",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({"message": "Login successful", "token": token}), 200
    return jsonify({"error": "Invalid admin credentials"}), 401


@app.route("/admin/stats", methods=["GET"])
@admin_token_required
def get_admin_stats():
    """Platform overview KPIs."""
    stats = database.get_admin_stats()
    return jsonify(stats), 200


@app.route("/admin/users", methods=["GET"])
@admin_token_required
def get_admin_users():
    """Retrieve full registered user base (customers, vendors, carriers)."""
    users = database.get_admin_users()
    return jsonify({"users": users}), 200


@app.route("/admin/analytics", methods=["GET"])
@admin_token_required
def get_admin_analytics():
    """Comprehensive platform analytics (Top Products, High Spenders, Vendor GMV, Categories, Carrier Earnings)."""
    top_products = database.viewtopproducs(5)
    top_spenders = database.viewhighestspender(5)
    vendor_revenue = database.highestrevenue_vendors()
    category_performance = database.top_popular_products_categories()
    carrier_revenue = database.get_all_shipping_companies()
    return jsonify({
        "top_products": top_products,
        "top_spenders": top_spenders,
        "vendor_revenue": vendor_revenue,
        "category_performance": category_performance,
        "carrier_revenue": carrier_revenue
    }), 200


@app.route("/admin/shipping-companies", methods=["GET"])
@admin_token_required
def get_admin_shipping_companies():
    """Admin view of all shipping partners with logistics metrics."""
    carriers = database.get_all_shipping_companies()
    return jsonify({"shipping_companies": carriers}), 200


@app.route("/admin/shipping-companies", methods=["POST"])
@admin_token_required
def add_admin_shipping_company():
    """Onboard a new logistics partner."""
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone") or data.get("contact_phone", "")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Company name, email, and password are required"}), 400

    if database.searchshipping(email):
        return jsonify({"error": "A shipping company with this email already exists"}), 409

    pw_hash = auth.encodere(password)
    try:
        new_carrier = database.register_shipping_company(name, email, phone, pw_hash)
        return jsonify({
            "message": "Shipping company onboarded successfully",
            "shipping_company": new_carrier
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================

if __name__ == "__main__":
    app.run(port=5001, debug=True)
