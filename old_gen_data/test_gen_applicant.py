from gen_applicant import Applicant
from gen_applicant import gen_applicants_by_amount, create_applicant_for_application

def test_Applicant():
    new_applicant = Applicant()
    assert isinstance(new_applicant, Applicant)
    assert isinstance(new_applicant.address, str)
    assert isinstance(new_applicant.city, str)
    assert isinstance(new_applicant.state, str)
    assert isinstance(new_applicant.zipcode, str)
    assert isinstance(new_applicant.date_of_birth, str)
    assert isinstance(new_applicant.gender, str)
    assert isinstance(new_applicant.first_name, str)
    assert isinstance(new_applicant.middle_name, str)
    assert isinstance(new_applicant.last_name, str)
    assert isinstance(new_applicant.email, str)
    assert isinstance(new_applicant.drivers_license, str)
    assert isinstance(new_applicant.income, int)
    assert isinstance(new_applicant.phone, str)
    assert isinstance(new_applicant.social_security, str)

def test_get_dummy_loaction():
    location = Applicant.get_dummy_location(self=None)
    assert len(location) == 4
    assert str(type(location)) == "<class 'list'>"

def test_get_dummy_date_of_birth():
    date = Applicant.get_dummy_date_of_birth(self=None)
    assert  isinstance(int(date[0:4]), int)
    assert date[4] == "-"
    assert isinstance(int(date[5:7]), int)
    assert date[7] == "-"
    assert isinstance(int(date[8:10]), int)

def test_get_dummy_gender():
    gender_list = ["MALE", "FEMALE", "OTHER", "UNSPECIFIED"]
    gender = Applicant.get_dummy_gender(self=None)
    assert gender in gender_list

def test_get_dummy_name():
    full_name = Applicant.get_dummy_name(self=None, gender = "FEMALE")
    assert len(full_name) == 3
    assert str(type(full_name)) == "<class 'list'>"

def test_get_drivers_license():
    dl = Applicant.get_divers_license(self=None)
    assert len(dl) == 14
    assert isinstance(dl[0:4], str)
    assert isinstance(int(dl[4:14]), int)
    assert int(dl[4:14]) >= 1000000000
    assert int(dl[4:14]) <= 9999999999

def test_get_dummy_email():
    email = Applicant.get_dummy_email(self=None, first_name="first", \
        middle_name="middle", last_name="last")
    assert "@" in email
    assert "." in email

def test_get_dummy_income():
    income = Applicant.get_dummy_income(self=None)
    assert income >= 1500000
    assert income <= 10000000

def test_get_dummy_phone():
    phone = Applicant.get_dummy_phone(self=None)
    assert  isinstance(int(phone[0:3]), int)
    assert phone[3] == "-"
    assert isinstance(int(phone[4:7]), int)
    assert phone[7] == "-"
    assert isinstance(int(phone[8:12]), int)

def test_get_dummy_ssn():
    ssn = Applicant.get_dummy_ssn(self=None)
    assert  isinstance(int(ssn[0:3]), int)
    assert ssn[3] == "-"
    assert isinstance(int(ssn[4:6]), int)
    assert ssn[6] == "-"
    assert isinstance(int(ssn[7:11]), int)

def test_gen_applicants_by_amount():
    applicants = gen_applicants_by_amount(10)
    assert len(applicants) == 10
    assert str(type(applicants)) == "<class 'list'>"

def test_create_applicant_for_application():
    app = Applicant()
    applicant_dict = create_applicant_for_application(app)
    assert isinstance(applicant_dict.get('firstName'), str)
    assert isinstance(applicant_dict.get('middleName'), str)
    assert isinstance(applicant_dict.get('lastName'), str)
    assert isinstance(applicant_dict.get('dateOfBirth'), str)
    assert isinstance(applicant_dict.get('gender'), str)
    assert isinstance(applicant_dict.get('email'), str)
    assert isinstance(applicant_dict.get('phone'), str)
    assert isinstance(applicant_dict.get('socialSecurity'), str)
    assert isinstance(applicant_dict.get('driversLicense'), str)
    assert isinstance(applicant_dict.get('income'), int)
    assert isinstance(applicant_dict.get('address'), str)
    assert isinstance(applicant_dict.get('city'), str)
    assert isinstance(applicant_dict.get('state'), str)
    assert isinstance(applicant_dict.get('zipcode'), str)
    assert isinstance(applicant_dict.get('mailingAddress'), str)
    assert isinstance(applicant_dict.get('mailingState'), str)
    assert isinstance(applicant_dict.get('mailingZipcode'), str)