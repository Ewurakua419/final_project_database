import uuid
from datetime import datetime, timezone

class Order:
    def __init__(self, cart_id, customer_id, subtotal, shipping_fee, order_id=None, order_date=None, items=None, shipping_address=None, payment_details=None):
        self.cart_id = cart_id
        self.customer_id = customer_id
        self.subtotal = float(subtotal)
        self.shipping_fee = float(shipping_fee)
        self.shipping_address = shipping_address
        self.payment_details = payment_details
        
        if order_id is None:
            self.order_id = str(uuid.uuid4())[:6]
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
            "status": "pending",
            "pricing_summary": {
                "subtotal": self.subtotal,
                "tax": tax,
                "shipping": self.shipping_fee,
                "grand_total": grand_total
            },
            "items": self.items,
            "shipping_address": self.shipping_address,
            "payment_details": self.payment_details
        }
