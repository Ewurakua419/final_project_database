import uuid

class ShippingCompany:
    def __init__(self, name, contact_phone=None, shipping_id=None):
        self.shipping_id = shipping_id or str(uuid.uuid4())[:6]
        self.name = name
        self.contact_phone = contact_phone or ""

    def to_dict(self):
        return {
            "shipping_id": self.shipping_id,
            "name": self.name,
            "contact_phone": self.contact_phone
        }

