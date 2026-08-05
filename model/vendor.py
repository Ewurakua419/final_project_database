from model.address import Address
import uuid
class Vendor:
    def __init__(self, name, address,unique_id):
        if unique_id==None:
            self.unique_id = str(uuid.uuid4())[:20]
        else:
            self.unique_id=unique_id
        self.name=name
        self.address=address#Address class
        self.products=[]