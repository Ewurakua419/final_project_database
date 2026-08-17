import database
from service.customer_service import CustomerService
from service.vendor_service import VendorService
from service.catalog_service import CatalogService
from service.exceptions import MarketplaceException, UserNotFoundError, ProductNotFoundError

class Marketplace:
    def __init__(self, name):
        self.name = name
        self.customers = CustomerService()
        self.vendors = VendorService()
        self.catalog = CatalogService()

    def finduser(self, email):
        try:
            user = self.customers.finduser(email)
            print("User found")
            return user
        except UserNotFoundError:
            print("User not found")
            return None

    def finduser_by_id(self, customer_id):
        try:
            return self.customers.finduser_by_id(customer_id)
        except UserNotFoundError:
            print("User not found by ID")
            return None

    def registerCustomer(self, name, password, email, first_name=None, last_name=None, phone_number=None):
        user = self.customers.register(name, password, email, first_name, last_name, phone_number)
        if user is None:
            print("User already exists")
            return None
        print("Successful")
        return user

    def login(self, email, password):
        try:
            return self.customers.login(email, password)
        except MarketplaceException as e:
            print(f"Login unsuccessful: {e}")
            return None

    def address_pick(self, username, address):
        try:
            return self.customers.address_pick(username, address)
        except MarketplaceException:
            return None

    def checkout(self, customer_id, shipping_address=None, payment_details=None, shipping_fee=0.0, shipping_id=None):
        return self.customers.checkout(customer_id, shipping_address, payment_details, shipping_fee, shipping_id)

    def get_cart(self, customer_id):
        return self.customers.get_cart(customer_id)

    def remove_from_cart(self, productid, customer_id):
        try:
            return self.customers.remove_from_cart(productid, customer_id)
        except ProductNotFoundError:
            return None

    def add_to_cart(self, productid, customer_id, quantity):
        try:
            return self.customers.add_to_cart(productid, customer_id, quantity)
        except ProductNotFoundError:
            return None

    def delete_customer_address(self, customer_id, address_id):
        return self.customers.delete_customer_address(customer_id, address_id)
    
    def create_review(self, username, message, productid, rating=5):
        try:
            customer = self.customers.finduser(username)
            # Use unique_id (fixed bug where user code used customer.id)
            return self.catalog.add_product_review(product_id=productid, customer_id=customer.unique_id, comment=message, rating=rating)
        except MarketplaceException:
            return None

    def get_customer_orders(self, customer_id):
        return self.customers.get_customer_orders(customer_id)
        
    def get_vendor_orders(self, vendor_id):
        return self.vendors.get_vendor_orders(vendor_id, self.customers.finduser_by_id)

    def get_vendor_stats(self, vendor_id):
        return self.vendors.get_vendor_stats(vendor_id)

    def update_order_status(self, order_id, new_status):
        success = database.update_order(order_id, {"status": new_status})
        if success:
            delivery = database.get_delivery_by_order(order_id)
            if delivery:
                db_status = "on the way"
                status_lower = new_status.lower()
                if status_lower == "delivered":
                    db_status = "delivered"
                elif status_lower == "shipped":
                    db_status = "on the way"
                elif status_lower == "pending":
                    db_status = "pending"
                
                # Update delivery status safely via database trigger/procedure update
                database.update_delivery_status(delivery["delivery_id"], db_status)
        return success
        
    def get_product_reviews(self, product_id):
        return self.catalog.get_product_reviews(product_id)
        
    def add_product_review(self, product_id, customer_id, comment, rating):
        return self.catalog.add_product_review(product_id, customer_id, comment, rating)

    def findvendor(self, email):
        try:
            vendor = self.vendors.findvendor(email)
            print("Vendor found")
            return vendor
        except UserNotFoundError:
            print("Vendor not found")
            return None
            
    def registerVendor(self, name, password, email, address, phone_number=None):
        vendor = self.vendors.register(name, password, email, address, phone_number)
        if vendor is None:
            print("Vendor already exists")
            return None
        print("Vendor registration successful")
        return vendor

    def loginVendor(self, email, password):
        try:
            return self.vendors.login(email, password)
        except MarketplaceException as e:
            print(f"Login unsuccessful: {e}")
            return None
                
    def _calculate_product_rating(self, product_id):
        return self.catalog._calculate_product_rating(product_id)

    def get_all_products(self):
        return self.catalog.get_all_products()

    def findproduct(self, productid):
        try:
            return self.catalog.findproduct(productid)
        except ProductNotFoundError:
            return None

    def add_product(self, vendor_id, product_data):
        return self.vendors.add_product(vendor_id, product_data)

    def update_product(self, vendor_id, product_id, updates):
        try:
            self.vendors.update_product(vendor_id, product_id, updates)
            return self.catalog.findproduct(product_id)
        except MarketplaceException:
            return None

    def deleteproduct(self, productid, vendor_id):
        return self.vendors.delete_product(productid, vendor_id)

    def update_customer_profile(self, customer_id, data):
        try:
            return self.customers.update_customer_profile(customer_id, data)
        except MarketplaceException:
            return None
