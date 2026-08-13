import uuid
from datetime import datetime, timezone

class Order:
    def __init__(self, cart_id, customer_id, subtotal, shipping_fee, order_id=None, order_date=None, items=None):
        self.cart_id = cart_id
        self.customer_id = customer_id
        self.subtotal = float(subtotal)
        self.shipping_fee = float(shipping_fee)
        
        if order_id is None:
            self.order_id = "ord_" + uuid.uuid4().hex[:10]
        else:
            self.order_id = order_id
            
        if order_date is None:
            self.order_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            self.order_date = order_date
            
        self.items = items if items is not None else []
        
    def to_dict(self):
        tax = round(self.subtotal * 0.08, 2)
        grand_total = round(self.subtotal + tax + self.shipping_fee, 2)
        
        return {
            "order_id": self.order_id,
            "user_id": self.customer_id,
            "created_at": self.order_date,
            "status": "pending", # Mocked for now
            "pricing_summary": {
                "subtotal": self.subtotal,
                "tax": tax,
                "shipping": self.shipping_fee,
                "grand_total": grand_total
            },
            "items": self.items,
            "shipping_address": {
                "id": "addr_1",
                "street": "123 Default Street",
                "city": "Default City",
                "state": "DC",
                "zip": "10000"
            },
            "payment_details": {
                "last_four": "4242",
                "brand": "Visa"
            }
        }
