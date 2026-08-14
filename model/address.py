import uuid

class Address:
    def __init__(self, city, street_address, customer_id, landmark=None, address_id=None):
        self.address_id = address_id or str(uuid.uuid4())[:6]
        self.city = city
        self.street_address = street_address
        self.customer_id = customer_id
        self.landmark = landmark

    def to_dict(self):
        return {
            "address_id": self.address_id,
            "city": self.city,
            "street": self.street_address,          # For frontend template compatibility
            "street_address": self.street_address,   # Matches DB schema column name
            "country": self.landmark,                # For frontend template compatibility
            "landmark": self.landmark,               # Matches DB schema column name
            "customer_id": self.customer_id
        }

    