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
                first_name=rows[5] if len(rows) > 5 else None,
                last_name=rows[6] if len(rows) > 6 else None,
                phone_number=rows[7] if len(rows) > 7 else None,
            )
            return user

    def finduser_by_id(self, customer_id):
        rows = database.searchcustomer_by_id(customer_id)
        if rows == None:
            print("User not found by ID")
            return None
        else:
            return Customer(
                name=rows[1],
                password=rows[2],
                unique_id=rows[0],
                ids=rows[3],
                email=rows[4],
                first_name=rows[5] if len(rows) > 5 else None,
                last_name=rows[6] if len(rows) > 6 else None,
                phone_number=rows[7] if len(rows) > 7 else None,
            )

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
        
    def checkout(self, customer_id, shipping_fee=0.0):
        # We now take customer_id directly from the JWT, skipping finduser lookup
        cart_data = self.get_cart(customer_id)
        if not cart_data or cart_data["total_items"] == 0:
            return None
            
        order_items = []
        subtotal_dollars = 0
        for item in cart_data["cart"]:
            prod = item["product"]
            price_dollars = prod.get("priceCents", 0) / 100
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
        
        # We assume cart_id is the customer's unique_id for now since MOCK_CARTS maps by unique_id
        from model.order import Order
        new_order = Order(
            cart_id=customer_id, 
            customer_id=customer_id, 
            subtotal=subtotal, 
            shipping_fee=shipping_fee,
            items=items
        )
        
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
    

    def get_customer_orders(self, customer_id):
        all_orders = database.get_all_orders()
        customer_orders = []
        for o in all_orders:
            if o.get("user_id") == customer_id or o.get("customer_id") == customer_id:
                customer_orders.append(o)
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
        return database.update_order(order_id, {"status": new_status})
        
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
                address=rows[0],
                name=rows[1],
                unique_id=rows[2],
                phone_number=rows[5] if len(rows) > 5 else None,
            )
            vendor.email = rows[3]
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
            rating = self._calculate_product_rating(p_dict["id"])
            # Reconstruct Product object to return to frontend
            p = Product(
                product_name=p_dict["name"],
                vendor_id=p_dict["vendor_id"],
                price=p_dict.get("priceCents", 0),
                image_url=p_dict.get("image", ""),
                product_type=p_dict.get("type", ""),
                product_id=p_dict["id"],
                description=p_dict.get("description", ""),
                rating=rating
            )
            products.append(p)
        return products

    def findproduct(self, productid):
        productid = productid.strip().lower()
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
        # We store it in db using to_dict to match the mock storage format
        database.addproduct(new_product.to_dict())
        return new_product

    def update_product(self, vendor_id, product_id, updates):
        product = self.findproduct(product_id)
        if product is None or product.vendor_id != vendor_id:
            return None
            
        database.updateproduct(product_id, updates)
        return self.findproduct(product_id)

    def deleteproduct(self, productid, vendor_id):
        product = self.findproduct(productid)
        if product is None or product.vendor_id != vendor_id:
            return False
        
        return database.deleteproduct(productid)

    #address focus
