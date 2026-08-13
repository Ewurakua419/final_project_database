import psycopg
from datetime import date
from model.transaction import Transaction
import uuid
import mariadb
def connect():
    return mariadb.connect(
    host="localhost",
    user="loisamoah",
    password=" ",
    database="ecommerce",
    port=3306
)
##Write data
# cur.execute("INSERT INTO students (name, age) VALUES (%s, %s)",("Alice", 20))
# conn.commit()

##read data
# cur.execute("SELECT * FROM students")
# rows = cur.fetchall()
# for row in rows:
#    print(row)
def searchcustomer(email):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT customer.*, cart.cart_id, cart_items.product_id
                FROM customer
                JOIN cart
                    ON customer.customer_id = cart.customer_id
                JOIN cart_items
                    ON cart.cart_id = cart_items.cart_id
                JOIN customer_credentials
                    ON customer.customer_id = customer_credentials.customer_id
                WHERE customer.email = %s
                """,
                (email,)
            )
            rows = cur.fetchone()
            if not rows:
                return None
            return rows


def login(email, password):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT customer.*,cart.id,customer_credentials.password_hash
                FROM customer
                JOIN customer_credentials
                    ON customer.customer_id = customer_credentials.customer_id
                WHERE customer.email = %s""",
                (email, ),
            )
            rows = cur.fetchone()
            if not rows:
                return None
            if password==rows[-1]:
                return rows


def register(f_name, l_name):
    pass

def undo():
    with connect() as conn:
        conn.rollback()


def findproduct(productid):
    with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """select product.* from product where product_id=%s""",(productid,))
                rows = cur.fetchone()
                if not rows:
                    return None
                return rows


def addproduct(product, ):
    
    with connect() as conn:
            with conn.cursor() as cur:
                if findproduct(productid=product.id)==None:
                    cur.execute("insert into product values(%s,%s,%s,%s,%s,%s,%s)",(product.id,
                            product.name,
                            product.vendor_id,
                            product.price,
                            product.quantity,
                            product.description,
                            product.type,))
                else:
                    cur.execute("select quantity from product where product_id= %s",(product.id))
                    rows = cur.fetchone()
                    quantity=rows[0]
                    quantity+=product.quantity
                    cur.execute("update product set quantity = %s where product_id = %s",(quantity,product.id))
                conn.commit()

def deleteproduct(productid):
    if findproduct(productid)!=None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(" delete from product where product_id=%s",(productid))

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


def addtocart(product, customer,quantity):#check spellling for cart_item
    dates=date.today()
    if searchcustomer(customer.email)!=None:
        
        with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT cart_id
                        FROM  cart
                        WHERE where cart.customer_id = %s """,
                        (customer.customer_id,),
                    )
                    rows = cur.fetchone()
                    ids=rows[0]
                    cur.execute(
                                """
                                SELECT quantity
                                FROM  product
                                WHERE  product_id = %s """,
                                (product.id),
                            )
                    rows = cur.fetchone()
                    quant=rows[0]
                    if quant-quantity>=0:
                        cur.execute("insert into cart_items values (%s, %s,%s,%s)",(product.id, ids,quantity,dates))

                    else:
                        print("too few items available")
