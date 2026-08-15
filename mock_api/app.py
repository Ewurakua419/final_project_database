from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
from datetime import datetime, timezone, timedelta
import sys
import os
from functools import wraps

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import SECRET_KEY
import auth
import jwt
from service.marketplace import Marketplace
import database

marketplace = Marketplace(name="Mock Marketplace")

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "http://127.0.0.1:5500"}
})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data["user_id"][:6]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
            
        return f(current_user_id, *args, **kwargs)
    return decorated

def vendor_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_vendor_id = data["vendor_id"][:6]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            return jsonify({"error": "Unauthorized"}), 401
            
        return f(current_vendor_id, *args, **kwargs)
    return decorated

def shipping_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_shipping_id = data["shipping_id"][:6]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            return jsonify({"error": "Unauthorized"}), 401
            
        return f(current_shipping_id, *args, **kwargs)
    return decorated

def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if "admin_id" not in data:
                return jsonify({"error": "Not an admin token"}), 403
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
            
        return f(*args, **kwargs)
    return decorated

def get_image_url(image_path):
    if not image_path:
        return ""
    if image_path.startswith("http://") or image_path.startswith("https://") or image_path.startswith("data:image"):
        return image_path
    base_url = request.host_url
    return f"{base_url}static/{image_path}"

# --- AUTH ---
@app.route("/register", methods=["POST"])
def register_customer():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    
    name = f"{first_name} {last_name}".strip()
    user = marketplace.registerCustomer(name, password, email, first_name=first_name, last_name=last_name, phone_number=phone_number)
    
    if user is None:
        return jsonify({"error": "Email already registered"}), 409
    
    payload = {"user_id": user.unique_id, "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Success", "user_id": user.unique_id, "token": token}), 201

@app.route("/login", methods=["POST"])
def login_customer():
    data = request.get_json()
    customer = marketplace.login(data.get("email"), data.get("password"))
    if not customer:
        return jsonify({"error": "Invalid email or password"}), 401
        
    payload = {"user_id": customer.unique_id, "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Success", "token": token}), 200

@app.route("/vendor/register", methods=["POST"])
def register_vendor():
    data = request.get_json()
    vendor = marketplace.registerVendor(data.get("vendor_name"), data.get("password"), data.get("email"), data.get("address", ""), phone_number=data.get("phone_number"))
    payload = {"vendor_id": vendor.unique_id, "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Success", "token": token}), 201

@app.route("/vendor/login", methods=["POST"])
def login_vendor():
    data = request.get_json()
    vendor = marketplace.loginVendor(data.get("email"), data.get("password"))
    if not vendor:
        return jsonify({"error": "Invalid email or password"}), 401
        
    payload = {"vendor_id": vendor.unique_id, "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Success", "token": token}), 200

# --- PRODUCTS ---
@app.route("/product-items", methods = ["GET"])
def get_products():
    products = marketplace.get_all_products()
    processed = []
    for p in products:
        d = p.to_dict()
        d['image'] = get_image_url(d.get('image', ''))
        processed.append(d)
    return jsonify({"products": processed}), 200

@app.route("/product-items/<product_id>", methods=["GET"])
def get_product(product_id):
    product = marketplace.findproduct(product_id)
    if product:
        d = product.to_dict()
        d['image'] = get_image_url(d.get('image', ''))
        return jsonify(d), 200
    return jsonify({"error": "Product not found"}), 404

@app.route("/vendor/products", methods=["GET"])
@vendor_token_required
def get_vendor_products(current_vendor_id):
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
    data = request.get_json()
    new_product = marketplace.add_product(current_vendor_id, data)
    return jsonify({"message": "Success", "product": new_product.to_dict()}), 201

@app.route("/vendor/products/<product_id>", methods=["PUT"])
@vendor_token_required
def update_vendor_product(current_vendor_id, product_id):
    updates = request.get_json()
    updated = marketplace.update_product(current_vendor_id, product_id, updates)
    return jsonify({"message": "Success", "product": updated.to_dict()}), 200

@app.route("/vendor/products/<product_id>", methods=["DELETE"])
@vendor_token_required
def delete_vendor_product(current_vendor_id, product_id):
    marketplace.deleteproduct(product_id, current_vendor_id)
    return jsonify({"message": "Success"}), 200

# --- CART / ORDERS ---
@app.route("/cart", methods=["GET"])
@token_required
def get_cart(current_user_id):
    result = marketplace.get_cart(current_user_id)
    for item in result.get("cart", []):
        if "product" in item and "image" in item["product"]:
            item["product"]["image"] = get_image_url(item["product"]["image"])
    return jsonify(result), 200

