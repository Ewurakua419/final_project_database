import uuid
from datetime import datetime, timedelta

class Delivery:
    def __init__(self, order_id, delivery_status="on the way", estimated_delivery_date=None, address_id=None, shipping_id=None, delivery_id=None):
        self.delivery_id = delivery_id or str(uuid.uuid4())[:6]
        self.order_id = order_id
        
        # Validate status against SQL check constraint: ('delivered', 'sent to port', 'on the way')
        valid_statuses = {"delivered", "sent to port", "on the way"}
        status_lower = delivery_status.lower()
        self.delivery_status = status_lower if status_lower in valid_statuses else "on the way"
        
        # Set default estimated delivery date to 5 days from now
        if estimated_delivery_date is None:
            self.estimated_delivery_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        else:
            self.estimated_delivery_date = estimated_delivery_date
            
        self.address_id = address_id
        self.shipping_id = shipping_id

    def to_dict(self):
        return {
            "delivery_id": self.delivery_id,
            "order_id": self.order_id,
            "delivery_status": self.delivery_status,
            "estimated_delivery_date": self.estimated_delivery_date,
            "address_id": self.address_id,
            "shipping_id": self.shipping_id
        }