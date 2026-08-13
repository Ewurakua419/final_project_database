import uuid
# from model.customer import Customer # Commented out to prevent circular import with model.customer
from model.transaction import Transaction
from model.order import Order
class Cart:
    def __init__(self,customer:"Customer", ids=None):
        self.balance=0
        self.products=[]
        self.user=customer
        if ids==None:
                    self.ids=str(uuid.uuid4())[:20]
        else:
            self.ids=ids

    def pay(self, balance, address):
        if balance==self.balance:
            order_id=str(uuid.uuid4())[:20]
            order1=Order(order_id=order_id,products=self.products, customer=self.user.unique_id, add_id=address.id)
            self.user.history.append(Transaction(amount=balance, user=self.user.unique_id, order_id=order_id, product=self.products, address=address.id))
            return order1

    def remove_product(self, product):
        if product in self.products:
            self.products.remove(product)

        else:
            return None

    def add_product(self,product):
        self.products.append(product)

    def check_product(self,product):
        if product in self.products:
             return True
        else:
             return False
        