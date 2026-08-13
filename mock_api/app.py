from products import products
from cart import cart
import uuid
from datetime import datetime
from orders import orders
from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
from datetime import datetime, timezone
import sys
import os
from functools import wraps
# Add the parent directory to sys.path so we can import auth.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import encodere, decodere, SECRET_KEY
import jwt
from datetime import timedelta
from service.marketplace import Marketplace

marketplace = Marketplace(name="Mock Marketplace")

# Initialize the Flask application
app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "http://127.0.0.1:5500"}
})

vendor_id = "vendor_001"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data["user_id"]
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
            current_vendor_id = data["vendor_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except KeyError:
            return jsonify({"error": "Not a vendor token"}), 403
            
        return f(current_vendor_id, *args, **kwargs)
    return decorated

def find_product(product_id):
    for p in products:
        if p["id"] == product_id:
            return p
    return None

def get_image_url(image_path):
    if image_path.startswith("http://") or image_path.startswith("https://") or image_path.startswith("data:image"):
        return image_path
    base_url = request.host_url
    return f"{base_url}static/{image_path}"

# ---authentication----
@app.route("/register", methods=["POST"])
def register_customer():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    
    if not email or not password or not first_name or not last_name or not phone_number:
        return jsonify({"error": "First name, last name, phone number, email, and password are required"}), 400
        
    name = f"{first_name} {last_name}".strip()
    user = marketplace.registerCustomer(name, password, email, first_name=first_name, last_name=last_name, phone_number=phone_number)
    if not user:
        return jsonify({"error": "User already exists or registration failed"}), 409
    
    return jsonify({
        "message": "User registered successfully", 
        "user_id": user.unique_id
    }), 201

    

@app.route("/login", methods=["POST"])
def login_customer():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    customer = marketplace.login(email, password)
    
    if not customer:
        return jsonify({"error": "Invalid email or password"}), 401
        
    # Generate JWT Token
    payload = {
        "user_id": customer.unique_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24) # Token expires in 24 hours
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return jsonify({
        "message": "Login successful",
        "token": token
    }), 200



@app.route("/vendor/register", methods=["POST"])
def register_vendor():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    vendor_name = data.get("vendor_name")
    phone_number = data.get("phone_number")
    address = data.get("address", "123 Vendor St")
    
    if not email or not password or not vendor_name or not phone_number:
        return jsonify({"error": "Vendor name, phone number, email, and password are required"}), 400
        
    vendor = marketplace.registerVendor(vendor_name, password, email, address, phone_number=phone_number)
    if not vendor:
        return jsonify({"error": "Vendor already exists or registration failed"}), 409
        
    return jsonify({
        "message": "Vendor registered successfully", 
        "vendor_id": vendor.unique_id
    }), 201

@app.route("/vendor/login", methods=["POST"])
def login_vendor():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    vendor = marketplace.loginVendor(email, password)
    
    if not vendor:
        return jsonify({"error": "Invalid email or password"}), 401
        
    # Generate JWT Token
    payload = {
        "vendor_id": vendor.unique_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return jsonify({
        "message": "Login successful",
        "token": token
    }), 200

DUMMY_VENDOR_EMAIL = "dummy_vendor@example.com"

@app.route("/product-items", methods = ["GET"])
def get_products():
    all_products = marketplace.get_all_products()
    processed_products = []

    for product in all_products:
        p_dict = product.to_dict()
        p_dict['image'] = get_image_url(p_dict['image'])
        processed_products.append(p_dict)
        
    return jsonify({"products": processed_products}), 200

@app.route("/product-items/<product_id>", methods=["GET"])
def get_product(product_id):
    product = marketplace.findproduct(product_id)
    if product:
        p_dict = product.to_dict()
        p_dict['image'] = get_image_url(p_dict['image'])
        return jsonify(p_dict), 200
    return jsonify({"error": "Product not found"}), 404


@app.route("/vendor/products", methods=["GET"])
@vendor_token_required
def get_vendor_products(current_vendor_id):
    all_products = marketplace.get_all_products()
    vendor_products = []
    
    for product in all_products:
        if product.vendor_id == current_vendor_id:
            p_dict = product.to_dict()
            p_dict['image'] = get_image_url(p_dict['image'])
            vendor_products.append(p_dict)
            
    return jsonify({"products": vendor_products}), 200

@app.route("/vendor/products", methods=["POST"])
@vendor_token_required
def add_vendor_product(current_vendor_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    if not data.get("name") or not data.get("priceCents") or not data.get("image"):
        return jsonify({"error": "Missing required fields"}), 400
        
    new_product = marketplace.add_product(current_vendor_id, data)
    if not new_product:
        return jsonify({"error": "Vendor not found"}), 404
        
    return jsonify({"message": "Product created successfully", "product": new_product.to_dict()}), 201

@app.route("/vendor/products/<product_id>", methods=["PUT"])
@vendor_token_required
def update_vendor_product(current_vendor_id, product_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    
    updates = {}
    allowed_string_fields = ["name", "image", "type", "description", "brand"]
    for field in allowed_string_fields:
        if field in data:
            updates[field] = data[field]
            
    if "priceCents" in data:
        updates["priceCents"] = int(data["priceCents"])
    if "stock" in data:
        updates["stock"] = int(data["stock"])
        
    updated_product = marketplace.update_product(current_vendor_id, product_id, updates)
    if not updated_product:
        return jsonify({"error": "Product not found or unauthorized"}), 404
        
    return jsonify({"message": "Product updated successfully", "product": updated_product.to_dict()}), 200

@app.route("/vendor/products/<product_id>", methods=["DELETE"])
@vendor_token_required
def delete_vendor_product(current_vendor_id, product_id):
    success = marketplace.deleteproduct(product_id, current_vendor_id)
    if not success:
        return jsonify({"error": "Product not found or unauthorized"}), 404
        
    return jsonify({"message": "Product deleted successfully"}), 200

@app.route("/vendor/orders", methods=["GET"])
@vendor_token_required
def get_vendor_orders(current_vendor_id):
    vendor_orders = marketplace.get_vendor_orders(current_vendor_id)
    if vendor_orders is None:
        return jsonify({"error": "Vendor not found"}), 404
        
    for order in vendor_orders:
        for item in order.get("items", []):
            if "image" in item:
                item["image"] = get_image_url(item["image"])
        
    sorted_orders = sorted(vendor_orders, key=get_order_date, reverse=True)
    return jsonify({"orders": sorted_orders}), 200

@app.route("/vendor/orders/<order_id>", methods=["PUT"])
@vendor_token_required
def update_vendor_order_status(current_vendor_id, order_id):
    data = request.get_json()
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
        
    success = marketplace.update_order_status(order_id, new_status)
    if not success:
        return jsonify({"error": "Order not found"}), 404
        
    return jsonify({"message": "Order status updated successfully"}), 200

@app.route("/vendor/stats", methods=["GET"])
@vendor_token_required
def get_vendor_stats(current_vendor_id):
    stats = marketplace.get_vendor_stats(current_vendor_id)
    if stats is None:
        return jsonify({"error": "Vendor not found"}), 404
        
    return jsonify(stats), 200




DUMMY_CUSTOMER_EMAIL = "dummy@example.com"

@app.route("/cart", methods=["GET"])
@token_required
def get_cart(current_user_id):
    result = marketplace.get_cart(current_user_id)
    if result is None:
        return jsonify({"error": "User not found"}), 404
        
    for item in result.get("cart", []):
        if "product" in item and "image" in item["product"]:
            item["product"]["image"] = get_image_url(item["product"]["image"])
            
    return jsonify(result), 200


@app.route("/cart", methods=["POST"])
@token_required
def add_to_cart(current_user_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400

    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "Invalid product_id or quantity"}), 400

    success = marketplace.add_to_cart(product_id, current_user_id, quantity)
    if not success:
        return jsonify({"error": "Product or user not found"}), 404

    return jsonify({"message": "Item added to cart successfully"}), 201


@app.route("/cart/<product_id>", methods=["DELETE"])
@token_required
def remove_item_completely(current_user_id, product_id):
    success = marketplace.remove_from_cart(product_id, current_user_id)
    if success:
        return jsonify({"message": "Item removed from cart successfully"}), 200
    return jsonify({"error": "Item not found in cart"}), 404

@app.route("/cart/<product_id>/quantity", methods=["PUT"])
@token_required
def update_item(current_user_id, product_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400

    data = request.get_json()
    quantity = data.get("quantity")

    if quantity is None or not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Invalid quantity"}), 400

    if quantity == 0:
        marketplace.remove_from_cart(product_id, current_user_id)
        return jsonify({"message": "Item quantity reached 0 and was removed"}), 200
        
    # To update quantity: remove it completely and add it back with the absolute quantity
    marketplace.remove_from_cart(product_id, current_user_id)
    success = marketplace.add_to_cart(product_id, current_user_id, quantity)
    
    if success:
        return jsonify({"message": "Item updated in cart"}), 200
    return jsonify({"error": "Item not found in cart"}), 404

TAX_RATE = 0.08
SHIPPING_FEE = 5.00

@app.route("/checkout", methods=["POST"])
@token_required
def to_checkout(current_user_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
    
    data = request.get_json()
    shipping_address = data.get("shipping_address", {})
    payment_details = data.get("payment_details", {})
    
    order = marketplace.checkout(current_user_id, shipping_fee=5.00)
    if not order:
        return jsonify({"error": "Cart is empty or user not found"}), 400
    
    return jsonify(order.to_dict()), 201



def get_order_date(order):
    return order.get("created_at", "")

@app.route("/orders", methods=["GET"])
@token_required
def get_orders(current_user_id):
    # Use authenticated customer ID
    customer_orders = marketplace.get_customer_orders(current_user_id)
    if customer_orders is None:
        return jsonify({"error": "Customer not found"}), 404
        
    formatted_orders = customer_orders
    
    for order in formatted_orders:
        for item in order.get("items", []):
            if "image" in item:
                item["image"] = get_image_url(item["image"])
    
    # Re-use our get_order_date function
    sorted_orders = sorted(formatted_orders, key=get_order_date, reverse=True)
    
    return jsonify({"orders": sorted_orders}), 200


# Run the local development server

# --- REVIEWS ---

@app.route("/product-items/<product_id>/reviews", methods=["GET"])
def get_reviews(product_id):
    product_reviews = marketplace.get_product_reviews(product_id)
    return jsonify({"reviews": [r.to_dict() for r in product_reviews]}), 200

@app.route("/product-items/<product_id>/reviews", methods=["POST"])
@token_required
def add_review(current_user_id, product_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400

    data = request.get_json()
    rating = int(data.get("rating", 5))
    text = data.get("text", "")
    
    # Now we pass the authenticated user ID
    review = marketplace.add_product_review(product_id, current_user_id, text, rating)
    
    if review is None:
        return jsonify({"error": "Failed to add review"}), 400
        
    return jsonify({"message": "Review added successfully", "review": review.to_dict()}), 201

if __name__ == "__main__":
    app.run(port=5001,debug=True)
