import uuid
from model.cart import Cart
from model.address import Address
class Customer:
    def __init__(self, name, password, email, unique_id=None, ids=None, first_name=None, last_name=None, phone_number=None):
            self.name=name
            self.email=email
            self.first_name = first_name or (name.split(" ")[0] if name else "")
            self.last_name = last_name or (name.split(" ")[1] if name and len(name.split(" ")) > 1 else "")
            self.phone_number = phone_number or ""
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



