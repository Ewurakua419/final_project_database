import psycopg
from datetime import date
from model.transaction import Transaction
import uuid
import mariadb
def connect():
    return mariadb.connect(
    host="localhost",
    user="loisamoah",
    password="9002",
    database="ecommerce",
    port=3306
)
##Write data
# cur.execute("INSERT INTO students (name, age) VALUES (%s, %s)",("Alice", 20))
# conn.commit()

##read data
# cur.execute("SELECT * FROM students")
# rows = cur.fetchall()
MOCK_USERS = [
    {
        "unique_id": "dummy_cust_001",
        "name": "Dummy User",
        "password": "hashed_password", # doesn't matter for cart
        "cart_ids": "cart_001",
        "email": "dummy@example.com"
    }
]
MOCK_VENDORS = [
    {
        "unique_id": "vendor_001",
        "name": "Dummy Vendor",
        "email": "dummy_vendor@example.com",
        "password": "hashed_password",
        "address": "123 Vendor St"
    }
]
from mock_api.products import products as MOCK_PRODUCTS
from mock_api.orders import orders
from mock_api.reviews import reviews as mock_api_reviews

# --- MOCK DATA ---
MOCK_CARTS = {} # Maps customer_id to a list of items: [{"product": product, "quantity": quantity}]
MOCK_ORDERS = orders

# Map the old mock review format to the new DB format
MOCK_REVIEWS = []
for r in mock_api_reviews:
    MOCK_REVIEWS.append({
        "review_id": r["id"],
        "product_id": r["product_id"],
        "customer_id": "dummy@example.com", # Mock mapping
        "comment": r["text"],
        "rating": r["rating"],
        "review_date": r["created_at"]
    })

def searchcustomer(email):
    # with connect() as conn:
    #     with conn.cursor() as cur:
    #         cur.execute(
    #             """
    #             SELECT customer.*, cart.cart_id, cart_items.product_id
    #             FROM customer
    #             JOIN cart
    #                 ON customer.customer_id = cart.customer_id
    #             JOIN cart_items
    #                 ON cart.cart_id = cart_items.cart_id
    #             JOIN customer_credentials
    #                 ON customer.customer_id = customer_credentials.customer_id
    #             WHERE customer.email = %s
    #             """,
    #             (email,)
    #         )
    #         rows = cur.fetchone()
    #         if not rows:
    #             return None
    #         return rows
    
    # --- MOCK LOGIC ---
    for u in MOCK_USERS:
        if u["email"] == email:
            # Returning tuple to simulate SQL row: (unique_id, name, password, cart_ids, email, first_name, last_name, phone_number)
            return (u["unique_id"], u["name"], u["password"], "cart_mock", u["email"], u.get("first_name", ""), u.get("last_name", ""), u.get("phone_number", ""))
    return None


def login(email, password):
    # with connect() as conn:
    #     with conn.cursor() as cur:
    #         cur.execute(
    #             """
    #             SELECT customer.*,cart.id,customer_credentials.password_hash
    #             FROM customer
    #             JOIN customer_credentials
    #                 ON customer.customer_id = customer_credentials.customer_id
    #             WHERE customer.email = %s""",
    #             (email, ),
    #         )
    #         rows = cur.fetchone()
    #         if not rows:
    #             return None
    #         if password==rows[-1]:
    #             return rows
    
    # --- MOCK LOGIC ---
    pass # In our new architecture, marketplace.py handles verification itself using searchcustomer


def register(name, userid, cart_ids, balance, password, email, first_name=None, last_name=None, phone_number=None):
    # f_name, l_name from original function definition are preserved conceptually below
    # pass
    
    # --- MOCK LOGIC ---
    new_user = {
        "unique_id": userid,
        "name": name,
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number
    }
    MOCK_USERS.append(new_user)
    return new_user

def searchvendor(email):
    # with connect() as conn:
    #     with conn.cursor() as cur:
    #         cur.execute(
    #             """
    #             SELECT vendor.*, vendor_credentials.password_hash
    #             FROM vendor
    #             JOIN vendor_credentials
    #                 ON vendor.vendor_id = vendor_credentials.vendor_id
    #             WHERE vendor.email = %s
    #             """,
    #             (email,)
    #         )
    #         rows = cur.fetchone()
    #         if not rows:
    #             return None
    #         return rows
    
    # --- MOCK LOGIC ---
    for v in MOCK_VENDORS:
        if v["email"] == email:
            # Return tuple to simulate SQL row: (address, name, unique_id, email, password, phone_number)
            return (v.get("address", ""), v["name"], v["unique_id"], v["email"], v["password"], v.get("phone_number", ""))
    return None

def registervendor(name, email, password, vendorid, address, phone_number=None):
    # with connect() as conn:
    #     with conn.cursor() as cur:
    #         cur.execute("INSERT INTO vendor ...")
    #         conn.commit()
    
    # --- MOCK LOGIC ---
    new_vendor = {
        "unique_id": vendorid,
        "name": name,
        "email": email,
        "password": password,
        "address": address,
        "phone_number": phone_number
    }
    MOCK_VENDORS.append(new_vendor)
    return new_vendor

