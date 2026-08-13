# from model.customer import Customer # Commented out to prevent circular import with model.customer
class Order:
    def __init__(self,order_id,products,add_id,customer="Customer"):
        self.order_id=order_id
        self.products=products
        self.customer=customer
        self.add_id=add_id

    def set_shipping_company(self):
        pass


