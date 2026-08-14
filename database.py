import database
import psycopg
from datetime import date
# from model.transaction import Transaction
import uuid
import mariadb
import dotenv
import os
from model.product import Product

dotenv.load_dotenv()


def connect():
    return mariadb.connect(
    host="localhost",
    user="loisamoah",
    password=os.getenv("MARIA_DB_PASS"),
    database="ecommerce",
    port=3306
)

# ------------------------------------------------------------------
# STRICT MOCK DATA (Mirroring ddl.sql EXACTLY)
# ------------------------------------------------------------------
DB_CUSTOMER = [
    {"customer_id": "CUST01", "f_name": "Dummy", "l_name": "User", "phone_number": "0241111111", "email": "dummy@example.com"},
    {"customer_id": "dummy_cust_001", "f_name": "Dummy", "l_name": "User", "phone_number": "0241111111", "email": "dummy@example.com"}
]
DB_CUSTOMER_CREDENTIALS = [
    {"customer_id": "CUST01", "password_hash": "hashed_password"},
    {"customer_id": "dummy_cust_001", "password_hash": "hashed_password"}
]

DB_VENDOR = [
    {"vendor_id": "VEND01", "vendor_name": "Dummy Vendor", "email": "dummy_vendor@example.com", "phone_number": "0242222222"},
    {"vendor_id": "vendor_001", "vendor_name": "Dummy Vendor", "email": "dummy_vendor@example.com", "phone_number": "0242222222"}
]
DB_VENDOR_CREDENTIALS = [
    {"vendor_id": "VEND01", "password_hash": "hashed_password"},
    {"vendor_id": "vendor_001", "password_hash": "hashed_password"}
]

DB_PRODUCT = [
    {"product_id": "PROD01", "vendor_id": "VEND01", "product_name": "Classic Black Leather Jacket", "description": "Premium vintage style genuine leather jacket", "price": 299.99, "stock_quantity": 50, "product_type": "fashion", "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5"},
    {"product_id": "PROD02", "vendor_id": "VEND01", "product_name": "Organic Face Wash", "description": "Gentle daily cleanser", "price": 24.99, "stock_quantity": 100, "product_type": "beauty", "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571"}
]

DB_FASHION = [
    {"product_id": "PROD01", "Color": "Black", "Material": "Leather", "Size": "M", "Gender_category": "unisex"}
]
DB_BEAUTY = [
    {"product_id": "PROD02", "skin_type": "All", "volume_weight": "150ml", "Is_organic": True}
]

DB_REVIEW = [
    {"review_id": "REV01", "product_id": "PROD01", "customer_id": "CUST01", "rating": 5, "review_date": "2024-01-01", "comment": "Great headphones!"}
]

DB_CART = []
DB_CART_ITEMS = []

DB_ORDERS = []
DB_ORDER_ITEMS = []

DB_ADDRESS = [
    {"address_id": "ADDR01", "city": "Accra", "Landmark": "Accra Mall", "street_address": "123 Main St", "customer_id": "CUST01"},
    {"address_id": "ADDR02", "city": "Accra", "Landmark": "Accra Mall", "street_address": "123 Main St", "customer_id": "dummy_cust_001"}
]

DB_SHIPPING_COMPANY = [
    {"shipping_id": "SHIP01", "name": "Speedy Delivery Ghana", "contact_phone": "+233302000001"},
    {"shipping_id": "SHIP02", "name": "EcoTransit Logistics", "contact_phone": "+233302000002"},
    {"shipping_id": "SHIP03", "name": "DropX Africa", "contact_phone": "+233302000003"},
    {"shipping_id": "SHIP04", "name": "Aramex Ghana", "contact_phone": "+233302000004"},
    {"shipping_id": "SHIP05", "name": "DHL Express Local", "contact_phone": "+233302000005"}
]

DB_DELIVERY = []

DB_PAYMENT = []
DB_CARD = []
DB_MOBILE_MONEY = []
DB_BANK_TRANSFER = []

