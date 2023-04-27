import gen_applicant
import gen_applications
import gen_user
import re
import json

def test_create_users():
    user_list, _ = gen_user.create_users(1, "member")
    assert isinstance(user_list, list)
    assert isinstance(user_list[0].get('username'), str)
    assert isinstance(user_list[0].get('password'), str)
    assert isinstance(user_list[0].get('firstName'), str)
    assert isinstance(user_list[0].get('lastName'), str)
    assert isinstance(user_list[0].get('email'), str)
    assert isinstance(user_list[0].get('phone'), str)
    assert isinstance(user_list[0].get('membershipId'), int)
    assert isinstance(user_list[0].get('lastFourOfSSN'), str)
    assert len(user_list[0].get('lastFourOfSSN')) == 4

def test_gen_password():
    password = gen_user.generate_password()
    res = False
    pattern = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$")
    if re.match(pattern, password):
        res = True
    assert res == True

def test_generate_user_name():
    applicants = gen_applicant.gen_applicants_by_amount(1)
    user_name = gen_user.generate_user_name(applicants[0])
    assert len(user_name) <= 20
    assert len(user_name) >= 6
    res = False
    pattern = re.compile("^[a-zA-Z0-9_.-]*$")
    if re.match(pattern, user_name):
        res = True
    assert res == True

def test_register_users():
    user_list, _ = gen_user.create_users(1, 'member')
    info_list, response_codes, new_users = gen_user.register_users(user_list)
    result = all(str(code) == "<Response [201]>" for code in response_codes)
    assert result == True

def test_login():
    user_list, _ = gen_user.create_users(1, 'admin')
    _, _, update_users = gen_user.register_users(user_list)
    user_name = update_users[0].get('username')
    password = update_users[0].get('password')
    resp, authorization_token = gen_user.login(user_name, password)
    assert  str(resp) == "<Response [200]>"
    assert authorization_token != None