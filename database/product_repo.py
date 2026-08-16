from database.connection import connect, run_query

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

def findproduct(productid):
    query = """
        SELECT product_id, vendor_id, product_name, price, image_url, product_type, description, stock_quantity
        FROM product 
        WHERE product_id = %s
    """
    row = run_query(query, (productid.strip(),), fetch='one')
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
    row = run_query(query, (product_id,), fetch='one')
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
    row = run_query(query, (product_id,), fetch='one')
    if row:
        return {
            "skin_type": row[0],
            "volume_weight": row[1],
            "Is_organic": bool(row[2])
        }
    return None

def addproduct(product_dict):
    product_id = product_dict["product_id"]
    vendor_id = product_dict["vendor_id"]
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
    product_id = fashion_dict["product_id"]
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
    product_id = beauty_dict["product_id"]
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
    params.append(productid)
    
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
    params.append(productid)
    
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
    params.append(productid)
    
    run_query(query, tuple(params), commit=True)
    return True

def deleteproduct(productid):
    query = "UPDATE product SET is_active = FALSE WHERE product_id = %s"
    run_query(query, (productid,), commit=True)
    return True

def get_reviews_by_product(product_id):
    query = "SELECT review_id, product_id, customer_id, rating, review_date, comment FROM review WHERE product_id = %s"
    rows = run_query(query, (product_id,), fetch='all')
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
    review_id = review_dict["review_id"]
    product_id = review_dict["product_id"]
    customer_id = review_dict["customer_id"]
    rating = review_dict["rating"]
    comment = review_dict["comment"]
    
    query = "INSERT INTO review (review_id, product_id, customer_id, rating, review_date, comment) VALUES (%s, %s, %s, %s, NOW(), %s)"
    run_query(query, (review_id, product_id, customer_id, rating, comment), commit=True)
