import database
from model.customer import Customer
from model.vendor import Vendor
import auth

class Marketplace:
    def __init__(self, name):
        self.name=name

    def finduser(self, name):
        name = name.strip().lower()
        rows = database.search(name)
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
    def registerCustomer(self, name, password, email):
        if database.search(name) is not None:
            print("User already exists")
            return None
        passworde = auth.encodere(password)
        user = Customer(name=name, email=email,password=passworde)
        database.register(
            name,
            userid=user.unique_id,
            cart_ids=user.cart.ids,
            balance=user.wallet.check_bal(),
            password=passworde,
        )

        print("Successful")
        return user

    def login(self, name, password):
        customer = self.finduser(name)

        if customer is None:
            print("Login unsuccessful: Username not found")
            return None

        if not auth.decodere(password, customer.password):
            print("Login unsuccessful: Wrong password")
            return None

        return customer

    def add_to_cart(self,product, username):
        customer = self.finduser(username)
        if customer is None:
            return None
        customer.cart.products.append(product)
        return customer.cart.products

    def address_pick(self,username,address):
        customer = self.finduser(username)
        if customer is None:
            return None
        if address in customer.address:
            return address
        else:
            return None
        
    def empty_cart(self,balance, username, address):
        customer = self.finduser(username)
        if customer is None:
            return None
       
        order=customer.cart.pay(balance=balance,address=address)
        # add order to database when built

        return True

    def remove_from_cart(self,product, username):
        customer = self.finduser(username)
        if customer is None:
            return None
        customer.cart.products.remove(product)
        # remove from cart database when built
        return customer.cart.products

    

    ##vendor focus
