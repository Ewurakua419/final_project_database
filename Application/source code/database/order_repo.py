import uuid
from model.product import Product
from database.connection import connect, run_query

def get_all_orders():
    query = """
        SELECT o.order_id, o.customer_id, c.cart_id, o.order_date, o.subtotal, o.shipping_fee 
        FROM orders o
        JOIN cart c ON o.customer_id = c.customer_id
    """
    order_rows = run_query(query, fetch='all')
    
    orders = []
    for o_row in order_rows:
        order_id = o_row[0]
        customer_id = o_row[1]
        cart_id = o_row[2]
        order_date = o_row[3].isoformat() if hasattr(o_row[3], 'isoformat') else str(o_row[3])
        subtotal = float(o_row[4])
        shipping_fee = float(o_row[5])
        
        # Fetch delivery status and details
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
            
        # Fetch address
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
                
        # Fetch payment details
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
            
        # Fetch order items
        item_query = """
            SELECT oi.product_id, p.product_name, p.image_url, p.price, oi.quantity, oi.is_dispatched 
            FROM order_items oi 
            JOIN product p ON oi.product_id = p.product_id 
            WHERE oi.order_id = %s
        """
        item_rows = run_query(item_query, (order_id,), fetch='all')
        if not item_rows and cart_id:
            # Fallback to cart_items for seeded orders
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

def add_order(order_dict, delivery_dict=None):
    """原子化下单：调用 stored procedure sp_place_order, 并保存支付和派送记录。"""
    order_id = order_dict["order_id"]
    customer_id = order_dict["user_id"]
    subtotal = order_dict["pricing_summary"]["subtotal"]
    shipping_fee = order_dict["pricing_summary"]["shipping"]
    
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("CALL sp_place_order(%s, %s)", (order_id, customer_id))
        
        pay_details = order_dict.get("payment_details")
        if pay_details:
            pay_id = str(uuid.uuid4())
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
            
            if pay_type == "card":
                card_name = pay_details.get("card_name", "Customer Card")
                expiry_str = pay_details.get("expiry")
                if expiry_str:
                    expiry_date = expiry_str + "-01"
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
                
        if delivery_dict:
            delivery_id = delivery_dict["delivery_id"]
            status = delivery_dict["delivery_status"]
            est_date = delivery_dict["estimated_delivery_date"]
            address_id = delivery_dict.get("address_id")
            shipping_id = delivery_dict.get("shipping_id")
            
            cursor.execute(
                """
                INSERT INTO delivery (delivery_id, order_id, delivery_status, estimated_delivery_date, address_id, shipping_id) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (delivery_id, order_id, status, est_date, address_id, shipping_id)
            )
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def add_delivery(delivery_dict):
    delivery_id = delivery_dict["delivery_id"]
    order_id = delivery_dict["order_id"]
    status = delivery_dict["delivery_status"]
    est_date = delivery_dict["estimated_delivery_date"]
    address_id = delivery_dict["address_id"] if delivery_dict.get("address_id") else None
    shipping_id = delivery_dict["shipping_id"] if delivery_dict.get("shipping_id") else None
    
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
    row = run_query(query, (order_id,), fetch='one')
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

def update_order(order_id, updates_dict):
    if "status" in updates_dict:
        status_val = updates_dict["status"]
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
        run_query(query, (db_status, order_id), commit=True)
        return True
    return False

def addtocart(product, customer_id, quantity):
    if hasattr(product, 'product_id'):
        product_id = product.product_id
    else:
        product_id = product[0]
        
    cart_query = "SELECT cart_id FROM cart WHERE customer_id = %s LIMIT 1"
    cart_row = run_query(cart_query, (customer_id,), fetch='one')
    if not cart_row:
        cart_id = "CRT" + customer_id[:3]
        run_query("INSERT IGNORE INTO cart (cart_id, customer_id) VALUES (%s, %s)", (cart_id, customer_id), commit=True)
        
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("CALL sp_add_to_cart(%s, %s, %s)", (customer_id, product_id, quantity))
        conn.commit()
        return True
    except Exception as e:
        print("CALL sp_add_to_cart failed, falling back to manual INSERT. Error:", e)
        conn.rollback()
        
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
    rows = run_query(query, (customer_id,), fetch='all')
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
    rowcount = run_query(query, (product_id, customer_id), commit=True)
    return rowcount > 0

def checkout(customer_id):
    query = """
        DELETE ci FROM cart_items ci 
        JOIN cart c ON ci.cart_id = c.cart_id 
        WHERE c.customer_id = %s
    """
    run_query(query, (customer_id,), commit=True)
    return True

def update_cart_qty(product_id, customer_id, quantity):
    """Directly updates a cart item quantity, triggering BEFORE UPDATE database stock checks."""
    query = """
        UPDATE cart_items ci
        JOIN cart c ON ci.cart_id = c.cart_id
        SET ci.quantity = %s
        WHERE ci.product_id = %s AND c.customer_id = %s
    """
    run_query(query, (quantity, product_id, customer_id), commit=True)
    return True
