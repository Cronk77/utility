import sys
import os
import json
import logging
import datetime
import requests
import random as ran
from dotenv import load_dotenv
import gen_user
import account
import gen_card

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

TRANSACTION_METHODS = ['APP', 'ATM', 'ACH', 'DEBIT_CARD', 'CREDIT_CARD']
TRANSACTION_TYPES = ['DEPOSIT', 'PURCHASE','VOID','WITHDRAWAL','PAYMENT','REFUND']

def create_transaction(authorization_token, applicant_id, last_four_ssn=None,\
     date_of_birth=None, card=None):
    '''Creates a transaction based on type of account and if they have a card'''
    logging.info(f"{DATE_TIME}: gen_transactions: Transaction Creation.")
    try:
        _, memb_account_info = account.get_account_by_member_id(authorization_token=authorization_token, memb_id=applicant_id)
        account_num = memb_account_info.get('content')[0].get('accountNumber')
        balance = memb_account_info.get('content')[0].get('balance')
        account_type = memb_account_info.get('content')[0].get('type')
    except:
        logging.info(f"{DATE_TIME}: gen_transactions: request for account information for applicant {applicant_id} FAILED")
    
    amount = ran.randint(1, 1000)
    difference = int(balance) - amount # Used to check if balance will go below 0

    accounts_with_cards = ["CHECKING", "CREDIT_CARD"]
    card_request = None
    transactions_method = ""
    transaction_type = ""
    if account_type in accounts_with_cards:
        given_card_type = ""
        if account_type == "CHECKING":
            given_card_type = "debit"
            transaction_method = TRANSACTION_METHODS[ran.randint(0, 3)]
            if difference < 0:# In case the amount would make the balance less than 0
                amount = balance 
            temp_int = [0,1,2,3,5]   
            transaction_type = TRANSACTION_TYPES[ran.choice(temp_int)]
        else:
            given_card_type = "credit"
            credit_card_type_list = ["PAYMENT", "PURCHASE", "REFUND", "VOID"]
            temp_int = [0,1,2,4]
            transaction_method = TRANSACTION_METHODS[ran.choice(temp_int)]
            if difference < 0:
                amount = balance
            transaction_type = ran.choice(credit_card_type_list)

        if card is None:
            #if no card, then need to pass in DOB and SSN to parms above
            card = gen_card.create_card(authorization_token=authorization_token, account_num=account_num, date_of_birth=date_of_birth, last_four_ssn=last_four_ssn, memb_id=None, card_type=given_card_type)

        card_request = {
            "cardNumber": card.get("cardNumber"),
            "securityCode": card.get('securityCode'),
            "expirationDate": card.get('expirationDate')
        }
    elif account_type == "LOAN":
        transaction_method = TRANSACTION_METHODS[ran.randint(0, 2)]
        if difference < 0:
            amount = balance
        transaction_type = "PAYMENT"
        card_request= ""
    else:
        # Saving account
        saving_type_list = ['WITHDRAWAL', 'DEPOSIT']
        transaction_method = TRANSACTION_METHODS[ran.randint(0, 2)]
        if difference < 0:
            saving_type_list = ['DEPOSIT']
        transaction_type = ran.choice(saving_type_list)
        card_request = ""
    # correct formatting yyyy-mm-ddT##:##:##.###Z
    temp_date = str(datetime.datetime.utcnow())
    temp_date = temp_date[0:10] + "T" + temp_date[11:23] + "Z"
    date = temp_date

    merchant_code = str(ran.randint(10000, 99999999))
    merchant_name = "RandomMerchantName"
    description = "Dummy Description"
    
    bool_list = [True, False]
    is_hold = bool_list[ran.randint(0,1)]
    
    if card_request is None:
         transaction = {
            "type": transaction_type,
            "method": transaction_method,
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
            "type": transaction_type,
            "method": transaction_method,
            "date": date,
            "amount": amount,
            "merchantCode": merchant_code,
            "merchantName": merchant_name,
            "description": description,
            "cardRequest": card_request,
            "accountNumber": account_num,
            "hold": is_hold
        }
    logging.info(f"{DATE_TIME}: {str(transaction)}")
    return transaction

def post_transactions(authorization_token, transaction):
    json_string = json.dumps(transaction)
    resp=""
    resp_info=""
    try:
        resp = requests.post(
                url=f"{TRANSACTION_URL}/transactions",
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
    except requests.RequestException:
        resp = "Request Failed"
    except :
        resp = "post_transaction: code issue"
        resp_info = ""
    if str(resp) == "<Response [200]>": 
        logging.info(f"{DATE_TIME}: transaction post was SUCCESSFUL")
    else:
        logging.info(f"{DATE_TIME}: transaction post was UNSUCCESSFUL")
    logging.info(f"{DATE_TIME}: {str(resp)}")
    logging.info(f"{DATE_TIME}: {str(resp_info)}")
    return resp, resp_info

def main(argv):
    user_list, users_info = gen_user.create_users(user_role="member", app_type="LOAN")
    info_list, _, updated_users = gen_user.register_users(user_list)
    _, _ = gen_user.user_creation_confirmation(info_list)

    user_name = updated_users[0].get('username')
    password = updated_users[0].get('password')
    _, authorization_token = gen_user.login(user_name, password)

    applicant_id = users_info[0].get('applicants')[0].get('id')
    _, memb_account_info = account.get_account_by_member_id(authorization_token, applicant_id)

    account_num = memb_account_info.get('content')[0].get('accountNumber')
    balance = memb_account_info.get('content')[0].get('balance')
    account_type = memb_account_info.get('content')[0].get('type')
    
    last_four_ssn = users_info[0].get('applicants')[0].get('socialSecurity')[7:]
    date_of_birth = users_info[0].get('applicants')[0].get('dateOfBirth')
    
    transaction = create_transaction(authorization_token=authorization_token, applicant_id=applicant_id, last_four_ssn=last_four_ssn, date_of_birth=date_of_birth, card=None)
    resp, resp_info = post_transactions(authorization_token=authorization_token, transaction=transaction)
if __name__ == "__main__":
    main(sys.argv)