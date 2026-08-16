"""
Shopping Cart, Checkout, and Customer Orders Routes.
"""

from flask import Blueprint, request, jsonify

from extensions import marketplace
from middleware import token_required, get_image_url

cart_bp = Blueprint("cart_bp", __name__)


@cart_bp.route("/cart", methods=["GET"])
@token_required
def get_cart(current_user_id):
    """Retrieve current customer cart items and subtotal."""
    result = marketplace.get_cart(current_user_id)
    for item in result.get("cart", []):
        if "product" in item and "image" in item["product"]:
            item["product"]["image"] = get_image_url(item["product"]["image"])
    return jsonify(result), 200


@cart_bp.route("/cart", methods=["POST"])
@token_required
def add_to_cart(current_user_id):
    """Add an item to customer cart with stock availability validation."""
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id or quantity <= 0:
        return jsonify({"error": "Valid product ID and positive quantity are required"}), 400

    try:
        marketplace.add_to_cart(product_id, current_user_id, quantity)
        return jsonify({"message": "Item added to cart successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@cart_bp.route("/cart/<product_id>", methods=["DELETE"])
@token_required
def remove_cart_item(current_user_id, product_id):
    """Remove a product from the customer's cart."""
    marketplace.remove_from_cart(product_id, current_user_id)
    return jsonify({"message": "Item removed from cart"}), 200


@cart_bp.route("/cart/<product_id>/quantity", methods=["PUT"])
@token_required
def update_cart_item_qty(current_user_id, product_id):
    """Update item quantity in cart with real-time stock checks."""
    data = request.get_json() or {}
    qty = int(data.get("quantity", 0))
    
    import database
    try:
        if qty <= 0:
            marketplace.remove_from_cart(product_id, current_user_id)
        else:
            database.update_cart_qty(product_id, current_user_id, qty)
        return jsonify({"message": "Cart updated successfully"}), 200
    except Exception as e:
        err_msg = str(e)
        if "Insufficient stock" in err_msg or "insufficient stock" in err_msg.lower():
            err_msg = "Insufficient stock available"
        return jsonify({"error": err_msg}), 400


@cart_bp.route("/checkout", methods=["POST"])
@token_required
def process_checkout(current_user_id):
    """Process customer order checkout, create delivery record and record payment."""
    data = request.get_json() or {}
    try:
        order = marketplace.checkout(
            current_user_id,
            shipping_address=data.get("shipping_address"),
            payment_details=data.get("payment_details"),
            shipping_fee=float(data.get("shipping_fee", 5.00)),
            shipping_id=data.get("shipping_id")
        )
        if order is None:
            return jsonify({"error": "Cart is empty or order could not be placed"}), 400
        return jsonify(order.to_dict()), 201
    except Exception as e:
        err_msg = str(e)
        if "Insufficient stock" in err_msg or "insufficient stock" in err_msg.lower():
            err_msg = "Insufficient stock available for one of the items in your cart."
        elif "Cannot place an order with an empty cart" in err_msg:
            err_msg = "Cannot place an order with an empty cart"
        return jsonify({"error": err_msg}), 400


@cart_bp.route("/orders", methods=["GET"])
@token_required
def get_customer_orders(current_user_id):
    """Retrieve full order history for the logged-in customer."""
    orders = marketplace.get_customer_orders(current_user_id)
    return jsonify({"orders": orders}), 200
