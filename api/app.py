"""
==============================================================================
Marketplace REST API - Application Entrypoint
==============================================================================
Initializes the Flask application, registers domain blueprints, configures
CORS for frontend access, and starts the development server.
==============================================================================
"""

import sys
import os
from flask import Flask
from flask_cors import CORS

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Route Blueprints
from routes.customer_routes import customer_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.vendor_routes import vendor_bp
from routes.shipping_routes import shipping_bp
from routes.admin_routes import admin_bp


def create_app():
    """Application factory for the Marketplace API."""
    app = Flask(__name__)

    # Configure Cross-Origin Resource Sharing
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://127.0.0.1:5500",
                "http://localhost:5500",
                "http://127.0.0.1:5001",
                "http://localhost:5001",
                "http://127.0.0.1:8000",
                "http://localhost:8000"
            ]
        }
    })

    # Register Domain Blueprints
    app.register_blueprint(customer_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(shipping_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)
