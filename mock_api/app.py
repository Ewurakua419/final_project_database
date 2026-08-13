from products import products
from cart import cart
# from vendors import vendors # Using marketplace instead

from reviews import reviews
import uuid
from datetime import datetime
from orders import orders
from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
from datetime import datetime, timezone
import sys
import os
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
    r"/product-items/*": {"origins": "http://127.0.0.1:5500"}, 
    r"/cart.*": {"origins": "http://127.0.0.1:5500"},
    r"/checkout.*": {"origins": "http://127.0.0.1:5500"},
    r"/orders.*": {"origins": "http://127.0.0.1:5500"},
    r"/vendor/.*": {"origins": "http://127.0.0.1:5500"},
})

vendor_id = "vendor_001"
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
    name = data.get("name", "New User")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    user = marketplace.registerCustomer(name, password, email)
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
    name = data.get("name", "New Vendor")
    address = data.get("address", "123 Vendor St")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    vendor = marketplace.registerVendor(name, password, email, address)
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
def get_vendor_products():
    vendor = marketplace.findvendor(DUMMY_VENDOR_EMAIL)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404

    all_products = marketplace.get_all_products()
    vendor_products = []
    
    for product in all_products:
        if product.vendor_id == vendor.unique_id:
            p_dict = product.to_dict()
            p_dict['image'] = get_image_url(p_dict['image'])
            vendor_products.append(p_dict)
            
    return jsonify({"products": vendor_products}), 200

@app.route("/vendor/products", methods=["POST"])
def add_vendor_product():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    if not data.get("name") or not data.get("priceCents") or not data.get("image"):
        return jsonify({"error": "Missing required fields"}), 400
        
    new_product = marketplace.add_product(DUMMY_VENDOR_EMAIL, data)
    if not new_product:
        return jsonify({"error": "Vendor not found"}), 404
        
    return jsonify({"message": "Product created successfully", "product": new_product.to_dict()}), 201

@app.route("/vendor/products/<product_id>", methods=["PUT"])
def update_vendor_product(product_id):
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
        
    updated_product = marketplace.update_product(DUMMY_VENDOR_EMAIL, product_id, updates)
    if not updated_product:
        return jsonify({"error": "Product not found or unauthorized"}), 404
        
    return jsonify({"message": "Product updated successfully", "product": updated_product.to_dict()}), 200

@app.route("/vendor/products/<product_id>", methods=["DELETE"])
def delete_vendor_product(product_id):
    success = marketplace.deleteproduct(product_id, DUMMY_VENDOR_EMAIL)
    if not success:
        return jsonify({"error": "Product not found or unauthorized"}), 404
        
    return jsonify({"message": "Product deleted successfully"}), 200

@app.route("/vendor/orders", methods=["GET"])
def get_vendor_orders():
    vendor_orders = []
    
    # Loop through every order in the system
    for order in orders:
        vendor_items = []
        vendor_subtotal = 0
        
        for item in order.get("items", []):
            product = find_product(item["product_id"])
            if product and product.get("vendor_id") == vendor_id:
                vendor_items.append(item)
                vendor_subtotal += item.get("item_total", 0)
                
        if len(vendor_items) > 0:
            order_copy = order.copy()
            order_copy["items"] = vendor_items
            
            order_copy["pricing_summary"] = {
                "subtotal": round(vendor_subtotal, 2),
                "tax": 0,
                "shipping": 0,
                "grand_total": round(vendor_subtotal, 2)
            }
            vendor_orders.append(order_copy)
            
    # Sort the orders so the newest ones appear first (uses get_order_date function)
    sorted_orders = sorted(vendor_orders, key=get_order_date, reverse=True)
    return jsonify({"orders": sorted_orders}), 200

@app.route("/vendor/orders/<order_id>", methods=["PUT"])
def update_vendor_order_status(order_id):
    data = request.get_json()
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
        
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = new_status
            return jsonify({"message": "Order status updated successfully", "order": order}), 200
            
    return jsonify({"error": "Order not found"}), 404

@app.route("/vendor/stats", methods=["GET"])
def get_vendor_stats():
    active_products = 0
    for product in products:
        if product.get("vendor_id") == vendor_id:
            active_products += 1
    
    total_sales = 0
    pending_orders_count = 0
    
    for order in orders:
        vendor_items = []
        for item in order.get("items", []):
            product = find_product(item["product_id"])
            if product and product.get("vendor_id") == vendor_id:
                vendor_items.append(item)
        
        if len(vendor_items) > 0:
            for item in vendor_items:
                total_sales += item.get("item_total", 0)
                
            if order.get("status") == "pending":
                pending_orders_count += 1
                
    return jsonify({
        "total_sales": round(total_sales, 2),
        "active_products": active_products,
        "pending_orders": pending_orders_count
    }), 200




