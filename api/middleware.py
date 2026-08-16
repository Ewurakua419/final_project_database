"""
Authentication decorators and request helper utilities for the API.
"""

import sys
import os
from functools import wraps
from flask import request, jsonify
import jwt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import SECRET_KEY


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
            
        # Check customer account status
        import database
        is_active = database.run_query("SELECT is_active FROM customer WHERE customer_id = %s", (current_user_id,), fetch='one')
        if not is_active or not is_active[0]:
            return jsonify({"error": "Your account has been suspended by an administrator."}), 403
            
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
            
        # Check vendor account status
        import database
        is_active = database.run_query("SELECT is_active FROM vendor WHERE vendor_id = %s", (current_vendor_id,), fetch='one')
        if not is_active or not is_active[0]:
            return jsonify({"error": "Your vendor account has been suspended by an administrator."}), 403
            
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
