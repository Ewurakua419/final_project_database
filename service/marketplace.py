import database
from model.customer import Customer
from model.vendor import Vendor
from model.product import Product
from model.address import Address
import auth

class Marketplace:
    def __init__(self, name):
        self.name=name

    # def finduser(self, name,password):
    def finduser(self, email):
        # name = name.strip().lower()
        # rows = database.searchcustomer(name,password)
        email = email.strip().lower()
        rows = database.searchcustomer(email)
        if rows == None:
            print("User not found")
            return None
        else:
            print("User found")
            user = Customer(
                name=rows[1],
                password=rows[2],
                unique_id=rows[0],
                ids=rows[3],
                email=rows[4],
            )
            return user

    ##customer focus
    # customer can register, *
    # sign in, *
    # select product and add to cart, 
    # remove product from cart , *
    # buy cart which consists of emptying cart into order,*
    #  create review, 
    # delete review, 
    #update review
    # update details
    def registerCustomer(self, name, password, email):
        # if database.search(name) is not None:
        if database.searchcustomer(email) is not None:
            print("User already exists")
            return None
        passworde = auth.encodere(password)
        # user = Customer(name=name, email=email,password=passworde)
        user = Customer(password=passworde, email=email)
        
        # database.register(
        #     name,
        #     userid=user.unique_id,
        #     cart_ids=user.cart.ids,
        #     balance=user.wallet.check_bal(),
        #     password=passworde,
        # )
        database.register(
            name=name,
            userid=user.unique_id,
            cart_ids=user.cart.ids,
            balance=0,
            password=passworde,
            email=email
        )

        print("Successful")
        return user

    # def login(self, name, password):
    def login(self, email, password):
        # customer = self.finduser(name,password)
        customer = self.finduser(email)

        if customer is None:
            print("Login unsuccessful: Username not found")
            return None

        if not auth.decodere(password, customer.password):
            print("Login unsuccessful: Wrong password")
            return None

        return customer


    def address_pick(self,username,address):
        customer = self.finduser(username)
        if customer is None:
            return None
        if address in customer.address:
            return address
        else:
            return None
        
    def ordercart(self, balance, username, address=None):
        customer = self.finduser(username)
        if customer is None:
            return None
       
        # order=customer.cart.pay(balance=balance,address=address)
        database.checkout(customer.unique_id)
        return True

    def get_cart(self, username):
        customer = self.finduser(username)
        if customer is None:
            return None
            
        cart_items = database.getcart(customer.unique_id)
        
        total_price = 0
        formatted_items = []
        for item in cart_items:
            product = item["product"]
            qty = item["quantity"]
            item_total = product.price * qty
            total_price += item_total
            formatted_items.append({
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "priceCents": product.price,
                    "image": getattr(product, "image", "products/placeholder.jpg")
                },
                "quantity": qty,
                "item_total": round(item_total, 2)
            })
            
        return {
            "cart": formatted_items,
            "total_items": sum(item["quantity"] for item in cart_items),
            "total_price": round(total_price, 2)
        }

    def remove_from_cart(self, productid, username):
        customer = self.finduser(username)
        if customer is None:
            return None

        product = self.findproduct(productid)
        if product is None:
            return None
        
        customer.cart.remove_product(product)
        database.removefromcart(productid, customer.unique_id)
        return True

    def add_to_cart(self, productid, username, quantity):
        customer = self.finduser(username)
        if customer is None:
            return None

        product = self.findproduct(productid)
        if product is None:
            return None
            
        customer.cart.add_product(product, quantity)
        database.addtocart(product, customer.unique_id, quantity)
        return True
    

    ##vendor focus
    #a vendor can--
    #add a new product
    #possibly remove products
    #restock
    # def findvendor(self, vendorid):
    #             vendorid = vendorid.strip().lower()
    #             rows = database.search(vendorid)#change to search vendor
    #             if rows == None:
    #                 print("User not found")
    #                 return None
    #             else:
    #                 print("User found")
    #                 vendor = Vendor(#edit to match database
    #                     name=rows[1],
    #                     unique_id=rows[2],
    #                     address=rows[0],
    #                 )
    #                 return vendor
                    
    def findvendor(self, email):
        email = email.strip().lower()
        rows = database.searchvendor(email)
        if rows is None:
            print("Vendor not found")
            return None
        else:
            print("Vendor found")
            vendor = Vendor(
                address=rows[0],
                name=rows[1],
                unique_id=rows[2],
            )
            vendor.email = rows[3]
            vendor.password = rows[4]
            return vendor
            
    def registerVendor(self, name, password, email, address):
        if database.searchvendor(email) is not None:
            print("Vendor already exists")
            return None
        passworde = auth.encodere(password)
        vendor = Vendor(name=name, address=address, unique_id=None)
        vendor.email = email
        vendor.password = passworde
        
        database.registervendor(
            name=name,
            email=email,
            password=passworde,
            vendorid=vendor.unique_id,
            address=address
        )
        print("Vendor registration successful")
        return vendor

    def loginVendor(self, email, password):
        vendor = self.findvendor(email)

        if vendor is None:
            print("Login unsuccessful: Vendor not found")
            return None

        if not auth.decodere(password, vendor.password):
            print("Login unsuccessful: Wrong password")
            return None

        return vendor
                
    ##product focus
    def get_all_products(self):
        raw_products = database.get_all_products()
        products = []
        for p_dict in raw_products:
            # Reconstruct Product object to return to frontend
            p = Product(
                product_name=p_dict["name"],
                vendor_id=p_dict["vendor_id"],
                price=p_dict.get("priceCents", 0),
                image_url=p_dict.get("image", ""),
                product_type=p_dict.get("type", ""),
                product_id=p_dict["id"],
                description=p_dict.get("description", "")
            )
            products.append(p)
        return products

    def findproduct(self, productid):
        productid = productid.strip().lower()
        rows = database.findproduct(productid)
        if rows is None:
            return None
        else:
            # (product_id, vendor_id, product_name, price, image_url, product_type, description)
            product = Product(
                product_id=rows[0],
                vendor_id=rows[1],
                product_name=rows[2],
                price=rows[3],
                image_url=rows[4],
                product_type=rows[5],
                description=rows[6]
            )
            return product

    def add_product(self, vendor_email, product_data):
        vendor = self.findvendor(vendor_email)
        if vendor is None:
            return None
            
        new_product = Product(
            product_name=product_data.get("name"),
            vendor_id=vendor.unique_id,
            price=product_data.get("priceCents", 0),
            image_url=product_data.get("image", ""),
            product_type=product_data.get("type", "General"),
            description=product_data.get("description", "")
        )
        # We store it in db using to_dict to match the mock storage format
        database.addproduct(new_product.to_dict())
        return new_product

    def update_product(self, vendor_email, product_id, updates):
        vendor = self.findvendor(vendor_email)
        if vendor is None:
            return None
            
        product = self.findproduct(product_id)
        if product is None or product.vendor_id != vendor.unique_id:
            return None
            
        database.updateproduct(product_id, updates)
        return self.findproduct(product_id)

    def deleteproduct(self, productid, vendor_email):
        vendor = self.findvendor(vendor_email)
        if vendor is None:
            return False

        product = self.findproduct(productid)
        if product is None or product.vendor_id != vendor.unique_id:
            return False
        
        return database.deleteproduct(productid)

    #address focus
