"""
Product Catalog and Reviews Routes.
"""

from flask import Blueprint, request, jsonify

from extensions import marketplace
from middleware import token_required, get_image_url

product_bp = Blueprint("product_bp", __name__)


@product_bp.route("/product-items", methods=["GET"])
def get_products():
    """Retrieve full catalog of marketplace products."""
    products = marketplace.get_all_products()
    processed = []
    for p in products:
        d = p.to_dict()
        d['image'] = get_image_url(d.get('image', ''))
        processed.append(d)
    return jsonify({"products": processed}), 200


@product_bp.route("/product-items/<product_id>", methods=["GET"])
def get_product(product_id):
    """Retrieve detailed product specifications and attributes."""
    product = marketplace.findproduct(product_id)
    if product:
        d = product.to_dict()
        d['image'] = get_image_url(d.get('image', ''))
        return jsonify(d), 200
    return jsonify({"error": "Product not found"}), 404


@product_bp.route("/product-items/<product_id>/reviews", methods=["GET"])
@product_bp.route("/products/<product_id>/reviews", methods=["GET"])
def get_product_reviews(product_id):
    """Retrieve all verified customer reviews for a product."""
    reviews = marketplace.get_product_reviews(product_id)
    return jsonify({"reviews": [r.to_dict() for r in reviews]}), 200


@product_bp.route("/product-items/<product_id>/reviews", methods=["POST"])
@product_bp.route("/products/<product_id>/reviews", methods=["POST"])
@token_required
def add_product_review(current_user_id, product_id):
    """Add a customer review and rating (1-5 stars) for a product."""
    data = request.get_json() or {}
    rating = data.get("rating")
    comment = data.get("text") or data.get("comment", "")
    
    if not rating or not comment:
        return jsonify({"error": "Rating and comment are required"}), 400

    try:
        review = marketplace.add_product_review(product_id, current_user_id, comment, int(rating))
        return jsonify(review.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
