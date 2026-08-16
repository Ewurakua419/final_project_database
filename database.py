import mariadb
import os
import dotenv
from datetime import date
import uuid
from model.product import Product

dotenv.load_dotenv()

def connect():
    return mariadb.connect(
        host="localhost",
        user="harisissah",
        password=os.getenv("MARIA_DB_PASS"),
        database="ecommerce",
        port=3306
    )

def run_query(query, params=None, fetch=None, commit=False):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
            return cursor.rowcount
        if fetch == 'all':
            return cursor.fetchall()
        if fetch == 'one':
            return cursor.fetchone()
        return None
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# REFACTORED DATABASE FUNCTIONS (Acting on MariaDB using SQL)
# ------------------------------------------------------------------

def searchcustomer(email):
    query = """
        SELECT c.customer_id, c.f_name, c.l_name, c.phone_number, c.email, cc.password_hash, c.is_active
        FROM customer c 
        JOIN customer_credentials cc ON c.customer_id = cc.customer_id 
        WHERE LOWER(c.email) = LOWER(%s)
    """
    row = run_query(query, (email.strip(),), fetch='one')
    if row:
        return (row[0], row[1], row[2], row[3], row[4], row[5], bool(row[6]))
    return None

def searchcustomer_by_id(customer_id):
    query = """
        SELECT c.customer_id, c.f_name, c.l_name, c.phone_number, c.email, cc.password_hash, c.is_active 
        FROM customer c 
        JOIN customer_credentials cc ON c.customer_id = cc.customer_id 
        WHERE c.customer_id = %s
    """
    row = run_query(query, (customer_id[:6],), fetch='one')
    if row:
        return (row[0], row[1], row[2], row[3], row[4], row[5], bool(row[6]))
    return None

