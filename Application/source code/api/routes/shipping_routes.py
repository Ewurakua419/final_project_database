"""
Logistics and Shipping Partner Routes.
"""

from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
import jwt

from auth import SECRET_KEY
import auth
from middleware import shipping_token_required
import database

shipping_bp = Blueprint("shipping_bp", __name__)


@shipping_bp.route("/shipping-companies", methods=["GET"])
def get_public_shipping_companies():
    """Public carrier lookup for customer checkout selection."""
    carriers = database.get_all_shipping_companies()
    return jsonify({"shipping_companies": carriers}), 200


@shipping_bp.route("/shipping/login", methods=["POST"])
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


@shipping_bp.route("/shipping/deliveries", methods=["GET"])
@shipping_token_required
def get_shipping_deliveries(current_shipping_id):
    """Retrieve all deliveries assigned to this logistics carrier with earnings."""
    result = database.get_deliveries_by_shipping_company(current_shipping_id)
    return jsonify(result), 200


@shipping_bp.route("/shipping/deliveries/<delivery_id>", methods=["PUT"])
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
