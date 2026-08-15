"""
Extensions and shared services for the Flask API.
"""

import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.marketplace import Marketplace

marketplace = Marketplace(name="Ashesi E-Commerce Marketplace")
