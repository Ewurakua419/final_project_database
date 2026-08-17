import os
import mariadb
import dotenv

# Load .env from Application/configuration files/.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'configuration files', '.env')
dotenv.load_dotenv(dotenv_path=dotenv_path)

# Initialize a global connection pool
try:
    db_pool = mariadb.ConnectionPool(
        host=os.getenv("MARIA_DB_HOST", "localhost"),
        user=os.getenv("MARIA_DB_USER", "harisissah"),
        password=os.getenv("MARIA_DB_PASS"),
        database=os.getenv("MARIA_DB_DB", "ecommerce"),
        port=int(os.getenv("MARIA_DB_PORT", 3306)),
        pool_name="ecommerce_pool",
        pool_size=10
    )
except mariadb.PoolError as e:
    print(f"Error creating database connection pool: {e}")
    db_pool = None

def connect():
    """Retrieve a connection from the pool, or fallback to a direct connection."""
    if db_pool:
        try:
            return db_pool.get_connection()
        except mariadb.Error as pool_err:
            print(f"Pool connection checkout failed, falling back to direct connection: {pool_err}")
            
    return mariadb.connect(
        host=os.getenv("MARIA_DB_HOST", "localhost"),
        user=os.getenv("MARIA_DB_USER", "harisissah"),
        password=os.getenv("MARIA_DB_PASS"),
        database=os.getenv("MARIA_DB_DB", "ecommerce"),
        port=int(os.getenv("MARIA_DB_PORT", 3306))
    )

def run_query(query, params=None, fetch=None, commit=False):
    """Execute a query against MariaDB. Standardizes rollback handling for writes."""
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
    except mariadb.Error as err:
        if commit:
            try:
                conn.rollback()
            except mariadb.Error:
                pass
        raise err
    finally:
        cursor.close()
        conn.close()
