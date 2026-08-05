class Product:
    def __init__(self, name, vendor_id, brand, price, quantity):
        self.brand=brand
        self.name=name
        self.vendor_id=vendor_id
        self.price=price
        self.quantity=quantity

class Fashion(Product):

    def __init__(self, name, vendor_id, brand, size, types, category, price, quantity):
        super().__init__(name, vendor_id, brand, price, quantity)
        self.size=size
        self.type=types #eg trousers shirt pants
        self.category=category#eg male or female or kids


class Beauty(Product):

    def __init__(self, name, vendor_id, brand, category, expiry_date, price, quantity):
        super().__init__(name, vendor_id, brand, price, quantity)
        self.category=category
        self.expiry=expiry_date


class Tech(Product):

    def __init__(self, name, vendor_id, brand, dimensions, category, price, quantity):
        super().__init__(name, vendor_id, brand, price, quantity)
        self.dimensions=dimensions#w*h*l
        self.category=category#type of item


class Food(Product):

    def __init__(self, name, vendor_id, brand, expiry, price, quantity):
        super().__init__(name, vendor_id, brand, price, quantity)
        self.expiry=expiry
