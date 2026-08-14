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
            return user

    def finduser_by_id(self, customer_id):
        rows = database.searchcustomer_by_id(customer_id)
        if rows == None:
            print("User not found by ID")
            return None
        else:
            first_name = rows[1]
            last_name = rows[2]
            return Customer(
                name=f"{first_name} {last_name}".strip(),
                password=rows[5],
                email=rows[4],
                unique_id=rows[0],
                ids=None,
                first_name=first_name,
                last_name=last_name,
                phone_number=rows[3],
            )

    ##customer focus
    # customer can register, *
    # sign in, *
    # select product and add to cart, *
    # remove product from cart , *
    # buy cart which consists of emptying cart into order,*
    #  create review, 
    # delete review, 
    #update review
    # update details
    def registerCustomer(self, name, password, email, first_name=None, last_name=None, phone_number=None):
        if database.searchcustomer(email) is not None:
            print("User already exists")
            return None
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
        
    def checkout(self, customer_id, shipping_address=None, payment_details=None, shipping_fee=0.0):
        # We now take customer_id directly from the JWT, skipping finduser lookup
        cart_data = self.get_cart(customer_id)
        if not cart_data or cart_data["total_items"] == 0:
            return None
            
        order_items = []
        subtotal_dollars = 0
        for item in cart_data["cart"]:
            prod = item["product"]
            price_dollars = prod.get("priceCents", 0)
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
        
        import uuid
        from model.address import Address
        from model.delivery import Delivery
        from model.order import Order
        
        # 1. Create and save Address if provided
        address_id = None
        shipping_address_dict = None
        if shipping_address:
            addr_obj = Address(
                city=shipping_address.get("city", "Accra"),
                street_address=shipping_address.get("street", "123 Liberation Road"),
                landmark=shipping_address.get("country", "Ghana"),
                customer_id=customer_id
            )
            database.add_address(addr_obj.to_dict())
            address_id = addr_obj.address_id
            shipping_address_dict = {
                "id": address_id,
                "street": shipping_address.get("street"),
                "city": shipping_address.get("city"),
                "country": shipping_address.get("country", "Ghana")
            }
        else:
            # Look up saved address
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

        # Generate 6-char order_id to fit VARCHAR(6) constraint
        order_id = str(uuid.uuid4())[:6]
        
        # Instantiate payment subclass and save details
        payment_dict = None
        if payment_details:
            from model.payment import Card, Momo, Bank_T
            pmeth = payment_details.get("method")
            if pmeth == "card":
                card_num = payment_details.get("card_last_4") or payment_details.get("card_num", "4242")
                payment_record = Card(cvv="123", card_num=card_num, expiry="12/26")
                payment_dict = {
                    "last_four": card_num[-4:] if len(card_num) >= 4 else card_num,
                    "brand": "Card"
                }
            elif pmeth == "momo":
                phone = payment_details.get("phone_number", "")
                net = payment_details.get("network", "")
                payment_record = Momo(phone=phone, acc_name="Customer Wallet", network=net)
                payment_dict = {
                    "last_four": phone[-4:] if len(phone) >= 4 else phone,
                    "brand": net or "Momo"
                }
            elif pmeth == "bank":
                acc_num = payment_details.get("acc_num") or "123456789"
                payment_record = Bank_T(acc_name="EcoBank Account", acc_num=acc_num, bank_name="EcoBank")
                payment_dict = {
                    "last_four": acc_num[-4:] if len(acc_num) >= 4 else acc_num,
                    "brand": "Bank Transfer"
                }
        
        # 2. Create Order
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
        
        # 3. Create Delivery linked to the address and order
        default_shipping_id = "SHIP01" # Defaulting to first shipping company
        delivery_obj = Delivery(
            order_id=new_order.order_id,
            delivery_status="on the way",
            address_id=address_id,
            shipping_id=default_shipping_id
        )
        database.add_delivery(delivery_obj.to_dict())
        
        # Clear cart
        database.checkout(customer_id)
        # Add order
        database.add_order(new_order.to_dict())
        
        return new_order

    def get_cart(self, customer_id):
        cart_items = database.getcart(customer_id)
        
        total_price = 0
        formatted_items = []
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

    def remove_from_cart(self, productid, customer_id):
        product = self.findproduct(productid)
        if product is None:
            return None
        
        database.removefromcart(productid, customer_id)
        return True

    def add_to_cart(self, productid, customer_id, quantity):
        product = self.findproduct(productid)
        if product is None:
            return None
            
        database.addtocart(product, customer_id, quantity)
        return True
    
    def create_review(self, username, message, productid):
        customer = self.finduser(username)
        if customer is None:
            return None
        product=self.findproduct(productid=productid)
        if product is None:
            return None
        #add to table message, userid and productid

    def get_customer_orders(self, customer_id):
        all_orders = database.get_all_orders()
        customer_orders = []
        for o in all_orders:
            if o.get("user_id") == customer_id or o.get("customer_id") == customer_id:
                o_copy = o.copy()
                customer = self.finduser_by_id(customer_id)
                if customer:
                    o_copy["customer_first_name"] = customer.first_name
                    o_copy["customer_last_name"] = customer.last_name
                customer_orders.append(o_copy)
        return customer_orders
        
    def get_vendor_orders(self, vendor_id):
        all_orders = database.get_all_orders()
        vendor_orders = []
        
        for order in all_orders:
            vendor_items = []
            vendor_subtotal = 0
            
            for item in order.get("items", []):
                product_id = item.get("product_id")
                if not product_id:
                    continue
                product = self.findproduct(product_id)
                if product and product.vendor_id == vendor_id:
                    vendor_items.append(item)
                    vendor_subtotal += item.get("item_total", 0)
                    
            if len(vendor_items) > 0:
                order_copy = order.copy()
                order_copy["items"] = vendor_items
                order_copy["pricing_summary"] = {
                    "subtotal": round(vendor_subtotal, 2),
                    "tax": 0,
                    "shipping": 0,
                    "grand_total": round(vendor_subtotal, 2)
                }
                
                cid = order_copy.get("customer_id") or order_copy.get("user_id")
                if cid:
                    customer = self.finduser_by_id(cid)
                    if customer:
                        order_copy["customer_first_name"] = customer.first_name
                        order_copy["customer_last_name"] = customer.last_name
                        
                vendor_orders.append(order_copy)
                
        return vendor_orders

    def get_vendor_stats(self, vendor_id):
        # Calculate active products
        all_products = self.get_all_products()
        active_products = sum(1 for p in all_products if p.vendor_id == vendor_id)
        
        # Calculate total sales and pending orders
        vendor_orders = self.get_vendor_orders(vendor_id)
        total_sales = 0
        pending_orders = 0
        
        if vendor_orders:
            for order in vendor_orders:
                # The pricing_summary is already pre-filtered for vendor items in get_vendor_orders
                total_sales += order.get("pricing_summary", {}).get("subtotal", 0)
                
                if order.get("status") == "pending":
                    pending_orders += 1
                    
        return {
            "total_sales": round(total_sales, 2),
            "active_products": active_products,
            "pending_orders": pending_orders
        }

    def update_order_status(self, order_id, new_status):
        success = database.update_order(order_id, {"status": new_status})
        if success:
            # Sync delivery status with order status
            delivery = database.get_delivery_by_order(order_id)
            if delivery:
                db_status = "on the way"
                status_lower = new_status.lower()
                if status_lower == "delivered":
                    db_status = "delivered"
                elif status_lower == "shipped":
                    db_status = "on the way"
                elif status_lower == "pending":
                    # For a newly placed/pending order, default delivery status is sent to port
                    db_status = "sent to port"
                
                delivery["delivery_status"] = db_status
        return success
        
    def get_product_reviews(self, product_id):
        from model.review import Review
        reviews_data = database.get_reviews_by_product(product_id)
        reviews = []
        for r in reviews_data:
            customer = self.finduser_by_id(r["customer_id"])
            customer_name = customer.name if customer else "Anonymous"
            reviews.append(Review(
                product_id=r["product_id"],
                customer_id=r["customer_id"],
                comment=r["comment"],
                rating=r["rating"],
                review_id=r["review_id"],
                review_date=r["review_date"],
                customer_name=customer_name
            ))
        return reviews
        
    def add_product_review(self, product_id, customer_id, comment, rating):
        from model.review import Review
        
        review = Review(
            product_id=product_id,
            customer_id=customer_id,
            comment=comment,
            rating=rating
        )
        
        # Save matching the DB schema instead of frontend format
        db_review = {
            "review_id": review.review_id,
            "product_id": review.product_id,
            "customer_id": review.customer_id,
            "comment": review.comment,
            "rating": review.rating,
            "review_date": review.review_date
        }
        database.add_review(db_review)
        return review

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
                name=rows[1],
                address="",
                unique_id=rows[0],
                phone_number=rows[3],
            )
            vendor.email = rows[2]
            vendor.password = rows[4]
            return vendor
            
    def registerVendor(self, name, password, email, address, phone_number=None):
        if database.searchvendor(email) is not None:
            print("Vendor already exists")
            return None
        passworde = auth.encodere(password)
        vendor = Vendor(name=name, address=address, unique_id=None, phone_number=phone_number)
        vendor.email = email
        vendor.password = passworde
        
        database.registervendor(
            name=name,
            email=email,
            password=passworde,
            vendorid=vendor.unique_id,
            address=address,
            phone_number=phone_number
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
    def _calculate_product_rating(self, product_id):
        reviews = database.get_reviews_by_product(product_id)
        count = len(reviews)
        if count == 0:
            return {"stars": 0, "count": 0}
        avg_stars = sum(r["rating"] for r in reviews) / count
        # Round to nearest half star
        avg_stars = round(avg_stars * 2) / 2
        return {"stars": avg_stars, "count": count}

    def get_all_products(self):
        raw_products = database.get_all_products()
        products = []
        for p_dict in raw_products:
            rating = self._calculate_product_rating(p_dict["product_id"])
            # Reconstruct Product object to return to frontend
            p = Product(
                product_name=p_dict["product_name"],
                vendor_id=p_dict["vendor_id"],
                price=p_dict.get("price", 0),
                image_url=p_dict.get("image_url", ""),
                product_type=p_dict.get("product_type", ""),
                product_id=p_dict["product_id"],
                description=p_dict.get("description", ""),
                rating=rating
            )
            products.append(p)
        return products

    def findproduct(self, productid):
        productid = productid.strip()
        rows = database.findproduct(productid)
        if rows is None:
            return None
        else:
            rating = self._calculate_product_rating(rows[0])
            # (product_id, vendor_id, product_name, price, image_url, product_type, description)
            product = Product(
                product_id=rows[0],
                vendor_id=rows[1],
                product_name=rows[2],
                price=rows[3],
                image_url=rows[4],
                product_type=rows[5],
                description=rows[6],
                rating=rating
            )
            return product

    def add_product(self, vendor_id, product_data):
        new_product = Product(
            product_name=product_data.get("name"),
            vendor_id=vendor_id,
            price=product_data.get("priceCents", 0),
            image_url=product_data.get("image", ""),
            product_type=product_data.get("type", "General"),
            description=product_data.get("description", "")
        )
        db_product = {
            "product_id": new_product.product_id,
            "vendor_id": new_product.vendor_id,
            "product_name": new_product.product_name,
            "price": new_product.price,
            "image_url": new_product.image_url,
            "product_type": new_product.product_type,
            "description": new_product.description,
            "stock_quantity": product_data.get("stock", 0)
        }
        database.addproduct(db_product)
        
        if new_product.product_type == "fashion":
            f_attrs = product_data.get("fashion_attributes", {})
            db_fashion = {
                "product_id": new_product.product_id,
                "color": f_attrs.get("Color", ""),
                "material": f_attrs.get("Material", ""),
                "size": f_attrs.get("Size", ""),
                "gender_category": f_attrs.get("Gender_category", "")
            }
            database.add_fashion(db_fashion)
        elif new_product.product_type == "beauty":
            b_attrs = product_data.get("beauty_attributes", {})
            db_beauty = {
                "product_id": new_product.product_id,
                "skin_type": b_attrs.get("skin_type", ""),
                "volume_weight": b_attrs.get("volume_weight", ""),
                "Is_organic": str(b_attrs.get("Is_organic", "False")).lower() in ("true", "1", "yes")
            }
            database.add_beauty(db_beauty)
            
        return new_product

    def update_product(self, vendor_id, product_id, updates):
        product = self.findproduct(product_id)
        if product is None or product.vendor_id != vendor_id:
            return None
            
        db_updates = {}
        if "name" in updates: db_updates["product_name"] = updates["name"]
        if "priceCents" in updates: db_updates["price"] = updates["priceCents"]
        if "image" in updates: db_updates["image_url"] = updates["image"]
        if "type" in updates: db_updates["product_type"] = updates["type"]
        if "description" in updates: db_updates["description"] = updates["description"]
        if "stock" in updates: db_updates["stock_quantity"] = updates["stock"]

        database.updateproduct(product_id, db_updates)
        
        f_attrs = updates.get("fashion_attributes")
        if f_attrs:
            db_f_updates = {}
            if "Color" in f_attrs: db_f_updates["color"] = f_attrs["Color"]
            if "Material" in f_attrs: db_f_updates["material"] = f_attrs["Material"]
            if "Size" in f_attrs: db_f_updates["size"] = f_attrs["Size"]
            if "Gender_category" in f_attrs: db_f_updates["gender_category"] = f_attrs["Gender_category"]
            database.update_fashion(product_id, db_f_updates)

        b_attrs = updates.get("beauty_attributes")
        if b_attrs:
            db_b_updates = {}
            if "skin_type" in b_attrs: db_b_updates["skin_type"] = b_attrs["skin_type"]
            if "volume_weight" in b_attrs: db_b_updates["volume_weight"] = b_attrs["volume_weight"]
            if "Is_organic" in b_attrs: db_b_updates["Is_organic"] = str(b_attrs["Is_organic"]).lower() in ("true", "1", "yes")
            database.update_beauty(product_id, db_b_updates)

        return self.findproduct(product_id)

    def deleteproduct(self, productid, vendor_id):
        product = self.findproduct(productid)
        if product is None or product.vendor_id != vendor_id:
            return False
        
        return database.deleteproduct(productid)

    #address focus
    def update_customer_profile(self, customer_id, data):
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        phone_number = data.get("phone_number")
        email = data.get("email")
        address_data = data.get("address")
        
        customer = self.finduser_by_id(customer_id)
        if not customer:
            return None
            
        if first_name is not None:
            customer.first_name = first_name
        if last_name is not None:
            customer.last_name = last_name
        if phone_number is not None:
            customer.phone_number = phone_number
        if email is not None:
            customer.email = email
            
        customer.name = f"{customer.first_name} {customer.last_name}".strip()
        
        for u in database.MOCK_USERS:
            if u["unique_id"] == customer_id:
                u["first_name"] = customer.first_name
                u["last_name"] = customer.last_name
                u["phone_number"] = customer.phone_number
                u["email"] = customer.email
                u["name"] = customer.name
                break
                
        address = None
        if address_data:
            from model.address import Address
            addr_list = database.get_addresses_by_customer(customer_id)
            if addr_list:
                existing_addr = addr_list[0]
                existing_addr["street"] = address_data.get("street", existing_addr.get("street"))
                existing_addr["street_address"] = address_data.get("street", existing_addr.get("street_address"))
                existing_addr["city"] = address_data.get("city", existing_addr.get("city"))
                existing_addr["country"] = address_data.get("country", existing_addr.get("country"))
                existing_addr["landmark"] = address_data.get("country", existing_addr.get("landmark"))
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
