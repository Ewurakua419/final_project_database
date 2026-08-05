import uuid
class Payment:
    def __init_(self):
        self.id=str(uuid.uuid4())

class Momo(Payment):
    def __init_(self, phone, acc_name,network):
        super().__init__() 
        self.phone=phone
        self.acc_name=acc_name
        self.network=network


class Card(Payment):
    def __init_(self,cvv, card_num,  expiry):
        super().__init_()
        self.cvv=cvv
        self.card_num=card_num
        self.expiry=expiry


class Bank_T(Payment):
    def __init_(self, acc_name, acc_num, bank_name):
        super().__init_()
        self.acc_name=acc_name
        self.acc_num=acc_num
        self.bank_name=bank_name
        