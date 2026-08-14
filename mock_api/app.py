from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
from datetime import datetime, timezone, timedelta
import sys
import os
from functools import wraps

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import SECRET_KEY
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
    order = marketplace.checkout(current_user_id, shipping_address=data.get("shipping_address"), payment_details=data.get("payment_details"), shipping_fee=5.00)
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

@app.route("/vendor/stats", methods=["GET"])
@vendor_token_required
def get_vendor_stats(current_vendor_id):
    stats = marketplace.get_vendor_stats(current_vendor_id)
    return jsonify(stats), 200

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

# --- SHIPPING ---
@app.route("/shipping/login", methods=["POST"])
def login_shipping():
    data = request.get_json()
    payload = {"shipping_id": "SHIP01", "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Login successful", "token": token}), 200

@app.route("/shipping/deliveries", methods=["GET"])
@shipping_token_required
def get_shipping_deliveries(current_shipping_id):
    dels = database.get_deliveries_by_shipping_company(current_shipping_id)
    return jsonify({"deliveries": dels}), 200

@app.route("/shipping/deliveries/<delivery_id>", methods=["PUT"])
@shipping_token_required
def update_shipping_delivery(current_shipping_id, delivery_id):
    new_status = request.get_json().get("status")
    updated = database.update_delivery_status(delivery_id, new_status)
    if updated:
        return jsonify({"message": "Status updated successfully"}), 200
    return jsonify({"error": "Delivery not found"}), 404

# --- MISC / ADMIN ---
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

if __name__ == "__main__":
    app.run(port=5001,debug=True)
