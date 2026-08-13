import uuid
from model.cart import Cart
from model.address import Address
class Customer:
    def __init__(self, password, email, unique_id=None, ids=None):
            self.email=email
            if unique_id==None:
                self.unique_id = str(uuid.uuid4())[:20]
            else:
                self.unique_id=unique_id
            self.cart=Cart(customer=self, ids=ids)
            self.wallet=[]
            self.address=[]
            self.password=str(password)

    def add_address(self,country,  postcode, city, street, house_num):
        self.address.append(Address(country,  postcode, city, street, house_num))

    def remove_address(self,addresses):
        if addresses in self.address:
            self.address.remove(addresses)
              

    def check_history(self):
        return (h.to_dict() for h in self.history)

    def add_payment(self, payment):
        self.wallet.append(payment)



