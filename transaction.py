from datetime import datetime
from address import Address
import uuid
import json
class Transaction:
    def __init__(self,amount, user, order_id, product, address):
        self.id=str(uuid.uuid4())
        self.user=user
        self.order_id=order_id
        self.product=[product]
        self.amount=amount
        self.timestamp=datetime.now()
        self.address=address
    
    def to_dict(self):
        return {
            "User": self.user,
            "Order_Id": self.order_id,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
            "product": self.product,
            "Address":self.address.to_dict()
        }