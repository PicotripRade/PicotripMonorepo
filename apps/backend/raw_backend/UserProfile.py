class User:

    def __init__(self,
                 time_stamp='999999999999',
                 guest=True,
                 first_name='Ivo',
                 last_name='Ivanovic',
                 attribute1=None,
                 attribute2=None,
                 attribute3=None,
                 email='ivo.ivanovic1988@gmail.com',
                 address='Mraovica sokace 4/9',
                 phone='+381658095637',
                 card_number='4054770075078795',
                 expiration_date='03/26',
                 cvc='683',
                 gender='male',
                 card_holder_name='ivo ivanovic',
                 travel_maker=True
                 ):
        if guest is True:
            self.first_name = None
            self.last_name = None
            self.attribute1 = None
            self.attribute2 = None
            self.attribute3 = None
            self.email = None
            self.address = None
            self.phone = None
            self.card_number = None
            self.expiration_date = None
            self.cvc = None
            self.gender = None
            self.card_holder_name = None
        else:
            self.guest = guest
            self.first_name = first_name
            self.last_name = last_name
            self.attribute1 = attribute1
            self.attribute2 = attribute2
            self.attribute3 = attribute3
            self.email = email
            self.address = address
            self.phone = phone
            self.card_number = card_number
            self.expiration_date = expiration_date
            self.cvc = cvc
            self.gender = gender
            self.card_holder_name = card_holder_name
            self.travel_maker = travel_maker
        self.time_stamp = time_stamp