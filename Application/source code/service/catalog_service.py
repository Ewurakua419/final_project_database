import database
from model.product import Product
from model.review import Review
from service.exceptions import ProductNotFoundError, ReviewValidationError

class CatalogService:
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
            p = Product(
                product_name=p_dict["product_name"],
                vendor_id=p_dict["vendor_id"],
                price=p_dict.get("price", 0),
                image_url=p_dict.get("image_url", ""),
                product_type=p_dict.get("product_type", ""),
                product_id=p_dict["product_id"],
                description=p_dict.get("description", ""),
                rating=rating,
                stock_quantity=p_dict.get("stock_quantity", 0)
            )
            if p.product_type == "fashion":
                p.fashion_attributes = database.find_fashion_attributes(p.product_id)
            elif p.product_type == "beauty":
                p.beauty_attributes = database.find_beauty_attributes(p.product_id)
            products.append(p)
        return products

    def findproduct(self, productid):
        productid = productid.strip()
        rows = database.findproduct(productid)
        if rows is None:
            raise ProductNotFoundError("Product not found")
            
        rating = self._calculate_product_rating(rows[0])
        product = Product(
            product_id=rows[0],
            vendor_id=rows[1],
            product_name=rows[2],
            price=rows[3],
            image_url=rows[4],
            product_type=rows[5],
            description=rows[6],
            rating=rating,
            stock_quantity=rows[7] if len(rows) > 7 else 0
        )
        if product.product_type == "fashion":
            product.fashion_attributes = database.find_fashion_attributes(product.product_id)
        elif product.product_type == "beauty":
            product.beauty_attributes = database.find_beauty_attributes(product.product_id)
        return product

    def get_product_reviews(self, product_id):
        reviews_data = database.get_reviews_by_product(product_id)
        reviews = []
        for r in reviews_data:
            customer_name = "Anonymous"
            # Query customer name safely
            cust_rows = database.searchcustomer_by_id(r["customer_id"])
            if cust_rows:
                customer_name = f"{cust_rows[1]} {cust_rows[2]}".strip()
                
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
        if rating < 1 or rating > 5:
            raise ReviewValidationError("Rating must be between 1 and 5 stars")
            
        review = Review(
            product_id=product_id,
            customer_id=customer_id,
            comment=comment,
            rating=rating
        )
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