# ------------------------------------------------------------------
# REFACTORED DATABASE FUNCTIONS (Acting on the strict tables above)
# ------------------------------------------------------------------

def searchcustomer(email):
    for c in DB_CUSTOMER:
        if c["email"] == email:
            # Need to get password hash
            pw_hash = ""
            for cred in DB_CUSTOMER_CREDENTIALS:
                if cred["customer_id"] == c["customer_id"]:
                    pw_hash = cred["password_hash"]
                    break
            # Return tuple to simulate SQL row: (customer_id, f_name, l_name, phone_number, email, password_hash)
            return (c["customer_id"], c["f_name"], c["l_name"], c["phone_number"], c["email"], pw_hash)
    return None

def searchcustomer_by_id(customer_id):
    for c in DB_CUSTOMER:
        if c["customer_id"] == customer_id:
            pw_hash = ""
            for cred in DB_CUSTOMER_CREDENTIALS:
                if cred["customer_id"] == c["customer_id"]:
                    pw_hash = cred["password_hash"]
                    break
            return (c["customer_id"], c["f_name"], c["l_name"], c["phone_number"], c["email"], pw_hash)
    return None

def register(name, userid, cart_ids, balance, password, email, first_name=None, last_name=None, phone_number=None):
    c = {
        "customer_id": userid,
        "f_name": first_name or name,
        "l_name": last_name or "",
        "phone_number": phone_number or "",
        "email": email
    }
    DB_CUSTOMER.append(c)
    DB_CUSTOMER_CREDENTIALS.append({"customer_id": userid, "password_hash": password})
    return c

def searchvendor(email):
    for v in DB_VENDOR:
        if v["email"] == email:
            pw_hash = ""
            for cred in DB_VENDOR_CREDENTIALS:
                if cred["vendor_id"] == v["vendor_id"]:
                    pw_hash = cred["password_hash"]
                    break
            # return tuple: (vendor_id, vendor_name, email, phone_number, password_hash)
            return (v["vendor_id"], v["vendor_name"], v["email"], v["phone_number"], pw_hash)
    return None

def registervendor(name, email, password, vendorid, address, phone_number=None):
    v = {
        "vendor_id": vendorid,
        "vendor_name": name,
        "email": email,
        "phone_number": phone_number or ""
    }
    DB_VENDOR.append(v)
    DB_VENDOR_CREDENTIALS.append({"vendor_id": vendorid, "password_hash": password})
    return v

def undo():
    pass

def get_all_products():
    return DB_PRODUCT

def get_all_orders():
    return DB_ORDERS

def add_order(order_dict):
    DB_ORDERS.append(order_dict)

def add_address(address_dict):
    DB_ADDRESS.append(address_dict)
    return address_dict

def get_addresses_by_customer(customer_id):
    return [addr for addr in DB_ADDRESS if addr["customer_id"] == customer_id]

def add_delivery(delivery_dict):
    DB_DELIVERY.append(delivery_dict)
    return delivery_dict

def get_delivery_by_order(order_id):
    for d in DB_DELIVERY:
        if d["order_id"] == order_id:
            return d
    return None

def get_all_shipping_companies():
    return DB_SHIPPING_COMPANY
    
def update_order(order_id, updates_dict):
    # This was historically used for status updates. Wait, status isn't in orders table directly, it's in delivery.
    # But for backward compatibility in mock, if we need to update order table.
    pass

def get_reviews_by_product(product_id):
    return [r for r in DB_REVIEW if r["product_id"] == product_id]

def add_review(review_dict):
    DB_REVIEW.append(review_dict)

def findproduct(productid):
    for p in DB_PRODUCT:
        if p["product_id"] == productid:
            return (
                p["product_id"],
                p["vendor_id"],
                p["product_name"],
                p["price"],
                p["image_url"],
                p["product_type"],
                p["description"]
            )
    return None

def addproduct(product_dict):
    DB_PRODUCT.insert(0, product_dict)

