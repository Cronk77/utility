'''Signs into admin user, generates banks and branches'''
import sys
import os
import json
import random as ran
import logging
import datetime
import requests
from faker import Faker
from dotenv import load_dotenv
from gen_user import create_users, register_users, login

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

def gen_authorization_token(updated_users=None):
    '''Create Admin and login to get JWT
        (authorization_token)'''
    if updated_users is None:
        user_list, _ = create_users(num=1, user_role='admin')
        _, _, updated_users = register_users(user_list)
    user_name = updated_users[0].get('username')
    password = updated_users[0].get('password')
    _, authorization_token = login(user_name, password)
    return authorization_token

def get_bank():
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

def get_branch(bank_id=None):
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

def gen_bank(authorization_token=None, bank=None):
    '''Takes/creates a bank dict and sends post request'''
    if authorization_token is None:
        authorization_token = gen_authorization_token()
    if bank is None:
        bank = get_bank()
    json_string = json.dumps(bank)
    logging.info(f"{DATE_TIME}: Bank Creation")
    try:
        resp = requests.post(
                url = f"{BANK_BRANCH_URL}/banks",
                data = json_string,
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
        resp_info = "EMPTY"
    except requests.RequestException:
        resp = "Request Failed"
        resp_info = "EMPTY"
    logging.info(f"{DATE_TIME}: {str(resp)}")
    logging.info(f"{DATE_TIME}: {str(resp_info)}")

    return resp, resp_info

def gen_banks(authorization_token=None, num=None):
    '''Generates number(num) of banks'''
    if authorization_token is None:
        authorization_token = gen_authorization_token()
    if num is None:
        num = 1
    banks = []
    for _ in range(num):
        _, bank_info = gen_bank(authorization_token)
        banks.append(bank_info)
    return banks

def gen_branch(authorization_token=None, bank_id=None, branch=None):
    '''Takes/creates a branch dict and sends post request'''
    # pylint: disable=invalid-name
    if authorization_token is None:
        authorization_token = gen_authorization_token()
    if bank_id is None:
        bank_id = 1
    if branch is None:
        branch = get_branch(bank_id)
    BRANCH_INFO = branch
    json_string = json.dumps(branch)
    logging.info(f"{DATE_TIME}: Branch Creation:")
    try:
        resp = requests.post(
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
    #    the result of resp_info = json.loads(resp.text)
    except requests.Timeout:
        resp = "Request has timed out"
    except requests.RequestException:
        resp = "Request Failed"
    logging.info(f"{DATE_TIME}: {str(resp)}")
    logging.info(f"{DATE_TIME}: {str(BRANCH_INFO)}")
    return resp, BRANCH_INFO

def gen_branches(authorization_token=None, bank_id=None, num=None):
    '''Generates number(num) of branches'''
    if authorization_token is None:
        authorization_token = gen_authorization_token()
    if bank_id is None:
        bank_id = 1
    if num is None:
        num = 1
    branches = []
    for _ in range(num):
        _, branch_info = gen_branch(authorization_token, bank_id)
        branches.append(branch_info)
    return branches

def main(argv):
    '''driver code to sign in as Admin and create Bank/Branch.'''
    '''Driver for gen user
        defualt: 1 bank / 1 branch
        2 args : # bank / 1 branch
        3 args : # bank / # branch
        >3 args: exit program
    '''
    bank_num = ""
    branch_num = ""
    if len(argv) == 1:
        bank_num = 1
        branch_num = 1
    elif len(argv) == 2:
        bank_num = int(argv[1])
        branch_num = 1
    elif len(argv) == 3:
        bank_num = int(argv[1])
        branch_num = int(argv[2])
    else:
        logging.info(f"{DATE_TIME}: gen_bank_branch: Too many arguments given")
        sys.exit()
    if bank_num == 0:
        logging.info(f"{DATE_TIME}: gen_bank_branch: Cannot have 0 banks")
        sys.exit()

    authorization_token = gen_authorization_token()
    banks = gen_banks(authorization_token=authorization_token, num=bank_num)
    for bank in banks:
        bank_id = bank.get("id")
        _ = gen_branches(authorization_token=authorization_token, bank_id=bank_id, num=branch_num)

if __name__ == "__main__":
    main(sys.argv)