@app.route("/cart", methods=["POST"])
@token_required
def add_to_cart(current_user_id):
    data = request.get_json()
    marketplace.add_to_cart(data.get("product_id"), current_user_id, data.get("quantity", 1))
    return jsonify({"message": "Success"}), 201

@app.route("/cart/<product_id>", methods=["DELETE"])
@token_required
def remove_item(current_user_id, product_id):
    marketplace.remove_from_cart(product_id, current_user_id)
    return jsonify({"message": "Success"}), 200

@app.route("/cart/<product_id>/quantity", methods=["PUT"])
@token_required
def update_item_qty(current_user_id, product_id):
    data = request.get_json()
    qty = data.get("quantity", 0)
    marketplace.remove_from_cart(product_id, current_user_id)
    if qty > 0:
        marketplace.add_to_cart(product_id, current_user_id, qty)
    return jsonify({"message": "Success"}), 200

@app.route("/checkout", methods=["POST"])
@token_required
def to_checkout(current_user_id):
    data = request.get_json()
    order = marketplace.checkout(
        current_user_id,
        shipping_address=data.get("shipping_address"),
        payment_details=data.get("payment_details"),
        shipping_fee=5.00,
        shipping_id=data.get("shipping_id")
    )
    if order is None:
        return jsonify({"error": "Cart is empty"}), 400
    return jsonify(order.to_dict()), 201

@app.route("/orders", methods=["GET"])
@token_required
def get_orders(current_user_id):
    orders = marketplace.get_customer_orders(current_user_id)
    return jsonify({"orders": orders}), 200

@app.route("/vendor/orders", methods=["GET"])
@vendor_token_required
def get_vendor_orders(current_vendor_id):
    vendor_orders = marketplace.get_vendor_orders(current_vendor_id)
    return jsonify({"orders": vendor_orders}), 200

@app.route("/vendor/orders/<order_id>", methods=["PUT"])
@vendor_token_required
def update_vendor_order_status(current_vendor_id, order_id):
    data = request.get_json()
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    success = marketplace.update_order_status(order_id, new_status)
    if success:
        return jsonify({"message": "Order status updated"}), 200
    return jsonify({"error": "Order not found or update failed"}), 404

@app.route("/vendor/stats", methods=["GET"])
@vendor_token_required
def get_vendor_stats(current_vendor_id):
    stats = marketplace.get_vendor_stats(current_vendor_id)
    return jsonify(stats), 200

@app.route("/vendor/analytics", methods=["GET"])
@vendor_token_required
def get_vendor_analytics(current_vendor_id):
    import database
    analytics = database.get_vendor_product_analytics(current_vendor_id)
    return jsonify({"analytics": analytics}), 200

@app.route("/vendor/orders/<order_id>/items/<product_id>/status", methods=["PUT"])
@vendor_token_required
def update_vendor_item_status(current_vendor_id, order_id, product_id):
    """Vendor marks an individual order item as 'sent to port'."""
    data = request.get_json() or {}
    new_status = data.get("item_status", "sent to port")
    if new_status not in ("pending", "sent to port"):
        return jsonify({"error": "Invalid item status. Must be 'pending' or 'sent to port'"}), 400
    # Verify the product belongs to this vendor
    product = marketplace.findproduct(product_id)
    if not product or product.vendor_id != current_vendor_id:
        return jsonify({"error": "Product not found or does not belong to you"}), 403
    success = database.update_order_item_status(order_id, product_id, new_status)
    if success:
        return jsonify({"message": "Item status updated", "item_status": new_status}), 200
    return jsonify({"error": "Order item not found"}), 404