def undo():
    with connect() as conn:
        conn.rollback()


def get_all_products():
    return MOCK_PRODUCTS

def get_all_orders():
    return MOCK_ORDERS

def add_order(order_dict):
    MOCK_ORDERS.append(order_dict)
    
def update_order(order_id, updates_dict):
    for o in MOCK_ORDERS:
        if o["order_id"] == order_id:
            for k, v in updates_dict.items():
                o[k] = v
            return True
    return False

def get_reviews_by_product(product_id):
    return [r for r in MOCK_REVIEWS if r["product_id"] == product_id]

def add_review(review_dict):
    MOCK_REVIEWS.append(review_dict)

def findproduct(productid):
    for p in MOCK_PRODUCTS:
        if p["id"] == productid:
            # Return tuple: (product_id, vendor_id, product_name, price, image_url, product_type, description)
            return (
                p["id"],
                p["vendor_id"],
                p["name"],
                p.get("priceCents", 0),
                p.get("image", ""),
                p.get("type", ""),
                p.get("description", "")
            )
    return None

def addproduct(product_dict):
    # product_dict should match the frontend format
    MOCK_PRODUCTS.insert(0, product_dict)
    
def updateproduct(productid, updates_dict):
    for p in MOCK_PRODUCTS:
        if p["id"] == productid:
            for k, v in updates_dict.items():
                p[k] = v
            return True
    return False

def deleteproduct(productid):
    for i, p in enumerate(MOCK_PRODUCTS):
        if p["id"] == productid:
            del MOCK_PRODUCTS[i]
            return True
    return False

def viewtopproducs():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT
                p.product_id,
                p.product_name,
                SUM(ci.quantity) AS total_units_sold
            FROM `Order` o
            JOIN Cart_Item ci
                ON o.cart_id = ci.cart_id
            JOIN Product p
                ON ci.product_id = p.product_id
            GROUP BY
                p.product_id,
                p.product_name
            ORDER BY total_units_sold DESC
            """)
            rows = cur.fetchall()
            return rows

def viewhighestspender():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT
                c.customer_id,
                c.f_name,
                c.l_name,
                SUM(o.subtotal + o.shipping_fee) AS total_spent
            FROM Customer c
            JOIN `Order` o
                ON c.customer_id = o.customer_id
            GROUP BY
                c.customer_id,
                c.f_name,
                c.l_name
            ORDER BY total_spent DESC
            LIMIT 1
            """)
            rows = cur.fetchall()
            return rows

def highestrevenue_vendors():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT
                    v.vendor_id,
                    v.vendor_name,
                    SUM(ci.quantity * p.price) AS total_revenue
                FROM Vendor v
                JOIN Product p
                    ON v.vendor_id = p.vendor_id
                JOIN Cart_Item ci
                    ON p.product_id = ci.product_id
                JOIN `Order` o
                    ON ci.cart_id = o.cart_id
                GROUP BY
                    v.vendor_id,
                    v.vendor_name
                ORDER BY total_revenue DESC """)
            rows = cur.fetchall()
            return rows

def top_popular_products_categories():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""WITH ProductCategories AS (
                    SELECT product_id, 'Fashion' AS category
                    FROM Fashion

                    UNION ALL

                    SELECT product_id, 'Beauty' AS category
                    FROM Beauty
                )
                SELECT
                    pc.category,
                    SUM(oi.quantity) AS units_sold
                FROM ProductCategories pc
                JOIN Order_Item oi
                    ON pc.product_id = oi.product_id
                GROUP BY pc.category
                ORDER BY units_sold DESC

                """)
            rows = cur.fetchall()
            return rows

def addtocart(product, customer_id, quantity):
    # dates=date.today()
    # if searchcustomer(customer.email)!=None:
    #     with connect() as conn:
    #             with conn.cursor() as cur:
    #                 cur.execute(
    #                     """
    #                     SELECT cart_id
    #                     FROM  cart
    #                     WHERE where cart.customer_id = %s """,
    #                     (customer.customer_id,),
    #                 )
    #                 ... (SQL commented out)
    
    # --- MOCK LOGIC ---
    if customer_id not in MOCK_CARTS:
        MOCK_CARTS[customer_id] = []
        
    # Check if item already exists in cart, update quantity if it does
    for item in MOCK_CARTS[customer_id]:
        if item["product"].product_id == product.product_id:
            item["quantity"] += quantity
            return True
            
    MOCK_CARTS[customer_id].append({"product": product, "quantity": quantity})
    return True

def getcart(customer_id):
    return MOCK_CARTS.get(customer_id, [])

def removefromcart(product_id, customer_id):
    if customer_id in MOCK_CARTS:
        for i, item in enumerate(MOCK_CARTS[customer_id]):
            if item["product"].product_id == product_id:
                MOCK_CARTS[customer_id].pop(i)
                return True
    return False

def checkout(customer_id):
    if customer_id not in MOCK_CARTS or not MOCK_CARTS[customer_id]:
        return False
    
    # In a real DB, you would move items from Cart to Order tables here.
    # For now, we just clear the mock cart.
    MOCK_CARTS[customer_id] = []
    return True
