import uuid
# from model.customer import Customer # Commented out to prevent circular import with model.customer
# from model.transaction import Transaction
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
            return order1

    def remove_product(self, product):
        for i, item in enumerate(self.products):
            if item["product"].id == product.id:
                self.products.pop(i)
                return True
        return None

    def add_product(self, product, quantity):
        for item in self.products:
            if item["product"].id == product.id:
                item["quantity"] += quantity
                return True
        self.products.append({"product": product, "quantity": quantity})
        return True

    def check_product(self, product):
        for item in self.products:
            if item["product"].id == product.id:
                 return True
        return False
        