import uuid

class Shipping:
    def __init__(self, name, address,unique_id, rate):
        if unique_id==None:
            self.unique_id = str(uuid.uuid4())[:20]
        else:
            self.unique_id=unique_id
        self.name=name
        self.address=address#Address class
        self.rate=rate
