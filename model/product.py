import uuid

class Product:
    def __init__(self, name, vendor_id,price, quantity, description, types,ids=None):
        
        self.name=name
        self.vendor_id=vendor_id
        self.price=price
        self.quantity=quantity
        self.description=description
        self.type=types
        if ids==None:
                    self.ids=str(uuid.uuid4())[:20]
        else:
            self.ids=ids

class Fashion(Product):

    def __init__(
        self,
        name,
        vendor_id,
        size,
        types,
        color,
        material,
        gender_category,
        price,
        quantity,
        description,
    ):
        super().__init__(
            name, vendor_id, price, quantity, types=types, description=description
        )
        self.size=size
        self.type=types #eg trousers shirt pants
        self.gender_category=gender_category#eg male or female or kids


class Beauty(Product):

    def __init__(
        self,
        name,
        vendor_id,
        category,
        expiry_date,
        price,
        quantity,
        types,
        description,
    ):
        super().__init__(
            name, vendor_id, price, quantity, types=types, description=description
        )
        self.category=category
        self.expiry=expiry_date
