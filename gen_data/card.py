import sys
import os
import json
import logging
import datetime
import requests
from dotenv import load_dotenv
import gen_applicant
import application
import user

load_dotenv()
CARD_URL = os.getenv('CARD_URL')
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

class Card:
    def __init__(self, card_type, card_number, security_code, exp_date):
        self.card_type = card_type
        self.card_number = card_number
        self.security_code = security_code
        self.exp_date = exp_date

def create_card_template(card_num, sec_code, exp_date, dob, l_ssn):
    card = {
            "cardNumber": card_num,
            "securityCode": sec_code,
            "expirationDate": exp_date,
            "dateOfBirth": dob,
            "lastFourOfSSN": l_ssn
    }
    return card

def card_activation(authorization_token, card):
    logging.info(f"{DATE_TIME}: gen_card: Card Activation")
    json_string = json.dumps(card)
    response=""
    try:
        response = requests.post(
                url=f"{CARD_URL}/cards/activation",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json',
                    'Authorization': f'{authorization_token}'
                },
                timeout=5
            )
    except requests.Timeout:
        response = "Request has timed out"
    except requests.RequestException:
        response = "Request Failed"
    except :
        response = "card_activation: code ERROR"
    if str(response) == "<Response [200]>": 
        logging.info(f"{DATE_TIME}: Card has been activated")
        logging.info(f"{DATE_TIME}: {str(response)}")
        response_info = json.loads(response.text)
        logging.info(f"{DATE_TIME}: {str(response_info)}")
    else:
        logging.info(f"{DATE_TIME}: Card could NOT be activated")
    return response

def create_debit_card(authorization_token, account_num, memb_id, replacement):
    debit = {
        "accountNumber": account_num,
        "membershipId": memb_id,
        "replacement": replacement
    }
    logging.info(f"{DATE_TIME}: card: Debit Card Creation")
    json_string = json.dumps(debit)
    response=""
    try:
        response = requests.post(
                url=f"{CARD_URL}/cards/debit",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json',
                    'Authorization': f'{authorization_token}'
                },
                timeout=5
            )
    except requests.Timeout:
        response = "Request has timed out"
    except requests.RequestException:
        response = "Request Failed"
    except :
        response = "debit_card_post: code issue"
        response_info = ""
    if str(response) == "<Response [200]>": 
        logging.info(f"{DATE_TIME}: Debit Card has been added for account number {account_num}")
        logging.info(f"{DATE_TIME}: {str(response)}")
        response_info = json.loads(response.text)
        logging.info(f"{DATE_TIME}: {str(response_info)}")
    else:
        logging.info(f"{DATE_TIME}: Debit Card could NOT be added for account number {account_num}")
    return response