DUMMY_CUSTOMER_EMAIL = "dummy@example.com"

@app.route("/cart", methods=["GET"])
def get_cart():
    result = marketplace.get_cart(DUMMY_CUSTOMER_EMAIL)
    if result is None:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify(result), 200


@app.route("/cart", methods=["POST"])
def add_to_cart():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400

    data = request.get_json()
    prod_id = data.get("prodID")
    quantity = data.get("quantity")

    if not prod_id or not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "Invalid prodID or quantity"}), 400

    success = marketplace.add_to_cart(prod_id, DUMMY_CUSTOMER_EMAIL, quantity)
    if not success:
        return jsonify({"error": "Product or user not found"}), 404

    return jsonify({"message": "Item added to cart successfully"}), 201


@app.route("/cart/<product_id>", methods=["DELETE"])
def remove_item_completely(product_id):
    success = marketplace.remove_from_cart(product_id, DUMMY_CUSTOMER_EMAIL)
    if success:
        return jsonify({"message": "Item removed from cart successfully"}), 200
    return jsonify({"error": "Item not found in cart"}), 404

@app.route("/cart/<product_id>/quantity", methods=["PUT"])
def update_item(product_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400

    data = request.get_json()
    quantity = data.get("quantity")

    if quantity is None or not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Invalid quantity"}), 400

    if quantity == 0:
        marketplace.remove_from_cart(product_id, DUMMY_CUSTOMER_EMAIL)
        return jsonify({"message": "Item quantity reached 0 and was removed"}), 200
        
    # To update quantity: remove it completely and add it back with the absolute quantity
    marketplace.remove_from_cart(product_id, DUMMY_CUSTOMER_EMAIL)
    success = marketplace.add_to_cart(product_id, DUMMY_CUSTOMER_EMAIL, quantity)
    
    if success:
        return jsonify({"message": "Item updated in cart"}), 200
    return jsonify({"error": "Item not found in cart"}), 404

TAX_RATE = 0.08
SHIPPING_FEE = 5.00

@app.route("/checkout", methods=["POST"])
def to_checkout():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
    
    data = request.get_json()
    shipping_address = data.get("shipping_address", {})
    payment_details = data.get("payment_details", {})
    
    cart_data = marketplace.get_cart(DUMMY_CUSTOMER_EMAIL)
    if not cart_data or cart_data["total_items"] == 0:
        return jsonify({"error": "Cart is empty"}), 400
        
    subtotal = cart_data["total_price"]
    order_items = cart_data["cart"] # Already formatted
            
    tax = round(subtotal * TAX_RATE, 2)
    shipping = SHIPPING_FEE
    grand_total = round(subtotal + tax + shipping, 2)
    
    order_id = "ord_" + uuid.uuid4().hex[:10]
    
    order = {
        "order_id": order_id,
        "user_id": DUMMY_CUSTOMER_EMAIL,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pending",
        "pricing_summary": {
            "subtotal": round(subtotal, 2),
            "tax": tax,
            "shipping": shipping,
            "grand_total": grand_total
        },
        "items": order_items,
        "shipping_address": shipping_address,
        "payment_details": {
            "last_four": payment_details.get("card_number", "")[-4:],
            "brand": "Visa"
        }
    }
    
    # Store order and empty cart
    orders.append(order)
    marketplace.ordercart(grand_total, DUMMY_CUSTOMER_EMAIL)
    
    return jsonify({
        "message": "Order placed successfully",
        "order": order
    }), 201



def get_order_date(order):
    return order.get("created_at", "")

@app.route("/orders", methods=["GET"])
def get_orders():
    user_id = "user_12345" # Hardcoded for now
    
    user_orders = []
    for order in orders:
        if order.get("user_id") == user_id:
            user_orders.append(order)
    

    sorted_orders = sorted(user_orders, key=get_order_date, reverse=True)
    
    return jsonify({"orders": sorted_orders}), 200


# Run the local development server

# --- REVIEWS ---

@app.route("/product-items/<product_id>/reviews", methods=["GET"])
def get_reviews(product_id):
    product_reviews = [r for r in reviews if r["product_id"] == product_id]
    return jsonify({"reviews": product_reviews}), 200

@app.route("/product-items/<product_id>/reviews", methods=["POST"])
def add_review(product_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400

    data = request.get_json()
    new_review = {
        "id": str(uuid.uuid4()),
        "product_id": product_id,
        "name": data.get("name", "Anonymous"),
        "rating": int(data.get("rating", 5)),
        "text": data.get("text", ""),
        "created_at": datetime.now().isoformat() + "Z"
    }
    reviews.append(new_review)
    return jsonify({"message": "Review added", "review": new_review}), 201

if __name__ == "__main__":
    app.run(port=5001,debug=True)
