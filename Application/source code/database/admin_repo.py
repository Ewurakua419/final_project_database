from database.connection import connect, run_query

def viewtopproducs(limit=5):
    """Utilizes the database view vw_product_sales for top selling products."""
    query = """
        SELECT product_id, product_name, units_sold, total_revenue
        FROM vw_product_sales
        ORDER BY units_sold DESC
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
    """Utilizes the database view vw_customer_order_history for top spenders."""
    query = """
        SELECT 
            coh.customer_id, 
            coh.f_name, 
            coh.l_name, 
            c.email, 
            SUM(coh.subtotal + coh.shipping_fee) AS total_spent, 
            COUNT(coh.order_id) AS total_orders
        FROM vw_customer_order_history coh
        JOIN customer c ON coh.customer_id = c.customer_id
        GROUP BY coh.customer_id, coh.f_name, coh.l_name, c.email
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
    """Utilizes the database view vw_vendor_sales for vendor revenues."""
    query = """
        SELECT vendor_id, vendor_name, total_revenue, units_sold
        FROM vw_vendor_sales
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

def get_admin_stats():
    """Utilizes the single-query view vw_admin_platform_summary instead of 4 sequential queries."""
    row = run_query("SELECT total_gmv, total_orders, total_customers, total_vendors FROM vw_admin_platform_summary", fetch='one')
    if row:
        return {
            "total_revenue": float(row[0]),
            "total_orders": int(row[1]),
            "total_users": int(row[2]) + int(row[3])
        }
    return {
        "total_revenue": 0.0,
        "total_users": 0,
        "total_orders": 0
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

def get_vendor_product_analytics(vendor_id):
    """Utilizes the database view vw_vendor_product_performance instead of manual multi-table joins."""
    query = """
        SELECT product_id, product_name, units_sold, total_revenue, average_rating
        FROM vw_vendor_product_performance
        WHERE vendor_id = %s
        ORDER BY units_sold DESC
    """
    rows = run_query(query, (vendor_id,), fetch='all')
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
    query_sales = "SELECT total_revenue FROM vw_vendor_sales WHERE vendor_id = %s"
    sales_row = run_query(query_sales, (vendor_id,), fetch='one')
    total_sales = float(sales_row[0]) if sales_row else 0.0
    
    query_products = "SELECT COUNT(*) FROM product WHERE vendor_id = %s"
    prod_row = run_query(query_products, (vendor_id,), fetch='one')
    active_products = int(prod_row[0]) if prod_row else 0
    
    query_orders = """
        SELECT COUNT(DISTINCT o.order_id) 
        FROM orders o 
        LEFT JOIN delivery d ON o.order_id = d.order_id 
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN product p ON oi.product_id = p.product_id
        WHERE p.vendor_id = %s AND (d.delivery_status IS NULL OR d.delivery_status != 'delivered')
    """
    ord_row = run_query(query_orders, (vendor_id,), fetch='one')
    pending_orders = int(ord_row[0]) if ord_row else 0
    
    return {
        "total_sales": total_sales,
        "active_products": active_products,
        "pending_orders": pending_orders
    }
