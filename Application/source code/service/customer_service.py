import uuid
import database
import auth
from model.customer import Customer
from model.address import Address
from model.delivery import Delivery
from model.order import Order
from model.product import Product
from service.exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    AccountSuspendedError,
    ProductNotFoundError
)

class CustomerService:
    def finduser(self, email):
        email = email.strip().lower()
        rows = database.searchcustomer(email)
        if rows is None:
            raise UserNotFoundError("Customer not found")
            
        first_name = rows[1]
        last_name = rows[2]
        user = Customer(
            name=f"{first_name} {last_name}".strip(),
            password=rows[5],
            email=rows[4],
            unique_id=rows[0],
            ids=None,
            first_name=first_name,
            last_name=last_name,
            phone_number=rows[3],
        )
        user.is_active = rows[6]
        return user

    def finduser_by_id(self, customer_id):
        rows = database.searchcustomer_by_id(customer_id)
        if rows is None:
            raise UserNotFoundError("Customer not found by ID")
            
        first_name = rows[1]
        last_name = rows[2]
        user = Customer(
            name=f"{first_name} {last_name}".strip(),
            password=rows[5],
            email=rows[4],
            unique_id=rows[0],
            ids=None,
            first_name=first_name,
            last_name=last_name,
            phone_number=rows[3],
        )
        user.is_active = rows[6]
        return user

    def register(self, name, password, email, first_name=None, last_name=None, phone_number=None):
        if database.searchcustomer(email) is not None:
            return None # Facade handles user exists check
            
        passworde = auth.encodere(password)
        user = Customer(
            name=name,
            password=passworde,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        
        database.register(
            name=name,
            userid=user.unique_id,
            cart_ids=user.cart.ids,
            balance=0,
            password=passworde,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        return user

    def login(self, email, password):
        customer = self.finduser(email)
        if not auth.decodere(password, customer.password):
            raise InvalidCredentialsError("Wrong password")
        if not customer.is_active:
            raise AccountSuspendedError("Customer account is suspended")
        return customer

    def address_pick(self, username, address):
        customer = self.finduser(username)
        if address in customer.address:
            return address
        return None

    def checkout(self, customer_id, shipping_address=None, payment_details=None, shipping_fee=0.0, shipping_id=None):
        cart_data = self.get_cart(customer_id)
        if not cart_data or cart_data["total_items"] == 0:
            return None
            
        order_items = []
        subtotal_dollars = 0
        for item in cart_data["cart"]:
            prod = item["product"]
            price_dollars = prod.get("price", 0)
            item_total = price_dollars * item["quantity"]
            subtotal_dollars += item_total
            
            order_items.append({
                "product_id": prod.get("id"),
                "name": prod.get("name"),
                "image": prod.get("image"),
                "price_at_purchase": price_dollars,
                "quantity": item["quantity"],
                "item_total": round(item_total, 2)
            })
            
        subtotal = round(subtotal_dollars, 2)
        items = order_items
        
        # 1. Create and save Address if provided
        address_id = None
        shipping_address_dict = None
        if shipping_address:
            street = shipping_address.get("street") or shipping_address.get("street_address", "123 Liberation Road")
            landmark = shipping_address.get("country") or shipping_address.get("landmark") or shipping_address.get("Landmark", "Ghana")
            addr_obj = Address(
                city=shipping_address.get("city", "Accra"),
                street_address=street,
                landmark=landmark,
                customer_id=customer_id
            )
            database.add_address(addr_obj.to_dict())
            address_id = addr_obj.address_id
            shipping_address_dict = {
                "id": address_id,
                "street": street,
                "city": shipping_address.get("city"),
                "country": landmark
            }
        else:
            addr_list = database.get_addresses_by_customer(customer_id)
            if addr_list:
                addr = addr_list[0]
                address_id = addr.get("address_id")
                shipping_address_dict = {
                    "id": address_id,
                    "street": addr.get("street") or addr.get("street_address"),
                    "city": addr.get("city"),
                    "country": addr.get("country") or addr.get("landmark", "Ghana")
                }

        order_id = str(uuid.uuid4())
        
        # Instantiate payment record representation
        payment_dict = None
        if payment_details:
            pmeth = payment_details.get("method") or payment_details.get("type")
            if pmeth == "card":
                card_num = payment_details.get("card_last_4") or payment_details.get("card_num", "4242")
                payment_dict = {
                    "last_four": card_num[-4:] if len(card_num) >= 4 else card_num,
                    "brand": "Card"
                }
            elif pmeth == "momo":
                phone = payment_details.get("phone_number", "")
                net = payment_details.get("network", "")
                payment_dict = {
                    "last_four": phone[-4:] if len(phone) >= 4 else phone,
                    "brand": net or "Momo"
                }
            elif pmeth == "bank":
                acc_num = payment_details.get("acc_num") or "123456789"
                payment_dict = {
                    "last_four": acc_num[-4:] if len(acc_num) >= 4 else acc_num,
                    "brand": "Bank Transfer"
                }
        
        new_order = Order(
            cart_id=customer_id, 
            customer_id=customer_id, 
            subtotal=subtotal, 
            shipping_fee=shipping_fee,
            items=items,
            order_id=order_id,
            shipping_address=shipping_address_dict,
            payment_details=payment_dict
        )
        
        resolved_shipping_id = shipping_id if shipping_id else "SHIP01"
        delivery_obj = Delivery(
            order_id=new_order.order_id,
            delivery_status="pending",
            address_id=address_id,
            shipping_id=resolved_shipping_id
        )
        
        database.add_order(new_order.to_dict(), delivery_dict=delivery_obj.to_dict())
        return new_order

    def get_cart(self, customer_id):
        cart_items = database.getcart(customer_id)
        formatted_items = []
        total_price = 0.0
        for item in cart_items:
            product = item["product"]
            qty = item["quantity"]
            item_total = product.price * qty
            total_price += item_total
            formatted_items.append({
                "product": product.to_dict(),
                "quantity": qty,
                "item_total": round(item_total, 2)
            })
            
        return {
            "cart": formatted_items,
            "total_items": sum(item["quantity"] for item in cart_items),
            "total_price": round(total_price, 2)
        }

    def add_to_cart(self, productid, customer_id, quantity):
        # Validate product existence
        rows = database.findproduct(productid)
        if rows is None:
            raise ProductNotFoundError("Product not found")
        product = Product(
            product_id=rows[0],
            vendor_id=rows[1],
            product_name=rows[2],
            price=rows[3],
            image_url=rows[4],
            product_type=rows[5],
            description=rows[6]
        )
        database.addtocart(product, customer_id, quantity)
        return True

    def remove_from_cart(self, productid, customer_id):
        rows = database.findproduct(productid)
        if rows is None:
            raise ProductNotFoundError("Product not found")
        database.removefromcart(productid, customer_id)
        return True

    def delete_customer_address(self, customer_id, address_id):
        return database.delete_address(address_id, customer_id)

    def get_customer_orders(self, customer_id):
        all_orders = database.get_all_orders()
        customer_orders = []
        for o in all_orders:
            if o.get("user_id") == customer_id or o.get("customer_id") == customer_id:
                o_copy = o.copy()
                try:
                    customer = self.finduser_by_id(customer_id)
                    if customer:
                        o_copy["customer_first_name"] = customer.first_name
                        o_copy["customer_last_name"] = customer.last_name
                except UserNotFoundError:
                    pass
                customer_orders.append(o_copy)
        return customer_orders

    def update_customer_profile(self, customer_id, data):
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        phone_number = data.get("phone_number")
        email = data.get("email")
        address_data = data.get("address")
        
        customer = self.finduser_by_id(customer_id)
        if first_name is not None:
            customer.first_name = first_name
        if last_name is not None:
            customer.last_name = last_name
        if phone_number is not None:
            customer.phone_number = phone_number
        if email is not None:
            customer.email = email
            
        customer.name = f"{customer.first_name} {customer.last_name}".strip()
        
        updates = {}
        if first_name is not None:
            updates["f_name"] = first_name
        if last_name is not None:
            updates["l_name"] = last_name
        if phone_number is not None:
            updates["phone_number"] = phone_number
        if email is not None:
            updates["email"] = email
        if updates:
            database.update_customer(customer_id, updates)
                
        address = None
        if address_data:
            addr_list = database.get_addresses_by_customer(customer_id)
            if addr_list:
                existing_addr = addr_list[0]
                addr_updates = {}
                if address_data.get("street"):
                    addr_updates["street_address"] = address_data["street"]
                if address_data.get("city"):
                    addr_updates["city"] = address_data["city"]
                if address_data.get("country"):
                    addr_updates["landmark"] = address_data["country"]
                if addr_updates:
                    database.update_address(existing_addr.get("address_id", ""), addr_updates)
                existing_addr.update(addr_updates)
                address = existing_addr
            else:
                addr_obj = Address(
                    city=address_data.get("city", ""),
                    street_address=address_data.get("street", ""),
                    landmark=address_data.get("country", ""),
                    customer_id=customer_id
                )
                database.add_address(addr_obj.to_dict())
                address = addr_obj.to_dict()
                
        return {
            "email": customer.email,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone_number": customer.phone_number,
            "address": address
        }
