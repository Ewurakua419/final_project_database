"""
Customer Authentication and Profile Management Routes.
"""

from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
import jwt

from auth import SECRET_KEY
from extensions import marketplace
from middleware import token_required
import database
from model.address import Address

customer_bp = Blueprint("customer_bp", __name__)


@customer_bp.route("/register", methods=["POST"])
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


@customer_bp.route("/login", methods=["POST"])
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


@customer_bp.route("/customer/profile", methods=["GET"])
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


@customer_bp.route("/customer/profile", methods=["PUT"])
@token_required
def update_customer_profile(current_user_id):
    """Update customer profile information."""
    data = request.get_json() or {}
    profile = marketplace.update_customer_profile(current_user_id, data)
    return jsonify(profile), 200


@customer_bp.route("/customer/addresses", methods=["POST"])
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


@customer_bp.route("/customer/addresses/<address_id>", methods=["DELETE"])
@token_required
def delete_customer_address(current_user_id, address_id):
    """Delete an address securely with foreign key safety."""
    success = database.delete_address(address_id, current_user_id)
    if success:
        return jsonify({"message": "Address removed successfully"}), 200
    return jsonify({"error": "Address not found or does not belong to you"}), 404
