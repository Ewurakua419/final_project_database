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
        
    def ordercart(self,balance, username, address):
        customer = self.finduser(username)
        if customer is None:
            return None
       
        order=customer.cart.pay(balance=balance,address=address)
        # add order to database when built
        #make allowance that product quantitu would reduce and if the product has 0 it is removed from cart

        return True

    def remove_from_cart(self,productid, username):
        customer = self.finduser(username)
        if customer is None:
            return None

        product=self.findproduct(productid=productid)
        if product is None:
            return None
        
        customer.cart.remove_product(product)
        # remove from cart database when built
        return customer.cart.products

    def add_to_cart(self, productid, username):
        customer = self.finduser(username)
        if customer is None:
            return None

        product=self.findproduct(productid=productid)
        if product is None:
            return None
        if customer.cart.check_product(product):
            return True
            #let database increment count
        else: 
            customer.cart.add_product(product)
        # remove from cart database when built
        return customer.cart.products
    

    ##vendor focus
    ##product focus
    def findproduct(self, productid):
            productid = productid.strip().lower()
            rows = database.search(productid)#change to search product
            if rows == None:
                print("User not found")
                return None
            else:
                print("User found")
                product = Product(#edit to match database
                    name=rows[1],
                    vendor_id=rows[2],
                    brand=rows[0],
                    price=rows[3],
                    quantity=rows[4],
                    ids=rows[0]
                )
                return product

    def deleteproduct(self,productid, vendorid):
        #find vendor
        #delete from database
