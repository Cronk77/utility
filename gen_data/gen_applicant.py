'''Creates Random Dummy Applicants Objects'''

import string
from datetime import datetime
import random as ran
from faker import Faker

faker = Faker()

class Applicant:
    '''Creates a Dummy Applicant'''

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        location = Applicant.get_dummy_location(self)
        self.address = location[0]
        self.city = location[1]
        self.state = location[2]
        self.zipcode = location[3]
        self.date_of_birth = Applicant.get_dummy_date_of_birth(self)
        self.gender = Applicant.get_dummy_gender(self)
        full_name = Applicant.get_dummy_name(self, self.gender)
        self.first_name = full_name[0]
        self.middle_name = full_name[1]
        self.last_name = full_name[2]
        self.email = Applicant.get_dummy_email(self, full_name[0], full_name[1], full_name[2])
        self.drivers_license = Applicant.get_divers_license(self)
        self.income = Applicant.get_dummy_income(self)
        self.phone = Applicant.get_dummy_phone(self)
        self.social_security = Applicant.get_dummy_ssn(self)
        self.applicant_id = None
        self.membership_id = None
        self.member_type = None
        self.applications = []
        self.user_name = None
        self.password = None
        self.authorization_token = None
        self.cards = []

    def get_dummy_location(self):
        '''Creates a dummy address, city, state, and zipcode'''
        address = faker.street_address()
        city = faker.city()
        state = faker.state()
        zipcode = faker.postalcode()
        loc_list = [address, city, state, zipcode]
        return loc_list

    def get_dummy_date_of_birth(self):
        '''Creates random date between the beginging of year 1900
        and 2004 bevause applicants have to be 18'''
        date = faker.date_between_dates(date_start=datetime(1900,1,1),\
        date_end=datetime(2004,1,1))# Must be 18
        return str(date)

    def get_dummy_gender(self):
        '''Produces random gender'''
        gender_list = ["MALE", "FEMALE", "OTHER", "UNSPECIFIED"]
        target_gender = gender_list[ran.randint(0,3)]
        return target_gender

    def get_dummy_name(self, gender):
        '''Takes the dummy generated gender and gets a full name'''
        first = ""
        middle = ""
        if gender == "MALE":
            first = faker.first_name_male()
            middle = faker.first_name_male()
        elif gender == "FEMALE":
            first = faker.first_name_female()
            middle = faker.first_name_female()
        else:
            first = faker.first_name_male()
            middle = faker.first_name_male()
        last = faker.last_name()
        full_name = [first, middle, last]
        return full_name

    def get_divers_license(self):
        '''Gets a rnadomly generated set of letters and numbers to place as
        a drivers license based on SSSSFFYYDDDNN ID format'''
        some_str = string.ascii_uppercase
        ssss = ''.join(ran.choice(some_str) for i in range(4))
        fff_yy_ddd_nn = str(ran.randint(1000000000, 9999999999))
        temp = ssss + fff_yy_ddd_nn
        return temp

    def get_dummy_email(self, first_name, middle_name, last_name):
        '''Generates a dummy random email'''
        email = first_name + middle_name[0] + last_name + '@gmail.com'
        return email

    def get_dummy_income(self):
        '''Creates a random income amount'''
        income = ran.randint(1500000, 10000000)
        return income

    def get_dummy_phone(self):
        '''Creates a random dummy phone number'''
        temp = []
        for _ in range(10):
            temp.append(str(ran.randint(0,9)))
        phone = temp[0] + temp[1] + temp[2] + "-" + temp[3] + temp[4] + temp[5] +\
            "-" + temp[6] + temp[7] + temp[8] + temp[9]
        return phone

    def get_dummy_ssn(self):
        '''Creates random dummy SSN'''
        ssn = faker.ssn()
        return ssn
    
    def set_applicant_id(self, incoming_applicant_id):
        '''Sets applicant_id'''
        self.applicant_id = incoming_applicant_id

    def set_membership_id(self, incoming_membership_id):
        '''Sets member_id'''
        self.membership_id = incoming_membership_id
    
    def set_application(self, incoming_application):
        '''Adds an application to this applicant'''
        self.applications.append(incoming_application)

    def set_member_type(self, incoming_member_type):
        '''sets role of applicant'''
        self.member_type = incoming_member_type

    def set_authorization_token(self, incoming_authorization_token):
        '''sets token for member'''
        self.authorization_token = incoming_authorization_token

    def set_password(self, incoming_password):
        '''sets members password'''
        self.password = incoming_password

    def set_user_name(self, incoming_user_name):
        '''sets members username'''
        self.user_name = incoming_user_name

    def set_card(self, incoming_card):
        '''Adds an application to this applicant'''
        self.cards.append(incoming_card)

def gen_applicants_by_amount(num):
    '''Given an int, This Module will create that many Applicants'''
    applicants = []
    for _ in range(num):
        new_app = Applicant()
        applicants.append(new_app)
    return applicants

def create_applicant_for_application(app):
    '''Creates a form that applications accepts from
        applicant information'''
    applicant = {
                "firstName": app.first_name,
                "middleName": app.middle_name,
                "lastName": app.last_name,
                "dateOfBirth": app.date_of_birth,
                "gender": app.gender,
                "email": app.email,
                "phone": app.phone,
                "socialSecurity": app.social_security,
                "driversLicense": app.drivers_license,
                "income": app.income,
                "address": app.address,
                "city": app.city,
                "state": app.state,
                "zipcode": app.zipcode,
                "mailingAddress": app.address,
                "mailingCity": app.city,
                "mailingState": app.state,
                "mailingZipcode": app.zipcode
                }
    return applicant
