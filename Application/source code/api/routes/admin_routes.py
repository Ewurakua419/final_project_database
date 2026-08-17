"""
Administrator Portal and Marketplace Analytics Routes.
"""

from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
import jwt

from auth import SECRET_KEY
import auth
from middleware import admin_token_required
import database

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route("/admin/login", methods=["POST"])
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


@admin_bp.route("/admin/stats", methods=["GET"])
@admin_token_required
def get_admin_stats():
    """Platform overview KPIs."""
    stats = database.get_admin_stats()
    return jsonify(stats), 200


@admin_bp.route("/admin/users", methods=["GET"])
@admin_token_required
def get_admin_users():
    """Retrieve full registered user base (customers, vendors, carriers)."""
    users = database.get_admin_users()
    return jsonify({"users": users}), 200


@admin_bp.route("/admin/users/<user_id>/toggle-status", methods=["PUT"])
@admin_token_required
def toggle_user_status(user_id):
    """Suspend or reactivate a customer/vendor account."""
    data = request.get_json() or {}
    role = data.get("role")
    if role not in ("customer", "vendor"):
        return jsonify({"error": "Invalid role specified. Allowed: 'customer', 'vendor'"}), 400
        
    if role == "customer":
        row = database.run_query("SELECT is_active FROM customer WHERE customer_id = %s", (user_id,), fetch='one')
    else:
        row = database.run_query("SELECT is_active FROM vendor WHERE vendor_id = %s", (user_id,), fetch='one')
        
    if not row:
        return jsonify({"error": "User not found"}), 404
        
    new_status = not row[0]
    
    if role == "customer":
        database.run_query("UPDATE customer SET is_active = %s WHERE customer_id = %s", (new_status, user_id), commit=True)
    else:
        database.run_query("UPDATE vendor SET is_active = %s WHERE vendor_id = %s", (new_status, user_id), commit=True)
        
    return jsonify({
        "message": "User status updated successfully",
        "is_active": new_status
    }), 200


@admin_bp.route("/admin/analytics", methods=["GET"])
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


@admin_bp.route("/admin/shipping-companies", methods=["GET"])
@admin_token_required
def get_admin_shipping_companies():
    """Admin view of all shipping partners with logistics metrics."""
    carriers = database.get_all_shipping_companies()
    return jsonify({"shipping_companies": carriers}), 200


@admin_bp.route("/admin/shipping-companies", methods=["POST"])
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
