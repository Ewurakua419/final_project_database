import uuid
from database.connection import connect, run_query

def searchshipping(email_or_id):
    query = """
        SELECT s.shipping_id, s.name, s.email, s.contact_phone, sc.password_hash
        FROM shipping_company s
        JOIN shipping_credentials sc ON s.shipping_id = sc.shipping_id
        WHERE LOWER(s.email) = LOWER(%s) OR s.shipping_id = %s
    """
    row = run_query(query, (email_or_id.strip(), email_or_id.strip()), fetch='one')
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
    """Queries performance statistics from vw_carrier_performance view."""
    query = """
        SELECT 
            sc.shipping_id, 
            sc.name, 
            sc.email, 
            sc.contact_phone,
            COALESCE(cp.total_deliveries, 0) AS total_deliveries,
            COALESCE(cp.total_shipping_revenue, 0) AS total_revenue,
            COALESCE(cp.completed_deliveries, 0) AS completed_deliveries
        FROM shipping_company sc
        LEFT JOIN vw_carrier_performance cp ON sc.shipping_id = cp.shipping_id
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
        shipping_id = ("SH" + str(uuid.uuid4()).replace("-", "").upper())
    else:
        shipping_id = shipping_id
        
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
    rows = run_query(query, (shipping_id,), fetch='all')
    deliveries = []
    total_earnings = 0.0
    completed_earnings = 0.0
    for r in rows:
        fee = float(r[8])
        total_earnings += fee
        if r[7] == 'delivered':
            completed_earnings += fee
            
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

def update_delivery_status(delivery_id, new_status):
    """Utilizes the database stored procedure sp_update_delivery_status directly."""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("CALL sp_update_delivery_status(%s, %s)", (delivery_id, new_status))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("CALL sp_update_delivery_status failed:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def update_order_item_status(order_id, product_id, new_status):
    """Utilizes the database stored procedure sp_update_order_item_status directly."""
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("CALL sp_update_order_item_status(%s, %s, %s)", (order_id, product_id, new_status))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("CALL sp_update_order_item_status failed:", e)
        return False
    finally:
        cursor.close()
        conn.close()
