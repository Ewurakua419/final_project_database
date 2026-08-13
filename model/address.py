import uuid
class Address:
    def __init__(self,landmark,  postcode, city, street, house_num):
        self.id=str(uuid.uuid4())[:20]
        self.landmark=landmark
        self.postcode=postcode
        self.city=city
        self.street=street
        self.house_num=house_num

    def set_landmark(self, landmark):
        self.landmark=landmark

    def set_postcode(self, postcode):
        self.postcode=postcode

    def set_city(self, city):
        self.city=city

    def set_street(self, street):
        self.street=street

    def set_house_num(self, house_num):
        self.house_num=house_num

    def to_dict(self):
            return {
                "landmark":self.landmark,
                "post code": self.postcode,
                "city": self.city,
                "street": self.street,
                "house_num": self.house_num
            }

    