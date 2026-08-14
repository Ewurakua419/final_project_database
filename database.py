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
        SELECT c.customer_id, c.f_name, c.l_name, c.phone_number, c.email, cc.password_hash 
        FROM customer c 
        JOIN customer_credentials cc ON c.customer_id = cc.customer_id 
        WHERE LOWER(c.email) = LOWER(%s)
    """
    row = run_query(query, (email.strip(),), fetch='one')
    if row:
        return (row[0], row[1], row[2], row[3], row[4], row[5])
    return None

def searchcustomer_by_id(customer_id):
    query = """
        SELECT c.customer_id, c.f_name, c.l_name, c.phone_number, c.email, cc.password_hash 
        FROM customer c 
        JOIN customer_credentials cc ON c.customer_id = cc.customer_id 
        WHERE c.customer_id = %s
    """
    row = run_query(query, (customer_id[:6],), fetch='one')
    if row:
        return (row[0], row[1], row[2], row[3], row[4], row[5])
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
        SELECT v.vendor_id, v.vendor_name, v.email, v.phone_number, vc.password_hash 
        FROM vendor v 
        JOIN vendor_credentials vc ON v.vendor_id = vc.vendor_id 
        WHERE LOWER(v.email) = LOWER(%s)
    """
    row = run_query(query, (email.strip(),), fetch='one')
    if row:
        return (row[0], row[1], row[2], row[3], row[4])
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
        del_query = "SELECT delivery_status, address_id, shipping_id FROM delivery WHERE order_id = %s LIMIT 1"
        del_row = run_query(del_query, (order_id,), fetch='one')
        status = "pending"
        address_id = None
        if del_row:
            status = del_row[0]
            address_id = del_row[1]
            
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
            
        # 5. Fetch order items
        item_query = """
            SELECT oi.product_id, p.product_name, p.image_url, p.price, oi.quantity 
            FROM order_items oi 
            JOIN product p ON oi.product_id = p.product_id 
            WHERE oi.order_id = %s
        """
        item_rows = run_query(item_query, (order_id,), fetch='all')
        items = []
        for i_row in item_rows:
            items.append({
                "product_id": i_row[0],
                "name": i_row[1],
                "image": i_row[2],
                "price_at_purchase": float(i_row[3]),
                "quantity": i_row[4],
                "item_total": round(float(i_row[3]) * i_row[4], 2)
            })
            
        tax = round(subtotal * 0.08, 2)
        grand_total = round(subtotal + tax + shipping_fee, 2)
        
        orders.append({
            "order_id": order_id,
            "user_id": customer_id,
            "customer_id": customer_id,
            "created_at": order_date,
            "status": status,
            "pricing_summary": {
                "subtotal": subtotal,
                "tax": tax,
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
                cursor.execute(
                    "INSERT INTO card (payment_id, token_id, card_num, card_name, Expiry_date) VALUES (%s, %s, %s, %s, DATE_ADD(CURRENT_DATE, INTERVAL 3 YEAR))",
                    (pay_id, "001", "4111XXXX" + pay_details.get("last_four", "1234"), "Customer Card")
                )
            elif pay_type == "mobile money":
                cursor.execute(
                    "INSERT INTO mobile_money (payment_id, network, phone_number, account_name) VALUES (%s, %s, %s, %s)",
                    (pay_id, pay_details.get("brand", "MTN"), "024" + pay_details.get("last_four", "1234567"), "Momo Wallet")
                )
            elif pay_type == "bank transfer":
                cursor.execute(
                    "INSERT INTO bank_transfer (payment_id, bank_name, account_number, account_name) VALUES (%s, %s, %s, %s)",
                    (pay_id, pay_details.get("brand", "Ecobank"), "100" + pay_details.get("last_four", "1234"), "Bank Transfer")
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
    # Status updates are synced with delivery status in SQL view, but update_order is used by vendor order updates.
    if "status" in updates_dict:
        status_val = updates_dict["status"]
        # Match check constraint value: 'delivered', 'sent to port', 'on the way'
        status_lower = status_val.lower()
        if status_lower == "shipped":
            db_status = "on the way"
        elif status_lower == "pending":
            db_status = "sent to port"
        elif status_lower in ["delivered", "sent to port", "on the way"]:
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
        SELECT product_id, vendor_id, product_name, price, image_url, product_type, description 
        FROM product 
        WHERE product_id = %s
    """
    row = run_query(query, (productid.strip()[:6],), fetch='one')
    if row:
        return (
            row[0],
            row[1],
            row[2],
            float(row[3]),
            row[4],
            row[5],
            row[6]
        )
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
    query = "DELETE FROM product WHERE product_id = %s"
    run_query(query, (productid[:6],), commit=True)
    return True

def viewtopproducs():
    pass

def viewhighestspender():
    pass

def highestrevenue_vendors():
    pass

def top_popular_products_categories():
    pass

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
    query = "SELECT delivery_id, delivery_status FROM delivery WHERE shipping_id = %s"
    rows = run_query(query, (shipping_id[:6],), fetch='all')
    return [{"delivery_id": r[0], "delivery_status": r[1]} for r in rows]

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
    cust_rows = run_query("SELECT customer_id, f_name, l_name, email FROM customer", fetch='all')
    for r in cust_rows:
        users.append({"id": r[0], "name": f"{r[1]} {r[2]}".strip(), "email": r[3], "role": "customer"})
    vend_rows = run_query("SELECT vendor_id, vendor_name, email FROM vendor", fetch='all')
    for r in vend_rows:
        users.append({"id": r[0], "name": r[1], "email": r[2], "role": "vendor"})
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

