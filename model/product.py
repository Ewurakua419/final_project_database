import uuid

class Product:
    def __init__(self, product_name, vendor_id, price, image_url, product_type, product_id=None, description="", rating=None):
        self.product_name = product_name
        self.vendor_id = vendor_id
        self.price = price
        self.image_url = image_url
        self.product_type = product_type
        self.description = description
        
        if rating is None:
            self.rating = {"stars": 0, "count": 0}
        else:
            self.rating = rating
        
        if product_id is None:
            self.product_id = str(uuid.uuid4())
        else:
            self.product_id = product_id

    def to_dict(self):
        return {
            "id": self.product_id,
            "name": self.product_name,
            "image": self.image_url,
            "priceCents": self.price,
            "type": self.product_type,
            "description": self.description,
            "vendor_id": self.vendor_id,
            "rating": self.rating,
            "keywords": [], # Default for now
            "stock": 10 # Default for now
        }

class Fashion(Product):

    def __init__(
        self,
        product_name,
        vendor_id,
        size,
        product_type,
        color,
        material,
        gender_category,
        price,
        image_url,
        description="",
    ):
        super().__init__(
            product_name, vendor_id, price, image_url, product_type, description=description
        )
        self.size=size
        self.color=color
        self.material=material
        self.gender_category=gender_category


class Beauty(Product):

    def __init__(
        self,
        product_name,
        vendor_id,
        category,
        expiry_date,
        price,
        image_url,
        product_type,
        description="",
    ):
        super().__init__(
            product_name, vendor_id, price, image_url, product_type, description=description
        )
        self.category=category
        self.expiry=expiry_date
