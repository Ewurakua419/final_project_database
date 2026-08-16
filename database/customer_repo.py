from database.connection import connect, run_query

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
    row = run_query(query, (customer_id,), fetch='one')
    if row:
        return (row[0], row[1], row[2], row[3], row[4], row[5], bool(row[6]))
    return None

def register(name, userid, cart_ids, balance, password, email, first_name=None, last_name=None, phone_number=None):
    cart_id = cart_ids if cart_ids else "CRT" + userid[:3]
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

def update_customer(customer_id, updates_dict):
    if not updates_dict:
        return False
    parts = []
    params = []
    for k, v in updates_dict.items():
        parts.append(f"{k} = %s")
        params.append(v)
    query = f"UPDATE customer SET {', '.join(parts)} WHERE customer_id = %s"
    params.append(customer_id)
    run_query(query, tuple(params), commit=True)
    return True

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

def add_address(address_dict):
    address_id = address_dict["address_id"]
    city = address_dict["city"]
    landmark = address_dict.get("landmark") or address_dict.get("country", "")
    street_address = address_dict.get("street_address") or address_dict.get("street", "")
    customer_id = address_dict["customer_id"]
    
    query = "INSERT INTO address (address_id, city, Landmark, street_address, customer_id) VALUES (%s, %s, %s, %s, %s)"
    run_query(query, (address_id, city, landmark, street_address, customer_id), commit=True)
    return address_dict

def get_addresses_by_customer(customer_id):
    query = "SELECT address_id, city, Landmark, street_address, customer_id FROM address WHERE customer_id = %s"
    rows = run_query(query, (customer_id,), fetch='all')
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
    query = "DELETE FROM address WHERE address_id = %s AND customer_id = %s"
    rows_affected = run_query(query, (address_id, customer_id), commit=True)
    return rows_affected is not None and rows_affected > 0

def update_address(address_id, updates_dict):
    if not updates_dict:
        return False
    parts = []
    params = []
    for k, v in updates_dict.items():
        parts.append(f"{k} = %s")
        params.append(v)
    query = f"UPDATE address SET {', '.join(parts)} WHERE address_id = %s"
    params.append(address_id)
    run_query(query, tuple(params), commit=True)
    return True