# --- PROFILE ---
@app.route("/customer/profile", methods=["GET"])
@token_required
def get_customer_profile(current_user_id):
    customer = marketplace.finduser_by_id(current_user_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    addr_list = database.get_addresses_by_customer(current_user_id)
    return jsonify({
        "email": customer.email,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone_number": customer.phone_number,
        "addresses": addr_list
    }), 200

@app.route("/customer/profile", methods=["PUT"])
@token_required
def update_customer_profile(current_user_id):
    data = request.get_json()
    profile = marketplace.update_customer_profile(current_user_id, data)
    return jsonify(profile), 200

@app.route("/customer/addresses", methods=["POST"])
@token_required
def add_customer_address(current_user_id):
    data = request.get_json()
    from model.address import Address
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
    """Delete a customer address."""
    success = database.delete_address(address_id, current_user_id)
    if success:
        return jsonify({"message": "Address deleted successfully"}), 200
    return jsonify({"error": "Address not found or unauthorized"}), 404

# --- SHIPPING ---
@app.route("/shipping/login", methods=["POST"])
def login_shipping():
    data = request.get_json() or {}
    identifier = data.get("email") or data.get("shipping_id") or ""
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "Email/ID and password are required"}), 400

    carrier = database.searchshipping(identifier)
    if not carrier:
        return jsonify({"error": "Invalid carrier email/ID or password"}), 401

    stored_pw = carrier["password_hash"]
    valid = False
    if stored_pw == password:
        valid = True
    elif auth.decodere(password, stored_pw):
        valid = True

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
    dels = database.get_deliveries_by_shipping_company(current_shipping_id)
    return jsonify({"deliveries": dels}), 200

@app.route("/shipping/deliveries/<delivery_id>", methods=["PUT"])
@shipping_token_required
def update_shipping_delivery(current_shipping_id, delivery_id):
    new_status = request.get_json().get("status")
    try:
        updated = database.update_delivery_status(delivery_id, new_status)
        if updated:
            return jsonify({"message": "Status updated successfully"}), 200
        return jsonify({"error": "Delivery not found"}), 404
    except Exception as e:
        err_msg = str(e)
        # Extract user-friendly trigger message if present
        if "Dispatch blocked" in err_msg or "Cannot dispatch" in err_msg:
            # Clean up raw MariaDB error prefix
            clean_msg = err_msg.split("Dispatch blocked:")[-1].strip() if "Dispatch blocked:" in err_msg else err_msg
            return jsonify({"error": f"Dispatch blocked: {clean_msg}"}), 400
        return jsonify({"error": err_msg}), 400


# --- REVIEWS ---
@app.route("/product-items/<product_id>/reviews", methods=["GET"])
def get_product_reviews(product_id):
    reviews = marketplace.get_product_reviews(product_id)
    return jsonify({"reviews": [r.to_dict() for r in reviews]}), 200

@app.route("/product-items/<product_id>/reviews", methods=["POST"])
@token_required
def add_product_review(current_user_id, product_id):
    data = request.get_json()
    rating = data.get("rating")
    comment = data.get("text") or data.get("comment", "")
    if not rating or not comment:
        return jsonify({"error": "Rating and comment are required"}), 400
    review = marketplace.add_product_review(product_id, current_user_id, comment, rating)
    return jsonify(review.to_dict()), 201

# --- MISC / ADMIN ---
@app.route("/shipping-companies", methods=["GET"])
def get_public_shipping_companies():
    """Public endpoint — returns list of carriers for checkout page."""
    carriers = database.get_all_shipping_companies()
    return jsonify({"shipping_companies": carriers}), 200

@app.route("/admin/login", methods=["POST"])
def login_admin():
    data = request.get_json()
    if data.get("email") == "admin" and data.get("password") == "admin":
        payload = {"admin_id": "SYS_ADMIN", "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({"message": "Login successful", "token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/admin/stats", methods=["GET"])
@admin_token_required
def get_admin_stats():
    stats = database.get_admin_stats()
    return jsonify(stats), 200

@app.route("/admin/users", methods=["GET"])
@admin_token_required
def get_admin_users():
    users = database.get_admin_users()
    return jsonify({"users": users}), 200

@app.route("/admin/analytics", methods=["GET"])
@admin_token_required
def get_admin_analytics():
    """Retrieve full marketplace performance analytics."""
    top_products = database.viewtopproducs(5)
    top_spenders = database.viewhighestspender(5)
    vendor_revenue = database.highestrevenue_vendors()
    category_performance = database.top_popular_products_categories()
    return jsonify({
        "top_products": top_products,
        "top_spenders": top_spenders,
        "vendor_revenue": vendor_revenue,
        "category_performance": category_performance
    }), 200

@app.route("/admin/shipping-companies", methods=["GET"])
@admin_token_required
def get_admin_shipping_companies():
    carriers = database.get_all_shipping_companies()
    return jsonify({"shipping_companies": carriers}), 200

@app.route("/admin/shipping-companies", methods=["POST"])
@admin_token_required
def add_admin_shipping_company():
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
            "message": "Shipping company registered successfully",
            "shipping_company": new_carrier
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001,debug=True)
