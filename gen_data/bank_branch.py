import sys
import os
import json
import random as ran
import logging
import datetime
import requests
from faker import Faker
from dotenv import load_dotenv
import user

load_dotenv()
BANK_BRANCH_URL = os.getenv('BANK_BRANCH_URL')
LOG_LOCATION = os.getenv('LOG_LOCATION')

DATE_TIME = datetime.datetime.now()

# pylint: disable=logging-fstring-interpolation
# pylint: disable=bare-except
# pylint: disable=no-member
# pylint: disable=redefined-outer-name

if LOG_LOCATION == "":
    try:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    except:
        print("gen_bank_branch:Logging: could not print to sys.stout")
else:
    try:
        logging.basicConfig(filename=LOG_LOCATION, level=logging.INFO)
    except:
        print(f"gen_bank_branch:Logging: {LOG_LOCATION} is not a valid PATH")

faker = Faker()

# USED BECAUSE THE POST RESPONSE  for /branches is an infinite loop
BRANCH_INFO = ""

def get_bank_template():
    '''Creates a dictionary of bank info for requests'''
    routing_num = str(ran.randint(100000000, 999999999))
    bank = {
        "routingNumber": routing_num,
        "address": faker.street_address(),
        "city": faker.city(),
        "state": faker.state(),
        "zipcode": faker.postalcode()
    }
    return bank

def get_branch_template(bank_id=None):
    '''Creates a dictionary of branch info for requests'''
    if bank_id is None:
        bank_id = 1
    temp = []
    for _ in range(10):
        temp.append(str(ran.randint(0,9)))
    phone = temp[0] + temp[1] + temp[2] + "-" + temp[3] + temp[4] + temp[5] +\
        "-" + temp[6] + temp[7] + temp[8] + temp[9]
    branch = {
        "name": faker.company(),
        "address": faker.street_address(),
        "city": faker.city(),
        "state": faker.state(),
        "zipcode": faker.postalcode(),
        "phone": phone,
        "bankID": bank_id
    }
    return branch

def gen_bank(authorization_token, bank):
    '''Takes/creates a bank dict and sends post request'''
    json_string = json.dumps(bank)
    logging.info(f"{DATE_TIME}: Bank Creation")
    response = ""
    try:
        response = requests.post(
                url = f"{BANK_BRANCH_URL}/banks",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json',
                    'Authorization': f'{authorization_token}'
                },
                timeout=5
        )
    except requests.Timeout:
        resp = "Request has timed out"
    except requests.RequestException:
        response = "Request Failed"
    except:
        response = "CODE ERROR"
    if str(response) == "<Response [201]>":
        bank_info = json.loads(response.text) 
        logging.info(f"{DATE_TIME}: Application ACCEPTED\n{response}\n{bank_info}")
    else:
        logging.info(f"{DATE_TIME}: Application NOT ACCEPTED:{response}")
    return response

def gen_branch(authorization_token, branch):
    '''Takes/creates a branch dict and sends post request'''
    # pylint: disable=invalid-name
    global BRANCH_INFO
    BRANCH_INFO = branch
    json_string = json.dumps(branch)
    logging.info(f"{DATE_TIME}: Branch Creation:")
    try:
        response = requests.post(
            f"{BANK_BRANCH_URL}/branches",
            data = json_string,
            headers={
                'accept': '*/*',
                'content-type': 'application/json',
                'Authorization': f'{authorization_token}'
            },
            timeout=5
        )
    # Problem with infinite recursion when looking at
    #    the result of response_info = json.loads(response.text)
    except requests.Timeout:
        response = "Request has timed out"
    except requests.RequestException:
        response = "Request Failed"
    except:
        response = "CODE ERROR"
    if str(response) == "<Response [201]>":
        logging.info(f"{DATE_TIME}: Application ACCEPTED\n{response}\n{BRANCH_INFO}")
    else:
        logging.info(f"{DATE_TIME}: Application NOT ACCEPTED:{response}")
    return BRANCH_INFO