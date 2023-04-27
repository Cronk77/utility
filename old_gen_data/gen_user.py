##### To run Program, you must give an int argument
##### for number of members and admins that should be registered
'''Creates and register a user using aline-user-microservice'''
import sys
import os
import json
import logging
import datetime
import requests
from password_generator import PasswordGenerator
from dotenv import load_dotenv
import gen_applications
import gen_applicant

load_dotenv()
USER_URL = os.getenv('USER_URL')
LOG_LOCATION = os.getenv('LOG_LOCATION')

DATE_TIME = datetime.datetime.now()

# pylint: disable=logging-fstring-interpolation
# pylint: disable=bare-except
if LOG_LOCATION == "":
    try:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    except:
        print("gen_user:Logging: could not print to sys.stout")
else:
    try:
        logging.basicConfig(filename=LOG_LOCATION, level=logging.INFO)
    except:
        print(f"gen_user:Logging: {LOG_LOCATION} is not a valid PATH")


pwo = PasswordGenerator()

def generate_password():
    '''Create a password based on API
        Validation Standards'''
    pwo.minlen = 8
    pwo.maxlen = 30
    pwo.minuchars = 1
    pwo.minlchars = 1
    pwo.minnumbers = 1
    pwo.minschars = 1
    pwo.excludeschars = "#^()-_=+|\\~`,.<>/\""
    password = pwo.generate()
    return password

def generate_user_name(applicant):
    '''Generates a user_name and helps to validate size
        of user_name between 6 and 20 characters'''
    user_name = applicant.first_name + "." + applicant.middle_name[0] + "." + applicant.last_name
    while len(user_name) < 6:
        user_name += 1
    if len(user_name) > 20:
        user_name = user_name[:20]
    return user_name

def create_users(num=None, user_role=None, applicants=None, app_type=None):
    '''Takes the num as number of users to create
        And returns a list of users.
        user_role can be 'member', 'employee',
        or 'admin'
    '''
    # pylint: disable-msg=too-many-locals
    if num is None:
        num = 1
    if user_role is None:
        user_role = 'member'
    if applicants is None:
        applicants = gen_applicant.gen_applicants_by_amount(num)
    print("CREATE_USER: " + str(app_type))############################################################################################
    applications, _ = gen_applications.get_applications(applicants, app_type=app_type)
    info_list, response_codes = gen_applications.post_requests(applications, gen_applications.hit_api_applications)
    print("HERE1")
    print(info_list)
    user_list = []
    for i, _ in enumerate(response_codes):
        # Checks each code to make sure its 201 and if not gets a replacment
        while str(response_codes[i]) != "<Response [201]>":
            print("HERE2")
            new_applicant = gen_applicant.gen_applicants_by_amount(1)
            new_application, _ = gen_applications.get_applications(new_applicant, app_type=app_type)
            new_info, new_code = gen_applications.post_requests(new_application, gen_applications.hit_api_applications)
            applicants[i] = new_applicant[0]
            applications[i] = new_application[0]
            response_codes[i] = new_code[0]
            info_list[i] = new_info[0]

        password = generate_password()
        user_name = generate_user_name(applicants[i])
        user = {
            "username": user_name,
            "password": password,
            "role": user_role,
            "firstName": applicants[i].first_name,
            "lastName": applicants[i].last_name,
            "email": applicants[i].email,
            "phone": applicants[i].phone,
            'membershipId': int(info_list[i].get('createdMembers')[0].get('membershipId')),
            'lastFourOfSSN': info_list[i].get('applicants')[0].get('socialSecurity')[7:]
        }
        user_list.append(user)
    print("HERE 3")
    return user_list, info_list


def hit_api_registration(json_string, token=None):
    '''Method for posting user/registration by
        sending a post request(ensure correct port
        if changed)'''
    try:
        resp = requests.post(
                url = f"{USER_URL}/users/registration",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json'
                },
                timeout=5
            )
    except requests.Timeout:
        resp = "Request has timed out"
    except requests.RequestException:
        resp = "Request Failed"
    logging.info(f"{DATE_TIME}: gen_user: User Registration")
    return resp

def hit_api_confirmation(json_string, token=None):
    '''Method for posting user/registration by
        sending a post request(ensure correct port
        if changed)'''
    try:
        resp = requests.post(
                url = f"{USER_URL}/users/confirmation",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json'
                },
                timeout=5
            )
    except requests.Timeout:
        resp = "Request has timed out"
    except requests.RequestException:
        resp = "Request Failed"
    logging.info(f"{DATE_TIME}: gen_user: User Confirmation")
    return resp

