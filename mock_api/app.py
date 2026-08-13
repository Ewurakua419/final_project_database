from products import products
from cart import cart
from vendors import vendors
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
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    for v in vendors:
        if v["email"] == email:
            return jsonify({"error": "Vendor already exists"}), 409
            
    hashed_password = encodere(password)
    
    new_vendor = {
        "id": "vendor_" + uuid.uuid4().hex[:10],
        "email": email,
        "password": hashed_password
    }
    vendors.append(new_vendor)
    
    return jsonify({
        "message": "Vendor registered successfully", 
        "vendor_id": new_vendor["id"]
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
        
    vendor = None
    for v in vendors:
        if v["email"] == email:
            vendor = v
            break
            
    if not vendor:
        return jsonify({"error": "Invalid email or password"}), 401
        
    if not decodere(password, vendor["password"]):
        return jsonify({"error": "Invalid email or password"}), 401
        
    payload = {
        "vendor_id": vendor["id"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return jsonify({
        "message": "Login successful",
        "token": token
    }), 200

@app.route("/product-items", methods = ["GET"])
def get_products():
    processed_products = []

    for product in products:
        product_copy = product.copy()
        product_copy['image'] = get_image_url(product_copy['image'])
        processed_products.append(product_copy)
        
    return jsonify({"products": processed_products}), 200

@app.route("/product-items/<product_id>", methods=["GET"])
def get_product(product_id):
    product = find_product(product_id)
    if product:
        product_copy = product.copy()
        product_copy['image'] = get_image_url(product_copy['image'])
        return jsonify(product_copy), 200
    return jsonify({"error": "Product not found"}), 404


@app.route("/vendor/products", methods=["GET"])
def get_vendor_products():
     # Hardcoded active vendor
    vendor_products = []
    
    for product in products:
        if product.get("vendor_id") == vendor_id:
            product_copy = product.copy()
            product_copy['image'] = get_image_url(product_copy['image'])
            vendor_products.append(product_copy)
            
    return jsonify({"products": vendor_products}), 200

@app.route("/vendor/products", methods=["POST"])
def add_vendor_product():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    
    if not data.get("name") or not data.get("priceCents") or not data.get("image"):
        return jsonify({"error": "Missing required fields"}), 400
        
    new_product = {
        "id": str(uuid.uuid4()),
        "name": data.get("name"),
        "image": data.get("image"),
        "priceCents": int(data.get("priceCents")),
        "type": data.get("type", "General"),
        "vendor_id": vendor_id,
        "rating": {"stars": 0, "count": 0},
        "description": data.get("description", ""),
        "keywords": [],
        "brand": data.get("brand", ""),
        "stock": int(data.get("stock", 0))
    }
    
    products.insert(0, new_product) # Add to the top of the list
    return jsonify({"message": "Product created successfully", "product": new_product}), 201

@app.route("/vendor/products/<product_id>", methods=["PUT"])
def update_vendor_product(product_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400
        
    data = request.get_json()
    product = find_product(product_id)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    if product.get("vendor_id") != vendor_id:
        return jsonify({"error": "Unauthorized"}), 403
        
    # Update fields dynamically
    allowed_string_fields = ["name", "image", "type", "description", "brand"]
    for field in allowed_string_fields:
        if field in data:
            product[field] = data[field]
            
    if "priceCents" in data:
        product["priceCents"] = int(data["priceCents"])
    if "stock" in data:
        product["stock"] = int(data["stock"])
        
    return jsonify({"message": "Product updated successfully", "product": product}), 200

@app.route("/vendor/products/<product_id>", methods=["DELETE"])
def delete_vendor_product(product_id):
    product = find_product(product_id)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    if product.get("vendor_id") != vendor_id:
        return jsonify({"error": "Unauthorized"}), 403
        
    products.remove(product)
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




@app.route("/cart", methods=["GET"])
def get_cart():
    cart_items = []
    total_price = 0
    for item in cart:
        item_id = item["prodID"]
        quantity = item["quantity"]
        product = find_product(item_id)
        
        if product:
            product_copy = product.copy()
            product_copy['image'] = get_image_url(product_copy['image'])
            
            item_total = product_copy.get("priceCents", 0) * quantity
            total_price += item_total
            
            cart_items.append({
                "product": product_copy,
                "quantity": quantity,
                "item_total": round(item_total, 2)
            })

    return jsonify({
        "cart": cart_items,
        "total_items": sum(item["quantity"] for item in cart),
        "total_price": round(total_price, 2)
    }), 200


@app.route("/cart", methods=["POST"])
def add_to_cart():
    #ensure the request is in JSON format
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400

    data = request.get_json()

    prod_id = data.get("prodID")
    quantity = data.get("quantity")

    #validate prod ID and quantity
    if not prod_id or not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "Invalid prodID or quantity"}), 400

    # Validate product exists
    if not find_product(prod_id):
        return jsonify({"error": "Product not found"}), 404

    # Check if item already exists in cart
    for item in cart:
        if item["prodID"] == prod_id:
            item["quantity"] += quantity
            return jsonify({"message": "Item updated in cart"}), 200

    cart.append({"prodID": prod_id, "quantity": quantity})
    return jsonify({"message": "Item added to cart successfully"}), 201


@app.route("/cart/<product_id>", methods=["DELETE"])
def remove_item_completely(product_id):
  # loop through cart and remove the item
    for item in cart:
        if item["prodID"] == product_id:
            cart.remove(item)
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

    target_item = None
    for item in cart:
        if item["prodID"] == product_id:
            target_item = item
            break

    if quantity == 0:
        cart.remove(target_item)
        return jsonify({"message": "Item quantity reached 0 and was removed"}), 200
        
    if target_item:
      target_item["quantity"] = quantity
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
    
    if len(cart) == 0:
        return jsonify({"error": "Cart is empty"}), 400
        
    subtotal = 0
    order_items = []
    
    for item in cart:
        prod = find_product(item["prodID"])
        if prod:
            price_dollars = prod.get("priceCents", 0) / 100
            item_total = price_dollars * item["quantity"]
            subtotal += item_total
            order_items.append({
                "product_id": prod["id"],
                "name": prod["name"],
                "image": get_image_url(prod["image"]),
                "price_at_purchase": price_dollars,
                "quantity": item["quantity"],
                "item_total": round(item_total, 2)
            })
            
    tax = round(subtotal * TAX_RATE, 2) # 8% tax
    shipping = SHIPPING_FEE
    grand_total = round(subtotal + tax + shipping, 2)
    
    order_id = "ord_" + uuid.uuid4().hex[:10]
    
    order = {
        "order_id": order_id,
        "user_id": "user_12345",
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
        "payment_details": payment_details
    }
    
    orders.append(order)
    cart.clear() # Empty the cart after successful checkout
    
    return jsonify(order), 200



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