def add_fashion(fashion_dict):
    DB_FASHION.insert(0, fashion_dict)

def add_beauty(beauty_dict):
    DB_BEAUTY.insert(0, beauty_dict)

    
def updateproduct(productid, updates_dict):
    for p in DB_PRODUCT:
        if p["product_id"] == productid:
            for k, v in updates_dict.items():
                p[k] = v
            return True
    return False

def update_fashion(productid, updates_dict):
    for f in DB_FASHION:
        if f["product_id"] == productid:
            for k, v in updates_dict.items():
                f[k] = v
            return True
    return False

def update_beauty(productid, updates_dict):
    for b in DB_BEAUTY:
        if b["product_id"] == productid:
            for k, v in updates_dict.items():
                b[k] = v
            return True
    return False

def deleteproduct(productid):
    for i, p in enumerate(DB_PRODUCT):
        if p["product_id"] == productid:
            del DB_PRODUCT[i]
            # cascade delete in fashion/beauty
            for j, f in enumerate(DB_FASHION):
                if f["product_id"] == productid:
                    del DB_FASHION[j]
                    break
            for j, b in enumerate(DB_BEAUTY):
                if b["product_id"] == productid:
                    del DB_BEAUTY[j]
                    break
            return True
    return False

def viewtopproducs():
    pass

def viewhighestspender():
    pass

def highestrevenue_vendors():
    pass

def top_popular_products_categories():
    pass

def addtocart(product, customer_id, quantity):
    # Support both a Product object and a tuple: (product_id, vendor_id, ...)
    if hasattr(product, 'product_id'):
        product_id = product.product_id
    else:
        product_id = product[0]

    
    # Ensure cart exists
    cart_id = None
    for c in DB_CART:
        if c["customer_id"] == customer_id:
            cart_id = c["cart_id"]
            break
            
    if not cart_id:
        cart_id = "CART" + customer_id
        DB_CART.append({"cart_id": cart_id, "customer_id": customer_id})
        
    # Check if item in cart
    for ci in DB_CART_ITEMS:
        if ci["cart_id"] == cart_id and ci["product_id"] == product_id:
            ci["quantity"] += quantity
            return True
            
    DB_CART_ITEMS.append({"product_id": product_id, "cart_id": cart_id, "quantity": quantity, "added_date": str(date.today())})
    return True

def getcart(customer_id):
    # Returning the structure mock_api/app.py expects, but querying from strict DB tables
    cart_id = None
    for c in DB_CART:
        if c["customer_id"] == customer_id:
            cart_id = c["cart_id"]
            break
            
    if not cart_id:
        return []
        
    items = []
    for ci in DB_CART_ITEMS:
        if ci["cart_id"] == cart_id:
            # find product
            for p in DB_PRODUCT:
                if p["product_id"] == ci["product_id"]:
                    product_obj = Product(
                        product_name=p["product_name"],
                        vendor_id=p["vendor_id"],
                        price=p["price"],
                        image_url=p["image_url"],
                        product_type=p["product_type"],
                        product_id=p["product_id"],
                        description=p["description"]
                    )
                    items.append({"product": product_obj, "quantity": ci["quantity"]})
    return items

def removefromcart(product_id, customer_id):
    cart_id = None
    for c in DB_CART:
        if c["customer_id"] == customer_id:
            cart_id = c["cart_id"]
            break
    if not cart_id:
        return False
        
    for i, ci in enumerate(DB_CART_ITEMS):
        if ci["cart_id"] == cart_id and ci["product_id"] == product_id:
            DB_CART_ITEMS.pop(i)
            return True
    return False

def checkout(customer_id):
    cart_id = None
    for c in DB_CART:
        if c["customer_id"] == customer_id:
            cart_id = c["cart_id"]
            break
    if not cart_id:
        return False
        
    # Remove cart items
    global DB_CART_ITEMS
    DB_CART_ITEMS = [ci for ci in DB_CART_ITEMS if ci["cart_id"] != cart_id]
    return True
