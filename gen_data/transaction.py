import sys
import os
import json
import logging
import datetime
import requests
import random as ran
from dotenv import load_dotenv
import user
import account
import card

load_dotenv()
TRANSACTION_URL = os.getenv('TRANSACTION_URL')
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

def create_transaction(authorization_token, applicant):
    global TRANSACTION_METHODS
    global TRANSACTION_TYPES
    logging.info(f"{DATE_TIME}: transactions: Transaction Creation.")
    account_num = None
    balance = None
    account_type = None
    # Problem in endpoint for getting accounts by memberid, it only give the last account created
    # the following code will reflect only account returned in endpoint call due to being the
    # only way to get balance without accessing database information
    try:
        _, memb_account_info = account.get_account_by_member_id(authorization_token=authorization_token, memb_id=applicant.applicant_id)
        account_num = memb_account_info.get('content')[0].get('accountNumber')
        balance = memb_account_info.get('content')[0].get('balance')
        account_type = memb_account_info.get('content')[0].get('type')
    except:
        logging.info(f"{DATE_TIME}: gen_transactions: request for account information for applicant {applicant.applicant_id} FAILED")
    if account_num is None:
        print("Could not access member accounts")
        return None
    
    amount = ran.randint(1, 1000)
    difference = int(balance) - amount # Used to check if balance will go below 0
    target_card_type = None
    temp_methods = None
    temp_types = None
    target_method = None
    target_type = None
    card_exist = False
    if account_type == "CHECKING":#############CHECKING################
        #look to see if card exists
        for card in applicant.cards:
            if card.card_type == "DEBIT":
                card_exist = True
                break
        # depending on if card exist, the transactions and method types change
        if card_exist is True:# Debit Card and Checking
            target_card_type = "DEBIT"
            temp_methods = ['APP', 'ATM', 'ACH', 'DEBIT_CARD']
            temp_types = ['DEPOSIT', 'PURCHASE','VOID','WITHDRAWAL','REFUND']
            if difference < 0:# In case the amount would make the balance less than 0
                temp_types = ['DEPOSIT','VOID', 'REFUND']
        else:# Just Checking, No Debit Card
            temp_methods = ['APP', 'ATM', 'ACH']
            temp_types = ['DEPOSIT','WITHDRAWAL']
            if difference < 0:# In case the amount would make the balance less than 0
                temp_types = ['DEPOSIT']
    elif account_type == "CREDIT_CARD":###########CREDIT CARD############
        card_exist = False
        for card in applicant.cards:
            if card.card_type == "CREDIT_CARD":
                card_exist = True
                break
        if card_exist is False:
            print("Credit Card exist but is not activated")
            return None
        else:
            target_card_type = "CREDIT_CARD"
            temp_methods = ['APP', 'ACH', 'CREDIT_CARD']
            temp_types = ['PURCHASE','VOID','PAYMENT','REFUND']
            if difference < 0:# In case the amount would make the balance less than 0
                temp_types = ['PURCHASE','VOID']
    elif account_type == "LOAN":###############LOAN###############
        temp_methods = ['APP', 'ATM', 'ACH']
        temp_types = 'PAYMENT'
        if difference < 0:# In case the amount would make the balance less than 0
            amount = balance
    elif account_type == "SAVINGS":###############SAVINGS############
        temp_methods = ['APP', 'ATM', 'ACH']
        temp_types = ['DEPOSIT', 'WITHDRAWAL']
        if difference < 0:# In case the amount would make the balance less than 0
                temp_types = ['DEPOSIT']
    
    target_method = ran.choice(temp_methods)
    target_type = ran.choice(temp_types)

    card_request = None
    if card_exist is True:
        target_card = None
        for card in applicant.cards:# finds the correct card
            if card.card_type == target_card_type:
                target_card = card
        card_request = {
            "cardNumber": target_card.card_number,
            "securityCode": target_card.security_code,
            "expirationDate": target_card.exp_date
        }
    
    # correct formatting yyyy-mm-ddT##:##:##.###Z
    temp_date = str(datetime.datetime.utcnow())
    temp_date = temp_date[0:10] + "T" + temp_date[11:23] + "Z"
    date = temp_date

    merchant_code = str(ran.randint(10000, 99999999))
    merchant_name = "RandomMerchantName"
    description = "Dummy Description"
    
    bool_list = [True, False]
    is_hold = bool_list[ran.randint(0,1)]

    transaction = ""
    if card_request is None:
         transaction = {
            "type": target_type,
            "method": target_method,
            "date": date,
            "amount": amount,
            "merchantCode": merchant_code,
            "merchantName": merchant_name,
            "description": description,
            "accountNumber": account_num,
            "hold": is_hold
        }
    else:
        transaction = {
            "type": target_type,
            "method": target_method,
            "date": date,
            "amount": amount,
            "merchantCode": merchant_code,
            "merchantName": merchant_name,
            "description": description,
            "cardRequest": card_request,
            "accountNumber": account_num,
            "hold": is_hold
        }
    logging.info(f"{DATE_TIME}: Created Transaction\n{str(transaction)}")
    return transaction


def post_transactions(authorization_token, transaction):
    logging.info(f"{DATE_TIME}: Posting Transaction")
    json_string = json.dumps(transaction)
    response=""
    try:
        response = requests.post(
                url=f"{TRANSACTION_URL}/transactions",
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
    except:
        response = "post_transaction: code issue"
    if str(response) == "<Response [200]>": 
        response_info = json.loads(response.text)
        logging.info(f"{DATE_TIME}: transaction post was SUCCESSFUL")
        logging.info(f"{DATE_TIME}: {str(response)}")
        logging.info(f"{DATE_TIME}: {str(response_info)}")
    else:
        logging.info(f"{DATE_TIME}: transaction post was UNSUCCESSFUL")
    print(response)
    return response