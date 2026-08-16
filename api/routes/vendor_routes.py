"""
Vendor Management, Catalog, Order Fulfillment, and Analytics Routes.
"""

from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
import jwt

from auth import SECRET_KEY
from extensions import marketplace
from middleware import vendor_token_required, get_image_url
import database

vendor_bp = Blueprint("vendor_bp", __name__)


@vendor_bp.route("/vendor/register", methods=["POST"])
def register_vendor():
    """Register a new vendor store."""
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    vendor = marketplace.registerVendor(
        data.get("vendor_name"),
        data.get("password"),
        email,
        data.get("address", ""),
        phone_number=data.get("phone_number")
    )
    if not vendor:
        return jsonify({"error": "A vendor with this email already exists"}), 400

    payload = {
        "vendor_id": vendor.unique_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Vendor registered successfully", "token": token}), 201


@vendor_bp.route("/vendor/login", methods=["POST"])
def login_vendor():
    """Vendor store authentication."""
    data = request.get_json() or {}
    vendor = marketplace.loginVendor(data.get("email"), data.get("password"))
    if not vendor:
        return jsonify({"error": "Invalid email or password"}), 401
        
    if not getattr(vendor, "is_active", True):
        return jsonify({"error": "Your vendor account has been suspended by an administrator."}), 403
        
    payload = {
        "vendor_id": vendor.unique_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"message": "Login successful", "token": token}), 200


@vendor_bp.route("/vendor/products", methods=["GET"])
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


@vendor_bp.route("/vendor/products", methods=["POST"])
@vendor_token_required
def add_vendor_product(current_vendor_id):
    """Create a new product listing."""
    data = request.get_json() or {}
    stock = data.get("stock")
    if stock is not None:
        try:
            if int(stock) < 1:
                return jsonify({"error": "Initial stock must be at least 1 unit"}), 400
        except ValueError:
            return jsonify({"error": "Stock must be an integer"}), 400
    new_product = marketplace.add_product(current_vendor_id, data)
    return jsonify({"message": "Product created successfully", "product": new_product.to_dict()}), 201


@vendor_bp.route("/vendor/products/<product_id>", methods=["PUT"])
@vendor_token_required
def update_vendor_product(current_vendor_id, product_id):
    """Update product details, price, description, or stock inventory."""
    updates = request.get_json() or {}
    stock = updates.get("stock")
    if stock is not None:
        try:
            if int(stock) < 0:
                return jsonify({"error": "Stock quantity cannot be negative"}), 400
        except ValueError:
            return jsonify({"error": "Stock must be an integer"}), 400
    updated = marketplace.update_product(current_vendor_id, product_id, updates)
    return jsonify({"message": "Product updated successfully", "product": updated.to_dict()}), 200


@vendor_bp.route("/vendor/products/<product_id>", methods=["DELETE"])
@vendor_token_required
def delete_vendor_product(current_vendor_id, product_id):
    """Delete a product listing."""
    marketplace.deleteproduct(product_id, current_vendor_id)
    return jsonify({"message": "Product removed successfully"}), 200


@vendor_bp.route("/vendor/orders", methods=["GET"])
@vendor_token_required
def get_vendor_orders(current_vendor_id):
    """Retrieve all customer orders containing items from this vendor."""
    vendor_orders = marketplace.get_vendor_orders(current_vendor_id)
    return jsonify({"orders": vendor_orders}), 200


@vendor_bp.route("/vendor/orders/<order_id>", methods=["PUT"])
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


@vendor_bp.route("/vendor/orders/<order_id>/items/<product_id>/status", methods=["PUT"])
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


@vendor_bp.route("/vendor/stats", methods=["GET"])
@vendor_token_required
def get_vendor_stats(current_vendor_id):
    """Retrieve vendor high-level KPI cards (sales, active products, pending orders)."""
    stats = marketplace.get_vendor_stats(current_vendor_id)
    return jsonify(stats), 200


@vendor_bp.route("/vendor/analytics", methods=["GET"])
@vendor_token_required
def get_vendor_analytics(current_vendor_id):
    """Retrieve per-product sales performance and ratings analytics."""
    analytics = database.get_vendor_product_analytics(current_vendor_id)
    return jsonify({"analytics": analytics}), 200