def register(name, userid, cart_ids, balance, password, email, first_name=None, last_name=None, phone_number=None):
    userid = userid[:6]
    cart_id = cart_ids[:6] if cart_ids else "CRT" + userid[:3]
    f_name = first_name or (name.split(" ")[0] if name else "")
    l_name = last_name or (name.split(" ")[1] if name and len(name.split(" ")) > 1 else "")
    
    conn = connect()
    cursor = conn.cursor()
    try:
        # Insert customer
        cursor.execute(
            "INSERT INTO customer (customer_id, f_name, l_name, phone_number, email) VALUES (%s, %s, %s, %s, %s)",
            (userid, f_name, l_name, phone_number or "", email)
        )
        # Insert credentials
        cursor.execute(
            "INSERT INTO customer_credentials (customer_id, password_hash) VALUES (%s, %s)",
            (userid, password)
        )
        # Insert cart
        cursor.execute(
            "INSERT INTO cart (cart_id, customer_id) VALUES (%s, %s)",
            (cart_id, userid)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
    
    return {
        "customer_id": userid,
        "f_name": f_name,
        "l_name": l_name,
        "phone_number": phone_number or "",
        "email": email
    }

def searchvendor(email):
    query = """
        SELECT v.vendor_id, v.vendor_name, v.email, v.phone_number, vc.password_hash, v.is_active 
        FROM vendor v 
        JOIN vendor_credentials vc ON v.vendor_id = vc.vendor_id 
        WHERE LOWER(v.email) = LOWER(%s)
    """
    row = run_query(query, (email.strip(),), fetch='one')
    if row:
        return (row[0], row[1], row[2], row[3], row[4], bool(row[5]))
    return None

def registervendor(name, email, password, vendorid, address, phone_number=None):
    vendorid = vendorid[:6]
    conn = connect()
    cursor = conn.cursor()
    try:
        # Insert vendor
        cursor.execute(
            "INSERT INTO vendor (vendor_id, vendor_name, email, phone_number) VALUES (%s, %s, %s, %s)",
            (vendorid, name, email, phone_number or "")
        )
        # Insert credentials
        cursor.execute(
            "INSERT INTO vendor_credentials (vendor_id, password_hash) VALUES (%s, %s)",
            (vendorid, password)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
        
    return {
        "vendor_id": vendorid,
        "vendor_name": name,
        "email": email,
        "phone_number": phone_number or ""
    }

def get_all_products():
    query = """
        SELECT product_id, vendor_id, product_name, description, price, stock_quantity, product_type, image_url 
        FROM product
        WHERE is_active = TRUE
    """
    rows = run_query(query, fetch='all')
    products = []
    for row in rows:
        products.append({
            "product_id": row[0],
            "vendor_id": row[1],
            "product_name": row[2],
            "description": row[3],
            "price": float(row[4]),
            "stock_quantity": row[5],
            "product_type": row[6],
            "image_url": row[7]
        })
    return products

def get_all_orders():
    # 1. Fetch all orders
    query = "SELECT order_id, customer_id, cart_id, order_date, subtotal, shipping_fee FROM orders"
    order_rows = run_query(query, fetch='all')
    
    orders = []
    for o_row in order_rows:
        order_id = o_row[0]
        customer_id = o_row[1]
        cart_id = o_row[2]
        order_date = o_row[3].isoformat() if hasattr(o_row[3], 'isoformat') else str(o_row[3])
        subtotal = float(o_row[4])
        shipping_fee = float(o_row[5])
        
        # 2. Fetch delivery status and details
        del_query = """
            SELECT d.delivery_status, d.address_id, d.shipping_id, d.estimated_delivery_date, sc.name
            FROM delivery d
            LEFT JOIN shipping_company sc ON d.shipping_id = sc.shipping_id
            WHERE d.order_id = %s LIMIT 1
        """
        del_row = run_query(del_query, (order_id,), fetch='one')
        status = "pending"
        address_id = None
        delivery_obj = None
        if del_row:
            status = "sent to port" if del_row[0] == "in port" else del_row[0]
            address_id = del_row[1]
            delivery_obj = {
                "delivery_status": "sent to port" if del_row[0] == "in port" else del_row[0],
                "estimated_delivery_date": str(del_row[3]) if del_row[3] else "N/A",
                "shipping_company": del_row[4] or "N/A"
            }
            
        # 3. Fetch address
        addr_dict = None
        if address_id:
            addr_query = "SELECT street_address, city, Landmark FROM address WHERE address_id = %s LIMIT 1"
            addr_row = run_query(addr_query, (address_id,), fetch='one')
            if addr_row:
                addr_dict = {
                    "id": address_id,
                    "street": addr_row[0],
                    "city": addr_row[1],
                    "country": addr_row[2]
                }
                
        # 4. Fetch payment details
        pay_query = "SELECT payment_id, payment_type FROM payment WHERE order_id = %s LIMIT 1"
        pay_row = run_query(pay_query, (order_id,), fetch='one')
        pay_dict = None
        if pay_row:
            pay_id = pay_row[0]
            pay_type = pay_row[1]
            
            last_4 = ""
            brand = pay_type
            
            if pay_type == 'card':
                card_query = "SELECT card_num FROM card WHERE payment_id = %s LIMIT 1"
                card_row = run_query(card_query, (pay_id,), fetch='one')
                if card_row:
                    last_4 = card_row[0][-4:] if len(card_row[0]) >= 4 else card_row[0]
                    brand = "Card"
            elif pay_type == 'mobile money':
                momo_query = "SELECT phone_number, network FROM mobile_money WHERE payment_id = %s LIMIT 1"
                momo_row = run_query(momo_query, (pay_id,), fetch='one')
                if momo_row:
                    last_4 = momo_row[0][-4:] if len(momo_row[0]) >= 4 else momo_row[0]
                    brand = momo_row[1]
            elif pay_type == 'bank transfer':
                bank_query = "SELECT account_number, bank_name FROM bank_transfer WHERE payment_id = %s LIMIT 1"
                bank_row = run_query(bank_query, (pay_id,), fetch='one')
                if bank_row:
                    last_4 = bank_row[0][-4:] if len(bank_row[0]) >= 4 else bank_row[0]
                    brand = bank_row[1]
                    
            pay_dict = {
                "last_four": last_4,
                "brand": brand
            }
            
        # 5. Fetch order items (include is_dispatched for vendor fulfillment workflow)
        item_query = """
            SELECT oi.product_id, p.product_name, p.image_url, p.price, oi.quantity, oi.is_dispatched 
            FROM order_items oi 
            JOIN product p ON oi.product_id = p.product_id 
            WHERE oi.order_id = %s
        """
        item_rows = run_query(item_query, (order_id,), fetch='all')
        if not item_rows and cart_id:
            # Fallback to cart_items for seeded orders which don't have order_items entries
            cart_item_query = """
                SELECT ci.product_id, p.product_name, p.image_url, p.price, ci.quantity 
                FROM cart_items ci 
                JOIN product p ON ci.product_id = p.product_id 
                WHERE ci.cart_id = %s
            """
            item_rows = run_query(cart_item_query, (cart_id,), fetch='all')
            
        items = []
        for i_row in item_rows:
            item_dict = {
                "product_id": i_row[0],
                "name": i_row[1],
                "image": i_row[2],
                "price_at_purchase": float(i_row[3]),
                "quantity": i_row[4],
                "item_total": round(float(i_row[3]) * i_row[4], 2)
            }
            # map boolean is_dispatched to frontend item_status string
            if len(i_row) > 5:
                item_dict["item_status"] = "sent to port" if i_row[5] else "pending"
            else:
                item_dict["item_status"] = "sent to port"
            items.append(item_dict)
            
        grand_total = round(subtotal + shipping_fee, 2)
        
        orders.append({
            "order_id": order_id,
            "user_id": customer_id,
            "customer_id": customer_id,
            "created_at": order_date,
            "status": status,
            "delivery": delivery_obj,
            "pricing_summary": {
                "subtotal": subtotal,
                "shipping": shipping_fee,
                "grand_total": grand_total
            },
            "items": items,
            "shipping_address": addr_dict,
            "payment_details": pay_dict
        })
        
    return orders

def add_order(order_dict):
    order_id = order_dict["order_id"][:6]
    customer_id = order_dict["user_id"][:6]
    subtotal = order_dict["pricing_summary"]["subtotal"]
    shipping_fee = order_dict["pricing_summary"]["shipping"]
    
    # Resolve cart_id
    cart_query = "SELECT cart_id FROM cart WHERE customer_id = %s LIMIT 1"
    cart_row = run_query(cart_query, (customer_id,), fetch='one')
    cart_id = cart_row[0] if cart_row else "CRT" + customer_id[:3]
    
    conn = connect()
    cursor = conn.cursor()
    try:
        # Insert into orders
        cursor.execute(
            "INSERT INTO orders (order_id, customer_id, cart_id, order_date, subtotal, shipping_fee) VALUES (%s, %s, %s, NOW(), %s, %s)",
            (order_id, customer_id, cart_id, subtotal, shipping_fee)
        )
        
        # Insert into order_items
        for item in order_dict.get("items", []):
            prod_id = item["product_id"][:6]
            qty = item["quantity"]
            cursor.execute(
                "INSERT INTO order_items (product_id, order_id, quantity, added_date) VALUES (%s, %s, %s, CURRENT_DATE)",
                (prod_id, order_id, qty)
            )
            
        # Log payment details if provided
        pay_details = order_dict.get("payment_details")
        if pay_details:
            pay_id = str(uuid.uuid4())[:6]
            pay_type = "card"
            brand = pay_details.get("brand", "Card").lower()
            if brand in ["mtn", "telecel", "at", "momo"]:
                pay_type = "mobile money"
            elif "bank" in brand:
                pay_type = "bank transfer"
                
            cursor.execute(
                "INSERT INTO payment (payment_id, customer_id, amount, payment_date, payment_type, order_id) VALUES (%s, %s, %s, CURRENT_DATE, %s, %s)",
                (pay_id, customer_id, subtotal + shipping_fee, pay_type, order_id)
            )
            
            # Subtypes
            if pay_type == "card":
                card_name = pay_details.get("card_name", "Customer Card")
                expiry_str = pay_details.get("expiry")
                if expiry_str:
                    expiry_date = expiry_str + "-01" # Convert YYYY-MM to YYYY-MM-DD
                    cursor.execute(
                        "INSERT INTO card (payment_id, token_id, card_num, card_name, Expiry_date) VALUES (%s, %s, %s, %s, %s)",
                        (pay_id, "001", "4111XXXX" + pay_details.get("last_four", "1234"), card_name, expiry_date)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO card (payment_id, token_id, card_num, card_name, Expiry_date) VALUES (%s, %s, %s, %s, DATE_ADD(CURRENT_DATE, INTERVAL 3 YEAR))",
                        (pay_id, "001", "4111XXXX" + pay_details.get("last_four", "1234"), card_name)
                    )
            elif pay_type == "mobile money":
                phone = pay_details.get("phone_number") or ("024" + pay_details.get("last_four", "1234567"))
                cursor.execute(
                    "INSERT INTO mobile_money (payment_id, network, phone_number, account_name) VALUES (%s, %s, %s, %s)",
                    (pay_id, pay_details.get("brand", "MTN"), phone, "Momo Wallet")
                )
            elif pay_type == "bank transfer":
                account = pay_details.get("account_number") or ("100" + pay_details.get("last_four", "1234"))
                cursor.execute(
                    "INSERT INTO bank_transfer (payment_id, bank_name, account_number, account_name) VALUES (%s, %s, %s, %s)",
                    (pay_id, pay_details.get("brand", "Ecobank"), account, "Bank Transfer")
                )
                
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def add_address(address_dict):
    address_id = address_dict["address_id"][:6]
    city = address_dict["city"]
    landmark = address_dict.get("landmark") or address_dict.get("country", "")
    street_address = address_dict.get("street_address") or address_dict.get("street", "")
    customer_id = address_dict["customer_id"][:6]
    
    query = "INSERT INTO address (address_id, city, Landmark, street_address, customer_id) VALUES (%s, %s, %s, %s, %s)"
    run_query(query, (address_id, city, landmark, street_address, customer_id), commit=True)
    return address_dict

def get_addresses_by_customer(customer_id):
    query = "SELECT address_id, city, Landmark, street_address, customer_id FROM address WHERE customer_id = %s"
    rows = run_query(query, (customer_id[:6],), fetch='all')
    addresses = []
    for row in rows:
        addresses.append({
            "address_id": row[0],
            "city": row[1],
            "street": row[3],
            "street_address": row[3],
            "country": row[2],
            "landmark": row[2],
            "customer_id": row[4]
        })
    return addresses

def delete_address(address_id, customer_id):
    """Delete an address belonging to a specific customer."""
    query = "DELETE FROM address WHERE address_id = %s AND customer_id = %s"
    rows_affected = run_query(query, (address_id[:6], customer_id[:6]), commit=True)
    return rows_affected is not None and rows_affected > 0

def add_delivery(delivery_dict):
    delivery_id = delivery_dict["delivery_id"][:6]
    order_id = delivery_dict["order_id"][:6]
    status = delivery_dict["delivery_status"]
    est_date = delivery_dict["estimated_delivery_date"]
    address_id = delivery_dict["address_id"][:6] if delivery_dict.get("address_id") else None
    shipping_id = delivery_dict["shipping_id"][:6] if delivery_dict.get("shipping_id") else None
    
    query = """
        INSERT INTO delivery (delivery_id, order_id, delivery_status, estimated_delivery_date, address_id, shipping_id) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    run_query(query, (delivery_id, order_id, status, est_date, address_id, shipping_id), commit=True)
    return delivery_dict

def get_delivery_by_order(order_id):
    query = """
        SELECT delivery_id, order_id, delivery_status, estimated_delivery_date, address_id, shipping_id 
        FROM delivery 
        WHERE order_id = %s 
        LIMIT 1
    """
    row = run_query(query, (order_id[:6],), fetch='one')
    if row:
        return {
            "delivery_id": row[0],
            "order_id": row[1],
            "delivery_status": row[2],
            "estimated_delivery_date": str(row[3]),
            "address_id": row[4],
            "shipping_id": row[5]
        }
    return None

def get_all_shipping_companies():
    query = "SELECT shipping_id, name, contact_phone FROM shipping_company"
    rows = run_query(query, fetch='all')
    companies = []
    for row in rows:
        companies.append({
            "shipping_id": row[0],
            "name": row[1],
            "contact_phone": row[2]
        })
    return companies
    
def update_order(order_id, updates_dict):
    # Status updates are synced with delivery status in SQL view, but update_order is used by courier order updates.
    if "status" in updates_dict:
        status_val = updates_dict["status"]
        # Match check constraint value: 'delivered', 'in port', 'on the way', 'pending'
        status_lower = status_val.lower()
        if status_lower == "shipped":
            db_status = "on the way"
        elif status_lower == "pending":
            db_status = "pending"
        elif status_lower in ["delivered", "in port", "on the way", "pending"]:
            db_status = status_lower
        else:
            db_status = "on the way"
            
        query = "UPDATE delivery SET delivery_status = %s WHERE order_id = %s"
        run_query(query, (db_status, order_id[:6]), commit=True)
        return True
    return False

def get_reviews_by_product(product_id):
    query = "SELECT review_id, product_id, customer_id, rating, review_date, comment FROM review WHERE product_id = %s"
    rows = run_query(query, (product_id[:6],), fetch='all')
    reviews = []
    for row in rows:
        reviews.append({
            "review_id": row[0],
            "product_id": row[1],
            "customer_id": row[2],
            "rating": row[3],
            "review_date": str(row[4]),
            "comment": row[5]
        })
    return reviews

def add_review(review_dict):
    review_id = review_dict["review_id"][:6]
    product_id = review_dict["product_id"][:6]
    customer_id = review_dict["customer_id"][:6]
    rating = review_dict["rating"]
    comment = review_dict["comment"]
    
    query = "INSERT INTO review (review_id, product_id, customer_id, rating, review_date, comment) VALUES (%s, %s, %s, %s, NOW(), %s)"
    run_query(query, (review_id, product_id, customer_id, rating, comment), commit=True)

def findproduct(productid):
    query = """
        SELECT product_id, vendor_id, product_name, price, image_url, product_type, description, stock_quantity
        FROM product 
        WHERE product_id = %s
    """
    row = run_query(query, (productid.strip()[:6],), fetch='one')
    if row:
        return (
            row[0],  # product_id
            row[1],  # vendor_id
            row[2],  # product_name
            float(row[3]),  # price
            row[4],  # image_url
            row[5],  # product_type
            row[6],  # description
            row[7],  # stock_quantity
        )
    return None

def find_fashion_attributes(product_id):
    query = "SELECT Color, Material, Size, Gender_category FROM fashion WHERE product_id = %s"
    row = run_query(query, (product_id[:6],), fetch='one')
    if row:
        return {
            "Color": row[0],
            "Material": row[1],
            "Size": row[2],
            "Gender_category": row[3]
        }
    return None

def find_beauty_attributes(product_id):
    query = "SELECT skin_type, volume_weight, Is_organic FROM beauty WHERE product_id = %s"
    row = run_query(query, (product_id[:6],), fetch='one')
    if row:
        return {
            "skin_type": row[0],
            "volume_weight": row[1],
            "Is_organic": bool(row[2])
        }
    return None

def addproduct(product_dict):
    product_id = product_dict["product_id"][:6]
    vendor_id = product_dict["vendor_id"][:6]
    product_name = product_dict["product_name"]
    description = product_dict["description"]
    price = product_dict["price"]
    stock_quantity = product_dict["stock_quantity"]
    product_type = product_dict["product_type"]
    image_url = product_dict["image_url"]
    
    query = """
        INSERT INTO product (product_id, vendor_id, product_name, description, price, stock_quantity, product_type, image_url) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    run_query(query, (product_id, vendor_id, product_name, description, price, stock_quantity, product_type, image_url), commit=True)

def add_fashion(fashion_dict):
    product_id = fashion_dict["product_id"][:6]
    color = fashion_dict["color"]
    material = fashion_dict["material"]
    size = fashion_dict["size"]
    gender_category = fashion_dict["gender_category"].lower()
    
    if gender_category not in ['men', 'women', 'unisex', 'kids']:
        gender_category = 'unisex'
        
    query = """
        INSERT INTO fashion (product_id, Color, Material, Size, Gender_category) 
        VALUES (%s, %s, %s, %s, %s)
    """
    run_query(query, (product_id, color, material, size, gender_category), commit=True)

def add_beauty(beauty_dict):
    product_id = beauty_dict["product_id"][:6]
    skin_type = beauty_dict["skin_type"]
    volume_weight = beauty_dict["volume_weight"]
    is_organic = beauty_dict["Is_organic"]
    
    query = """
        INSERT INTO beauty (product_id, skin_type, volume_weight, Is_organic) 
        VALUES (%s, %s, %s, %s)
    """
    run_query(query, (product_id, skin_type, volume_weight, is_organic), commit=True)

def updateproduct(productid, updates_dict):
    if not updates_dict:
        return False
        
    parts = []
    params = []
    for k, v in updates_dict.items():
        parts.append(f"{k} = %s")
        params.append(v)
        
    query = f"UPDATE product SET {', '.join(parts)} WHERE product_id = %s"
    params.append(productid[:6])
    
    run_query(query, tuple(params), commit=True)
    return True

def update_fashion(productid, updates_dict):
    if not updates_dict:
        return False
        
    parts = []
    params = []
    for k, v in updates_dict.items():
        parts.append(f"{k} = %s")
        params.append(v)
        
    query = f"UPDATE fashion SET {', '.join(parts)} WHERE product_id = %s"
    params.append(productid[:6])
    
    run_query(query, tuple(params), commit=True)
    return True

def update_beauty(productid, updates_dict):
    if not updates_dict:
        return False
        
    parts = []
    params = []
    for k, v in updates_dict.items():
        parts.append(f"{k} = %s")
        params.append(v)
        
    query = f"UPDATE beauty SET {', '.join(parts)} WHERE product_id = %s"
    params.append(productid[:6])
    
    run_query(query, tuple(params), commit=True)
    return True

def deleteproduct(productid):
    query = "UPDATE product SET is_active = FALSE WHERE product_id = %s"
    run_query(query, (productid[:6],), commit=True)
    return True

def viewtopproducs(limit=5):
    """Retrieve top selling products by units sold and revenue."""
    query = """
        SELECT p.product_id, p.product_name, COALESCE(SUM(oi.quantity), 0) AS total_units_sold, COALESCE(SUM(oi.quantity * p.price), 0) AS total_revenue
        FROM product p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_units_sold DESC
        LIMIT %s
    """
    rows = run_query(query, (limit,), fetch='all')
    products = []
    for r in rows:
        products.append({
            "product_id": r[0],
            "product_name": r[1],
            "units_sold": int(r[2]),
            "revenue": float(r[3])
        })
    return products

def viewhighestspender(limit=5):
    """Retrieve top spending customers by total order amount."""
    query = """
        SELECT c.customer_id, c.f_name, c.l_name, c.email, SUM(o.subtotal + o.shipping_fee) AS total_spent, COUNT(o.order_id) AS total_orders
        FROM customer c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.f_name, c.l_name, c.email
        ORDER BY total_spent DESC
        LIMIT %s
    """
    rows = run_query(query, (limit,), fetch='all')
    spenders = []
    for r in rows:
        spenders.append({
            "customer_id": r[0],
            "customer_name": f"{r[1]} {r[2]}".strip(),
            "email": r[3],
            "total_spent": float(r[4]),
            "total_orders": int(r[5])
        })
    return spenders

def highestrevenue_vendors():
    """Retrieve vendor revenue rankings and units sold."""
    query = """
        SELECT v.vendor_id, v.vendor_name, COALESCE(SUM(oi.quantity * p.price), 0) AS total_revenue, COALESCE(SUM(oi.quantity), 0) AS units_sold
        FROM vendor v
        JOIN product p ON v.vendor_id = p.vendor_id
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY v.vendor_id, v.vendor_name
        ORDER BY total_revenue DESC
    """
    rows = run_query(query, fetch='all')
    vendors = []
    for r in rows:
        vendors.append({
            "vendor_id": r[0],
            "vendor_name": r[1],
            "total_revenue": float(r[2]),
            "units_sold": int(r[3])
        })
    return vendors

def top_popular_products_categories():
    """Retrieve sales breakdown by product categories."""
    query = """
        WITH ProductCategories AS (
            SELECT product_id, 'Fashion' AS category FROM fashion
            UNION ALL
            SELECT product_id, 'Beauty' AS category FROM beauty
        )
        SELECT pc.category, COALESCE(SUM(oi.quantity), 0) AS units_sold, COALESCE(SUM(oi.quantity * p.price), 0) AS total_revenue
        FROM ProductCategories pc
        JOIN product p ON pc.product_id = p.product_id
        JOIN order_items oi ON pc.product_id = oi.product_id
        GROUP BY pc.category
        ORDER BY units_sold DESC
    """
    rows = run_query(query, fetch='all')
    categories = []
    for r in rows:
        categories.append({
            "category": r[0],
            "units_sold": int(r[1]),
            "revenue": float(r[2])
        })
    return categories

def addtocart(product, customer_id, quantity):
    if hasattr(product, 'product_id'):
        product_id = product.product_id
    else:
        product_id = product[0]
        
    customer_id = customer_id[:6]
    product_id = product_id[:6]
    
    # Make sure Cart exists for user
    cart_query = "SELECT cart_id FROM cart WHERE customer_id = %s LIMIT 1"
    cart_row = run_query(cart_query, (customer_id,), fetch='one')
    if not cart_row:
        cart_id = "CRT" + customer_id[:3]
        run_query("INSERT IGNORE INTO cart (cart_id, customer_id) VALUES (%s, %s)", (cart_id, customer_id), commit=True)
        
    # Call stored procedure
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("CALL sp_add_to_cart(%s, %s, %s)", (customer_id, product_id, quantity))
        conn.commit()
        return True
    except Exception as e:
        print("CALL sp_add_to_cart failed, falling back to manual INSERT. Error:", e)
        # Fallback to manual insert if stored procedure fails for some reason
        conn.rollback()
        
        # Get cart_id again
        cursor.execute("SELECT cart_id FROM cart WHERE customer_id = %s LIMIT 1", (customer_id,))
        c_row = cursor.fetchone()
        if c_row:
            cart_id = c_row[0]
            cursor.execute(
                "INSERT INTO cart_items (product_id, cart_id, quantity, added_date) VALUES (%s, %s, %s, CURRENT_DATE) ON DUPLICATE KEY UPDATE quantity = quantity + %s",
                (product_id, cart_id, quantity, quantity)
            )
            conn.commit()
            return True
        return False
    finally:
        cursor.close()
        conn.close()

def getcart(customer_id):
    query = """
        SELECT ci.product_id, ci.quantity, p.product_name, p.vendor_id, p.price, p.image_url, p.product_type, p.description 
        FROM cart_items ci 
        JOIN cart c ON ci.cart_id = c.cart_id 
        JOIN product p ON ci.product_id = p.product_id 
        WHERE c.customer_id = %s
    """
    rows = run_query(query, (customer_id[:6],), fetch='all')
    items = []
    for row in rows:
        product_obj = Product(
            product_id=row[0],
            vendor_id=row[3],
            product_name=row[2],
            price=float(row[4]),
            image_url=row[5],
            product_type=row[6],
            description=row[7]
        )
        items.append({"product": product_obj, "quantity": row[1]})
    return items

def removefromcart(product_id, customer_id):
    query = """
        DELETE ci FROM cart_items ci 
        JOIN cart c ON ci.cart_id = c.cart_id 
        WHERE ci.product_id = %s AND c.customer_id = %s
    """
    rowcount = run_query(query, (product_id[:6], customer_id[:6]), commit=True)
    return rowcount > 0

def checkout(customer_id):
    query = """
        DELETE ci FROM cart_items ci 
        JOIN cart c ON ci.cart_id = c.cart_id 
        WHERE c.customer_id = %s
    """
    run_query(query, (customer_id[:6],), commit=True)
    return True

def update_customer(customer_id, updates_dict):
    if not updates_dict:
        return False
    parts = []
    params = []
    for k, v in updates_dict.items():
        parts.append(f"{k} = %s")
        params.append(v)
    query = f"UPDATE customer SET {', '.join(parts)} WHERE customer_id = %s"
    params.append(customer_id[:6])
    run_query(query, tuple(params), commit=True)
    return True

def get_deliveries_by_shipping_company(shipping_id):
    query = """
        SELECT 
            d.delivery_id, 
            CONCAT(c.f_name, ' ', c.l_name),
            c.phone_number,
            a.city,
            a.street_address,
            a.Landmark,
            d.estimated_delivery_date,
            d.delivery_status,
            COALESCE(o.shipping_fee, 0),
            d.order_id
        FROM delivery d
        LEFT JOIN orders o ON d.order_id = o.order_id
        LEFT JOIN customer c ON o.customer_id = c.customer_id
        LEFT JOIN address a ON d.address_id = a.address_id
        WHERE d.shipping_id = %s
    """
    rows = run_query(query, (shipping_id[:6],), fetch='all')
    deliveries = []
    total_earnings = 0.0
    completed_earnings = 0.0
    for r in rows:
        fee = float(r[8])
        total_earnings += fee
        if r[7] == 'delivered':
            completed_earnings += fee
            
        # Fetch items for this delivery package
        items_query = """
            SELECT oi.product_id, p.product_name, v.vendor_name, oi.quantity, oi.is_dispatched
            FROM order_items oi
            JOIN product p ON oi.product_id = p.product_id
            JOIN vendor v ON p.vendor_id = v.vendor_id
            WHERE oi.order_id = %s
        """
        item_rows = run_query(items_query, (r[9],), fetch='all')
        items = []
        for ir in item_rows:
            items.append({
                "product_id": ir[0],
                "product_name": ir[1],
                "vendor_name": ir[2],
                "quantity": ir[3],
                "is_dispatched": bool(ir[4])
            })
            
        deliveries.append({
            "id": r[0],
            "customer": r[1] or "Unknown Customer",
            "phone": r[2] or "N/A",
            "city": r[3] or "N/A",
            "street": r[4] or "N/A",
            "landmark": r[5] or "N/A",
            "estDate": str(r[6]) if r[6] else "TBD",
            "status": "sent to port" if r[7] == "in port" else r[7],
            "shipping_fee": fee,
            "items": items
        })
    return {
        "deliveries": deliveries,
        "total_earnings": round(total_earnings, 2),
        "completed_earnings": round(completed_earnings, 2)
    }

def get_admin_stats():
    # Sum subtotal of all orders
    rev_row = run_query("SELECT SUM(subtotal) FROM orders", fetch='one')
    total_revenue = float(rev_row[0]) if rev_row and rev_row[0] is not None else 0.0
    
    # Total customers
    cust_row = run_query("SELECT COUNT(*) FROM customer", fetch='one')
    total_cust = cust_row[0] if cust_row else 0
    
    # Total vendors
    vend_row = run_query("SELECT COUNT(*) FROM vendor", fetch='one')
    total_vend = vend_row[0] if vend_row else 0
    
    # Total orders
    order_row = run_query("SELECT COUNT(*) FROM orders", fetch='one')
    total_orders = order_row[0] if order_row else 0
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_users": total_cust + total_vend,
        "total_orders": total_orders
    }

def get_admin_users():
    users = []
    cust_rows = run_query("SELECT customer_id, f_name, l_name, email, is_active FROM customer", fetch='all')
    for r in cust_rows:
        users.append({"id": r[0], "name": f"{r[1]} {r[2]}".strip(), "email": r[3], "role": "customer", "is_active": bool(r[4])})
    vend_rows = run_query("SELECT vendor_id, vendor_name, email, is_active FROM vendor", fetch='all')
    for r in vend_rows:
        users.append({"id": r[0], "name": r[1], "email": r[2], "role": "vendor", "is_active": bool(r[3])})
    return users

def update_delivery_status(delivery_id, new_status):
    # Check if delivery exists first (rowcount=0 for same-value updates in MariaDB)
    exists = run_query("SELECT delivery_id FROM delivery WHERE delivery_id = %s", (delivery_id[:6],), fetch='one')
    if not exists:
        return False
    run_query("UPDATE delivery SET delivery_status = %s WHERE delivery_id = %s", (new_status, delivery_id[:6]), commit=True)
    return True

def update_address(address_id, updates_dict):
    if not updates_dict:
        return False
    parts = []
    params = []
    for k, v in updates_dict.items():
        parts.append(f"{k} = %s")
        params.append(v)
    query = f"UPDATE address SET {', '.join(parts)} WHERE address_id = %s"
    params.append(address_id[:6])
    run_query(query, tuple(params), commit=True)
    return True

def get_vendor_product_analytics(vendor_id):
    query = """
        SELECT
            p.product_id,
            p.product_name,
            COALESCE(s.units_sold, 0) as units_sold,
            COALESCE(s.total_revenue, 0) as total_revenue,
            COALESCE(r.average_rating, 0) as average_rating
        FROM Product p
        LEFT JOIN vw_product_sales s ON p.product_id = s.product_id
        LEFT JOIN vw_product_ratings r ON p.product_id = r.product_id
        WHERE p.vendor_id = %s
        ORDER BY units_sold DESC
    """
    rows = run_query(query, (vendor_id[:6],), fetch='all')
    analytics = []
    for r in rows:
        analytics.append({
            "product_id": r[0],
            "product_name": r[1],
            "units_sold": int(r[2]),
            "revenue": float(r[3]),
            "average_rating": float(r[4])
        })
    return analytics

def get_vendor_dashboard_stats(vendor_id):
    # Total sales from vw_vendor_sales
    query_sales = "SELECT total_revenue FROM vw_vendor_sales WHERE vendor_id = %s"
    sales_row = run_query(query_sales, (vendor_id[:6],), fetch='one')
    total_sales = float(sales_row[0]) if sales_row else 0.0
    
    # Active products from product table
    query_products = "SELECT COUNT(*) FROM product WHERE vendor_id = %s"
    prod_row = run_query(query_products, (vendor_id[:6],), fetch='one')
    active_products = int(prod_row[0]) if prod_row else 0
    
    # Pending orders from delivery table (left join since seeded orders might not have delivery records)
    query_orders = """
        SELECT COUNT(DISTINCT o.order_id) 
        FROM orders o 
        LEFT JOIN delivery d ON o.order_id = d.order_id 
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN product p ON oi.product_id = p.product_id
        WHERE p.vendor_id = %s AND (d.delivery_status IS NULL OR d.delivery_status != 'delivered')
    """
    ord_row = run_query(query_orders, (vendor_id[:6],), fetch='one')
    pending_orders = int(ord_row[0]) if ord_row else 0
    
    return {
        "total_sales": total_sales,
        "active_products": active_products,
        "pending_orders": pending_orders
    }

def searchshipping(email_or_id):
    query = """
        SELECT s.shipping_id, s.name, s.email, s.contact_phone, sc.password_hash
        FROM shipping_company s
        JOIN shipping_credentials sc ON s.shipping_id = sc.shipping_id
        WHERE LOWER(s.email) = LOWER(%s) OR s.shipping_id = %s
    """
    row = run_query(query, (email_or_id.strip(), email_or_id.strip()[:6]), fetch='one')
    if row:
        return {
            "shipping_id": row[0],
            "name": row[1],
            "email": row[2],
            "contact_phone": row[3],
            "password_hash": row[4]
        }
    return None

def get_all_shipping_companies():
    query = """
        SELECT 
            sc.shipping_id, 
            sc.name, 
            sc.email, 
            sc.contact_phone,
            COUNT(d.delivery_id) AS total_deliveries,
            COALESCE(SUM(o.shipping_fee), 0) AS total_revenue,
            COUNT(CASE WHEN d.delivery_status = 'delivered' THEN 1 END) AS completed_deliveries
        FROM shipping_company sc
        LEFT JOIN delivery d ON sc.shipping_id = d.shipping_id
        LEFT JOIN orders o ON d.order_id = o.order_id
        GROUP BY sc.shipping_id, sc.name, sc.email, sc.contact_phone
        ORDER BY total_revenue DESC
    """
    rows = run_query(query, fetch='all')
    carriers = []
    for r in rows:
        carriers.append({
            "shipping_id": r[0],
            "name": r[1],
            "email": r[2],
            "contact_phone": r[3],
            "total_deliveries": int(r[4]),
            "total_revenue": float(r[5]),
            "completed_deliveries": int(r[6])
        })
    return carriers

def register_shipping_company(name, email, phone_number, password_hash, shipping_id=None):
    if not shipping_id:
        shipping_id = ("SH" + str(uuid.uuid4()).replace("-", "").upper())[:6]
    else:
        shipping_id = shipping_id[:6]
        
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO shipping_company (shipping_id, name, email, contact_phone) VALUES (%s, %s, %s, %s)",
            (shipping_id, name, email.strip(), phone_number or "")
        )
        cursor.execute(
            "INSERT INTO shipping_credentials (shipping_id, password_hash) VALUES (%s, %s)",
            (shipping_id, password_hash)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
        
    return {
        "shipping_id": shipping_id,
        "name": name,
        "email": email,
        "contact_phone": phone_number or ""
    }

def update_order_item_status(order_id, product_id, new_status):
    """Update the is_dispatched flag for a specific item in an order (vendor fulfillment)."""
    # Verify the order_item exists
    exists = run_query(
        "SELECT product_id FROM order_items WHERE order_id = %s AND product_id = %s",
        (order_id[:6], product_id[:6]), fetch='one'
    )
    if not exists:
        return False
    is_disp = 1 if new_status == "sent to port" else 0
    run_query(
        "UPDATE order_items SET is_dispatched = %s WHERE order_id = %s AND product_id = %s",
        (is_disp, order_id[:6], product_id[:6]), commit=True
    )
    return True

