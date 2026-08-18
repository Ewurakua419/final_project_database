import database
import auth
from model.vendor import Vendor
from model.product import Product
from service.exceptions import UserNotFoundError, InvalidCredentialsError, AccountSuspendedError, ProductNotFoundError, MarketplaceException

class VendorService:
    def findvendor(self, email):
        email = email.strip().lower()
        rows = database.searchvendor(email)
        if rows is None:
            raise UserNotFoundError("Vendor not found")
            
        vendor = Vendor(
            name=rows[1],
            address="",
            unique_id=rows[0],
            phone_number=rows[3],
        )
        vendor.email = rows[2]
        vendor.password = rows[4]
        vendor.is_active = rows[5]
        return vendor

    def register(self, name, password, email, address, phone_number=None):
        if database.searchvendor(email) is not None:
            return None # Facade handles vendor exists check
            
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
        return vendor

    def login(self, email, password):
        vendor = self.findvendor(email)
        if not auth.decodere(password, vendor.password):
            raise InvalidCredentialsError("Wrong password")
        if not vendor.is_active:
            raise AccountSuspendedError("Vendor account is suspended")
        return vendor

    def get_vendor_stats(self, vendor_id):
        return database.get_vendor_dashboard_stats(vendor_id)

    def get_vendor_orders(self, vendor_id, finduser_by_id_helper):
        all_orders = database.get_all_orders()
        vendor_orders = []
        
        for order in all_orders:
            vendor_items = []
            vendor_subtotal = 0
            
            for item in order.get("items", []):
                product_id = item.get("product_id")
                if not product_id:
                    continue
                rows = database.findproduct(product_id)
                if rows and rows[1] == vendor_id:
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
                    try:
                        customer = finduser_by_id_helper(cid)
                        if customer:
                            order_copy["customer_first_name"] = customer.first_name
                            order_copy["customer_last_name"] = customer.last_name
                            order_copy["customer_email"] = customer.email
                            order_copy["customer_phone"] = customer.phone_number
                    except Exception:
                        pass
                        
                vendor_orders.append(order_copy)
                
        return vendor_orders

    def add_product(self, vendor_id, product_data):
        new_product = Product(
            product_name=product_data.get("name"),
            vendor_id=vendor_id,
            price=product_data.get("price", product_data.get("priceCents", 0)),
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
        rows = database.findproduct(product_id)
        if rows is None or rows[1] != vendor_id:
            raise ProductNotFoundError("Product not found or access denied")
            
        db_updates = {}
        if "name" in updates: db_updates["product_name"] = updates["name"]
        if "price" in updates: db_updates["price"] = updates["price"]
        elif "priceCents" in updates: db_updates["price"] = updates["priceCents"]
        if "image" in updates: db_updates["image_url"] = updates["image"]
        if "type" in updates:
            if updates["type"] != rows[5]:
                raise MarketplaceException("Product category/type cannot be changed after creation.")
            db_updates["product_type"] = updates["type"]
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

        return True

    def delete_product(self, productid, vendor_id):
        rows = database.findproduct(productid)
        if rows is None or rows[1] != vendor_id:
            return False
        return database.deleteproduct(productid)
