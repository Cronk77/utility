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
import application
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

def create_user(applicant, role):
    logging.info(f"{DATE_TIME}: user: User Creation")
    password = generate_password()
    user_name = generate_user_name(applicant)
    applicant.set_user_name(user_name)
    applicant.set_password(password)
    user = {
        "username": user_name,
        "password": password,
        "role": role,
        "firstName": applicant.first_name,
        "lastName": applicant.last_name,
        "email": applicant.email,
        "phone": applicant.phone,
        'membershipId': applicant.membership_id,
        'lastFourOfSSN': applicant.social_security[7:]
    }
    return user

def register_user(user):
    logging.info(f"{DATE_TIME}: user: Register User")
    json_string = json.dumps(user)
    try:
        response = requests.post(
                url = f"{USER_URL}/users/registration",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json'
                },
                timeout=5
        )
    except requests.Timeout:
        response = "Request has timed out"
    except requests.RequestException:
        response = "Request Failed"
    except:
        response = "CODE ERROR"

    if str(response) == "<Response [201]>":
        application_info = json.loads(response.text) 
        logging.info(f"{DATE_TIME}: User Registration ACCEPTED\n{response}\n{application_info}")
    else:
        logging.info(f"{DATE_TIME}: User Registration NOT ACCEPTED: {response}")
    return response

def confirm_user(token):
    logging.info(f"{DATE_TIME}: user: Confirm User")
    confirmation_token = {'token' : token}
    json_string = json.dumps(confirmation_token)
    try:
        response = requests.post(
                url = f"{USER_URL}/users/confirmation",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json'
                },
                timeout=5
        )
    except requests.Timeout:
        response = "Request has timed out"
    except requests.RequestException:
        response = "Request Failed"
    except:
        response = "CODE ERROR"
    if str(response) == "<Response [200]>":
        confirmation_info = json.loads(response.text) 
        logging.info(f"{DATE_TIME}: User Confirmation ACCEPTED\n{response}\n{confirmation_info}")
    else:
        logging.info(f"{DATE_TIME}: User Confirmation NOT ACCEPTED: {response}")
    return response

def user_sign_in(applicant):
    '''Takes username and password of Admin
        and signs in'''
    login_template = {
        'username': applicant.user_name,
        'password': applicant.password
    }
    json_string = json.dumps(login_template)
    try:
        response = requests.post(
                url = f"{USER_URL}/login",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json'
                },
                timeout=5
            )
    except requests.Timeout:
        response = "Request has timed out"
    except requests.RequestException:
        response = "Request Failed"
    except:
        response = "CODE ERROR"
    if str(response) == "<Response [200]>":
        logging.info(f"{DATE_TIME}: gen_user: User: {applicant.user_name} is Logged in.")
        authorization_token = response.headers.get('Authorization')
        applicant.set_authorization_token(authorization_token)
    else:
        logging.info(f"{DATE_TIME}: gen_user: User : {applicant.user_name} was NOT logged in.")
    return response