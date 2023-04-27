import sys
import os
import json
import logging
import datetime
import requests
from dotenv import load_dotenv
from gen_applications import get_applications, post_requests, hit_api_applications
from gen_user import create_users, login, get_user_profile, register_users, user_creation_confirmation
from gen_applicant import gen_applicants_by_amount

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

def card_activation(authorization_token, card_num, sec_code, exp_date, dob, l_ssn):
    card_details = {
            "cardNumber": card_num,
            "securityCode": sec_code,
            "expirationDate": exp_date,
            "dateOfBirth": dob,
            "lastFourOfSSN": l_ssn
    }
    logging.info(f"{DATE_TIME}: gen_card: Card Activation")
    json_string = json.dumps(card_details)
    resp=""
    resp_info=""
    try:
        resp = requests.post(
                url=f"{CARD_URL}/cards/activation",
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
        resp = "card_activation: code issue"
        resp_info = ""
    if str(resp) == "<Response [200]>": 
        logging.info(f"{DATE_TIME}: Card has been activated for Card number {card_num}")
    else:
        logging.info(f"{DATE_TIME}: Card could NOT be activated for Card number {card_num}")
    logging.info(f"{DATE_TIME}: {str(resp)}")
    logging.info(f"{DATE_TIME}: {str(resp_info)}")
    return resp, resp_info

def debit_card_post(authorization_token, account_num, memb_id, rep):
    debit = {
        "accountNumber": account_num,
        "membershipId": memb_id,
        "replacement": rep
    }
    logging.info(f"{DATE_TIME}: gen_card: Debit Card Creation")
    json_string = json.dumps(debit)
    resp=""
    resp_info=""
    try:
        resp = requests.post(
                url=f"{CARD_URL}/cards/debit",
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
        resp = "debit_card_post: code issue"
        resp_info = ""
    if str(resp) == "<Response [200]>": 
        logging.info(f"{DATE_TIME}: Debit Card has been added for account number {account_num}")
    else:
        logging.info(f"{DATE_TIME}: Debit Card could NOT be added for account number {account_num}")
    logging.info(f"{DATE_TIME}: {str(resp)}")
    logging.info(f"{DATE_TIME}: {str(resp_info)}")
    return resp, resp_info

def create_card(authorization_token, account_num, date_of_birth=None, last_four_ssn=None, \
    memb_id=None, card_type=None, replacement=None):
    '''Create a credit/debit card and activates it
        debit is defualt'''
    if card_type is None:
        card_type = "debit"

    account_type = ""
    if card_type == "debit":
        account_type = "CHECKING"
    elif card_type == "credit":
        account_type = "CREDIT_CARD"
    else:
        logging.info(f"{DATE_TIME}: gen_card: create_card invalid card type for {card_type}")
        return "Empty CARD"

    if replacement is None:
        replacement = False
    
    _, user_info = get_user_profile(authorization_token)
    if date_of_birth is None:
        date_of_birth = input("Enter in date of birth(yyy-mm-dd): ")

    if  last_four_ssn is None:
        last_four_ssn = input("Enter in last four of ssn: ")

    card_num = ""
    sec_code = ""
    exp_date = ""
    dob = ""
    l_ssn = ""
    if card_type == "debit":
        if memb_id is None:
            memb_id = user_info.get('membershipId')
        _, resp_info = debit_card_post(authorization_token=authorization_token,\
             account_num=account_num, memb_id=memb_id, rep=replacement)
        card_num = resp_info.get('cardNumber')
        sec_code = resp_info.get('securityCode')
        exp_date = resp_info.get('expirationDate')
        dob = date_of_birth
        l_ssn = last_four_ssn
    else:
        # credit
        card_num = str(input("Enter card number: "))
        sec_code = str(input("Enter security code: "))
        exp_date = str(input("Enter experation date(yyyy-mm-dd): "))
        dob = str(input("Enter date of birth(yyyy-mm-dd): "))
        l_ssn = str(input("Enter in last four of ssn for member: "))
        
    _, card_info = card_activation(authorization_token, card_num, sec_code, exp_date, dob, l_ssn)
    return card_info

def main(argv):
    '''driver code to sign in as Admin and create Bank/Branch.'''
    '''Driver for gen user
        defualt: 1 debit auto
        2 args : # debit auto
        3 args : # card_type auto
        4:args : # card_type auto/manual
            card_type not credit or debit
        >4 args: exit program
    '''
    num_of_cards = ""
    given_card_type = ""
    card_options = ["debit", "credit"]
    if len(argv) == 1:
        num_of_cards = 1
        given_card_type = "debit"
    elif len(argv) == 2:
        if argv[1] == "0":
            logging.info(f"{DATE_TIME}: gen_card: number of cards was 0")
            sys.exit()
        num_of_cards = int(argv[1])
        given_card_type = "debit"
    elif len(argv) == 3:
        if argv[1] == "0":
            logging.info(f"{DATE_TIME}: gen_card: number of cards was 0")
            sys.exit()
        num_of_cards = int(argv[1])
        if argv[2].lower() not in card_options:
            logging.info(f"{DATE_TIME}: gen_card: Card type given was not a card option('debit' or 'credit'")
            sys.exit()
        given_card_type = argv[2]
    elif len(argv) == 4:
        if argv[1] == "0":
            logging.info(f"{DATE_TIME}: gen_card: number of cards was 0")
            sys.exit()
        num_of_cards = int(argv[1])
        if argv[2].lower() not in card_options:
            logging.info(f"{DATE_TIME}: gen_card: Card type given was not a card option('debit' or 'credit'")
            sys.exit()
        given_card_type = argv[2]
    elif len(argv) > 4:
        logging.info(f"{DATE_TIME}: gen_card: Too many arguments given")
        sys.exit()
    
    cards = []
    if len(argv) == 4 and argv[3].lower() == "manual":
        print("here")
        for i in range(num_of_cards):
        #Allows user to sign in to a specific member and create a card for an account
            print("To create card, please Login: ")
            user_name = input("Enter User Name: ")
            password = input("Enter Password: ")
            account_num = input("Enter account number: ")
            _, authorization_token = login(user_name, password)
            card = create_card(account_num=account_num, authorization_token=authorization_token,\
                 memb_id=memb_id, card_type=given_card_type)
            cards.append(card)
    else:
        app_type = ""
        if given_card_type.lower() == "debit":
            app_type = "CHECKING"
        else:
            app_type = "CREDIT_CARD"
        for i in range(num_of_cards):
            user_list, users_info = create_users(user_role="member", app_type=app_type)
            info_list, _, update_users = register_users(user_list)
            _, _ = user_creation_confirmation(info_list)

            account_num = users_info[0].get('createdAccounts')[0].get('accountNumber')
            memb_id = users_info[0].get('createdMembers')[0].get('membershipId')

            user_name = update_users[0].get('username')
            password = update_users[0].get('password')
            _, authorization_token = login(user_name, password)

            last_four_ssn = users_info[0].get('applicants')[0].get('socialSecurity')[7:]
            date_of_birth = users_info[0].get('applicants')[0].get('dateOfBirth')
            
            card = create_card(authorization_token=authorization_token, account_num=account_num,\
                date_of_birth=date_of_birth, last_four_ssn=last_four_ssn, memb_id=memb_id, \
                card_type=given_card_type)
            cards.append(card)

if __name__ == "__main__":
    main(sys.argv)
