import psycopg
from datetime import date
from model.transaction import Transaction
import uuid
def connect():
    return psycopg.connect(
        host="localhost",
        dbname="wallet",
        user="postgres",
        password=" ",
        port=5432
    )
##Write data
#cur.execute("INSERT INTO students (name, age) VALUES (%s, %s)",("Alice", 20))
#conn.commit()

##read data
#cur.execute("SELECT * FROM students")
#rows = cur.fetchall()
#for row in rows:
#    print(row)

def search(user):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT users.*,wallet.id, wallet.balance
                FROM wallet
                JOIN users ON wallet.user_id = users.id
                WHERE users.username = %s
                """, (user,))
            rows = cur.fetchone()
            if not rows:
                return None
            return rows

def withdraw(userid:str, balance:int, tr:Transaction):
    with connect() as conn:
        with conn.cursor() as cur:
            """balance=rows[2]

            balance-=amt"""
            cur.execute("update wallet set balance= %s where user_id=%s",(balance,userid))

            cur.execute("insert into transactions values(%s,%s,%s,%s,%s,%s)",(tr.id,tr.sender,tr.reciever,tr.amount,tr.type,tr.timestamp))
            conn.commit()

def register(name:str, balance:int, password:str, ids:str, userid:str):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("Insert into users(id, username, password)  values (%s,%s,%s)",(userid, name, password))
            cur.execute("Insert into wallet(id, user_id, balance) values (%s,%s,%s)",(ids,userid, balance))
            conn.commit()

def deposit(userid:str, balance:int, tr:Transaction, ):
    with connect() as conn:
        with conn.cursor() as cur:
            """balance=rows[2]
            balance+=amt"""
            cur.execute("update wallet set balance= %s where user_id=%s",(balance,userid))
            cur.execute("insert into transactions values(%s,%s,%s,%s,%s,%s)",(tr.id,tr.sender,tr.reciever,tr.amount,tr.type,tr.timestamp))
            conn.commit()

def undo():
    with connect() as conn:
        conn.rollback()

def getTransactions(wallet_id):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("select * from transactions where sender_wallet_id=%s or reciever_wallet_id=%s",(wallet_id,wallet_id))
            conn.commit()