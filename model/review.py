import uuid
from datetime import datetime, timezone

class Review:
    def __init__(self, product_id, customer_id, comment, rating, review_id=None, review_date=None):
        self.product_id = product_id
        self.customer_id = customer_id
        self.comment = comment
        self.rating = int(rating)
        
        if review_id is None:
            self.review_id = str(uuid.uuid4())
        else:
            self.review_id = review_id
            
        if review_date is None:
            self.review_date = datetime.now(timezone.utc).isoformat() + "Z"
        else:
            self.review_date = review_date

    def to_dict(self):
        # We also need to map the output format to what the frontend expects
        # The frontend previously expected: id, product_id, name, rating, text, created_at
        return {
            "id": self.review_id,
            "product_id": self.product_id,
            "name": self.customer_id, # Frontend shows the name, but we use ID here for now
            "rating": self.rating,
            "text": self.comment,
            "created_at": self.review_date
        }