def register_users(user_list):
    '''Registers a list of User by posting
        to aline-user-microservice API'''
    info_list, response_codes = gen_applications.post_requests(user_list, hit_api_registration)
    # Checks each code to make sure its 201 and if not gets a new user to replace
    for i, _ in enumerate(response_codes):
        while str(response_codes[i]) != "<Response [201]>":
            logging.info(f"{DATE_TIME}: gen_user: REATTEMPT User Creation")
            new_user, _ = create_users(1, user_list[i].get('role'))
            new_info, new_code = gen_applications.post_requests(new_user, hit_api_registration)
            user_list[i] = new_user[0]
            response_codes[i] = new_code[0]
            info_list[i] = new_info[0]
        password = user_list[i].get('password')
        logging.info(f"{DATE_TIME}: gen_user: User password: {password}")
    return info_list, response_codes, user_list

def user_creation_confirmation(info_list):
    '''Once a User has been registered, This Method
        uses /users/confirmation to confirm user is
        registered. The input_tokens can be found printed
        in the console'''
    tokens = []
    for info in info_list:
        input_token = input(f"Enter Token for {info.get('username')}: ")
        token = {'token' : input_token}
        tokens.append(token)
    info_list, response_codes = gen_applications.post_requests(tokens, hit_api_confirmation)
    return info_list, response_codes

def login(user_name, password):
    '''Takes username and password of Admin
        and signs in'''
    login_dict = {
        'username': user_name,
        'password': password
    }
    json_string = json.dumps(login_dict)
    try:
        resp = requests.post(
                f"{USER_URL}/login",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json'
                },
                timeout=5
            )
    except requests.Timeout:
        resp = "Request has timed out"
    except requests.RequestException:
        resp = "Request Failed"
    if str(resp) == "<Response [200]>":
        logging.info(f"{DATE_TIME}: gen_user: User: {user_name} is Logged in.")
    else:
        logging.info(f"{DATE_TIME}: gen_user: User : {user_name} was NOT logged in.")
    authorization_token = resp.headers.get('Authorization')
    #logging.info(f"{DATE_TIME}: gen_user: auth_token : {authorization_token}")
    return resp, authorization_token

def get_user_profile(authorization_token, user_id=None):
    target_url = ""
    if user_id is None:
        target_url = f"{USER_URL}/users/current/profile"
    else:
        target_url = f"{USER_URL}/users/{user_id}/profile"
    resp_info = ""
    try:
        resp = requests.get(
                url=target_url,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json',
                    'Authorization': f'{authorization_token}'
                },
                timeout=5
            )
        resp_info = json.loads(resp.text)
    except requests.Timeout:
        resp = "Request has timed out"
    except requests.RequestException:
        resp = "Request Failed"
    if str(resp) == "<Response [200]>":
        logging.info(f"{DATE_TIME}: gen_user: getting user information: {resp_info.get('username')}")
    else:
        logging.info(f"{DATE_TIME}: gen_user: getting user: failed to get user information.")
    return resp, resp_info

def main(argv):
    '''Driver for gen user
        defualt: 1 member / 0 admin
        2 args : # member / 0 admin
        3 args : # member / # admin
        >3 args: exit program
    '''
    app_types = ["CHECKING", "SAVINGS", "CHECKING_AND_SAVINGS", "CREDIT_CARD", "LOAN"]
    user_num = ""
    admin_num = ""
    app_type = None
    if len(argv) == 1:
        user_num = 1
        admin_num = 0
    elif len(argv) == 2:
        user_num = int(argv[1])
        admin_num = 0
    elif len(argv) == 3:
        user_num = int(argv[1])
        admin_num = int(argv[2])
    elif len(argv) == 4:
        user_num = int(argv[1])
        admin_num = int(argv[2])
        if argv[3].upper() not in app_types:
            logging.info(f"{DATE_TIME}: gen_user: given application type not known.")
            sys.exit()
        app_type = argv[3].upper()
    elif len(argv) > 4:
        logging.info(f"{DATE_TIME}: gen_user: Too many arguments given")
        print("gen_user: Too many arguments given")
        sys.exit()
    else:
        user_num = int(argv[1])
        admin_num = int(argv[2])

    if user_num > 0:
        user_list, _ = create_users(user_num, "member", app_type=app_type)
        #_, _, _ = register_users(user_list)
        # Can confirm user creation by un commenting line and going into
        # UserConfirmationService.java and uncomment line that prints token
        info_list, _, _ = register_users(user_list)
        _, _ = user_creation_confirmation(info_list)

    if admin_num > 0:
        user_list, _ = create_users(admin_num, 'admin', app_type=app_type)
        _, _, _ = register_users(user_list)
        
if __name__ == "__main__":
    main(sys.argv)
