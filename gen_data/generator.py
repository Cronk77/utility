import sys
import os
import json
import logging
import datetime
import requests
import random as ran
from dotenv import load_dotenv
import gen_applicant
from application import get_dummy_application_type, create_general_application, post_application,create_loan_application, Application
import user
import account
from card import card_activation, create_card_template,create_debit_card, Card
import bank_branch
import transaction

load_dotenv()
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

MENU_OPTIONS = {
    1: 'Option 1: Create Members',
    2: 'Option 2: Get list of Members',
    3: 'Option 3: Sign in',
    4: 'Option 4: Add Card to Member',
    5: 'Option 5: Create Bank and Branch',
    6: 'Option 6: Create Transaction',
    7: 'Exit'
}

APPLICANTS = {}
SIGNED_IN_MEMBER = None

def add_user(applicant, role=None):
    if role is None:
        role = "member"
    user_template = user.create_user(applicant, role)
    response = user.register_user(user_template)
    attempts = 10
    while str(response) != "<Response [201]>":
        attempts -= 1
        if attempts != 0:
            logging.info(f"{DATE_TIME}: Generator: User Registration Failed, reattempting")
            response = user.register_user(user_template)
        else:
            logging.info(f"{DATE_TIME}: Generator: User Registration Failed")
            print(f"Unable to Register User {applicant.first_name} {applicant.last_name}")
            break
    
    registration_information = ""
    if str(response) == "<Response [201]>":
        if role == "member":
            registration_information = json.loads(response.text)
            input_token = input(f"Enter Token for {applicant.user_name}: ")
            response = user.confirm_user(input_token)
            while str(response) != "<Response [200]>":
                input_token = input(f"Enter Token for {applicant.user_name}: ")
                response = user.confirm_user(input_token)
        else:
            logging.info(f"{DATE_TIME}: Generator: ADMIN Created")

def create_new_applicant(application_type=None):
    new_applicant = gen_applicant.Applicant()
    if application_type is None:
        application_type = get_dummy_application_type()
        #application_type = "SAVINGS"
    new_application = ""
    response = None
    if application_type == "LOAN":
        new_applicant = create_new_applicant(application_type="CHECKING")# recursive to create member w/ Checking account
        add_user(new_applicant, role="member")
        member_sign_in(str(new_applicant.applicant_id))
        new_loan_application = create_loan_application(applicant=new_applicant)
        response = post_application(application=new_loan_application, token=new_applicant.authorization_token)
    else:
        new_application = create_general_application(applicant=new_applicant, application_type=application_type)
        response = post_application(application=new_application)
    application_information = ""
    if str(response) == "<Response [201]>":
        application_information = json.loads(response.text)
    else:
        logging.info(f"{DATE_TIME}: Generator: Application creation failed, reattempting")
        response = None
        while str(response) != "<Response [201]>":
            if application_type == "LOAN":
                new_applicant = create_new_applicant(application_type="CHECKING")# recursive to create member w/ Checking account
                add_user(new_applicant, role="member")
                member_sign_in(str(new_applicant.applicant_id))
                new_loan_application = create_loan_application(applicant=new_applicant)
                response = post_application(application=new_loan_application, token=new_applicant.authorization_token)
            else:
                new_applicant = gen_applicant.Applicant()
                new_application = create_general_application(applicant=new_applicant, application_type=application_type)
                response = post_application(application=new_application)
        application_information = json.loads(response.text)
    # Create Application Object and sets it to applicant
    application_type = application_information.get('applicationType')
    print(f"\nApplication Type: {application_type}\n")
    print("\nApplication was Accepted!\n")
    account_number = application_information.get('createdAccounts')[0].get('accountNumber')
    new_application = Application(application_type=application_type, account_number=account_number)
    new_applicant.set_application(new_application)

    if application_type != "LOAN":
        applicant_id = application_information.get('applicants')[0].get('id')
        membership_id = application_information.get('createdMembers')[0].get('membershipId')
        new_applicant.set_applicant_id(applicant_id)
        new_applicant.set_membership_id(membership_id)

    application_key = new_applicant.applicant_id
    APPLICANTS[application_key] = new_applicant
    return new_applicant

def member_sign_in(target_applicant=None):
    print("")
    if target_applicant is None:
        target_applicant = input("Enter in Member Id to sign in: ")
    applicant_found = None
    for key in APPLICANTS:
        if str(key) == target_applicant:
            applicant_found = str(target_applicant)
            break
    if applicant_found is None:
        print("Could not find Member Id")
    else:
        applicant = APPLICANTS.get(int(applicant_found))
        response = user.user_sign_in(applicant)
        if str(response) == "<Response [200]>":
            print(f"{APPLICANTS[key].first_name} {APPLICANTS[key].last_name} Was Signed in.\n")
            global SIGNED_IN_MEMBER
            SIGNED_IN_MEMBER = applicant
        else:
            print(f"{APPLICANTS[key].first_name} {APPLICANTS[key].last_name} Was NOT Signed in.\n")

def add_card(applicant, card_type):
    card_exist = False
    card_number = None
    security_code = None
    exp_date = None
    dob = None
    last_four = None
    dob = applicant.date_of_birth
    last_four = applicant.social_security[7:]
    account_num = None
    if card_type == "CREDIT":
        for card in applicant.cards:
            if card.card_type == "CREDIT_CARD":
                card_exist = True
                break
        if card_exist == True:
            print("Credit Card Already exists")
            return
        else:
            unactivated_credit_account = False
            for application in applicant.applications:
                if application.application_type == "CREDIT_CARD":
                    unactivated_credit_account = True
            if unactivated_credit_account is True:# For applications of CREDIT CARDS but have not activated
                card_number = input("Enter Card number: ")
                security_code = input("Enter security code: ")
                exp_date = input("Enter in Expiration Date: ")
            else:# for No applications of type Credit Card
                application_template = create_general_application(applicant, "CREDIT_CARD")
                response = post_application(application=application_template, token=applicant.authorization_token)
                if str(response) == "<Response [201]>":
                    card_number = input("Enter Card number: ")
                    security_code = input("Enter security code: ")
                    exp_date = input("Enter in Expiration Date: ")
                else:
                    print("\nCredit Card NOT ACCEPTED\n")
                    return
    else:
        # DEBIT
        is_checking_exist = False
        for card in applicant.cards:# Checks to see if DEBIT card in applicants Cards
            if card.card_type == "DEBIT":
                card_exist = True
                break
        if card_exist == True:
            print("\nDebit Card Already exists\n")
            return
        else:# needs to create card
            membership_id = applicant.membership_id
            for application_item in applicant.applications:# Checks applications to see if Checking account exists
                if application_item.application_type == "CHECKING":
                    is_checking_exist = True
                    account_num = application_item.account_number
                    break
            if is_checking_exist == False:# Does not have Checking account
                application_template = create_general_application(applicant, "CHECKING")
                response = post_application(application=application_template, token=applicant.authorization_token)
                application_information = ""
                if str(response) == "<Response [201]>":
                    application_information = json.loads(response.text)
                    application_type = application_information.get('applicationType')
                    account_number = application_information.get('createdAccounts')[0].get('accountNumber')
                    new_type_application = Application(application_type=application_type, account_number=account_number)
                    applicant.set_application(new_type_application)
                    account_num = account_number
                else:
                    print("Application for Checking account was not accepted")
            else:# has checking account but does not have a activated card
                target_application = ""
                for application in applicant.applications:
                    if application.application_type == "CHECKING":
                        target_application = application
                account_num = target_application.account_number

            response = create_debit_card(applicant.authorization_token, account_num, membership_id, False)
            if str(response) == "<Response [200]>":
                card_information = json.loads(response.text)
                card_number = card_information.get("cardNumber")
                security_code = card_information.get('securityCode')
                exp_date = card_information.get('expirationDate')
    card_template = create_card_template(card_num=card_number, sec_code=security_code, exp_date=exp_date, dob=dob, l_ssn=last_four)
    response = card_activation(applicant.authorization_token, card_template)
    if str(response) == "<Response [200]>":
        new_card = Card(card_type=card_type, card_number=card_number, security_code=security_code, exp_date=exp_date)
        applicant.set_card(new_card)
        print("Card Activation ACCEPTED\n")
    else:
        print("Card Activation FAILED\n")

def create_bank_branch(number_bank, number_branch):
    applicant = create_new_applicant(application_type="CHECKING")
    add_user(applicant, role="admin")
    member_sign_in(str(applicant.applicant_id))
    authorization_token = applicant.authorization_token
    banks = {}
    for _ in range(number_bank):
        bank = bank_branch.get_bank_template()
        response = bank_branch.gen_bank(authorization_token=authorization_token, bank=bank)
        bank_info = json.loads(response.text)
        bank_id = bank_info.get("id")
        branches = []
        for _ in range(number_branch):
            branch = bank_branch.get_branch_template(bank_id=bank_id)
            branch_info = bank_branch.gen_branch(authorization_token=authorization_token, branch=branch)
            branches.append(branch_info)
        banks[bank_id] = branches
        print("Bank and Branches were created")
    return banks

def add_transaction():
    global SIGNED_IN_MEMBER
    applicant = SIGNED_IN_MEMBER
    authorization_token = applicant.authorization_token
    new_transaction = transaction.create_transaction(authorization_token, applicant)
    if new_transaction is not None:
        response = transaction.post_transactions(authorization_token, new_transaction)
        if str(response) == "<Response [200]>":
            print(f"Transaction Successful: \n {new_transaction}")
        else:
            print("Transaction Unsuccessful")

def print_menu():
    for key in MENU_OPTIONS.keys():
        print (key, '--', MENU_OPTIONS[key])

def main(argv=None):
    while(True):
        print_menu()
        try:
            option = int(input('Enter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        if option == 1:# Create Member 
            num_applicants = int(input("Enter number of Applicants to Create: "))
            for _ in range(num_applicants):
                applicant = create_new_applicant()
                if applicant.authorization_token is None:
                    add_user(applicant)
        elif option == 2:# print out Members
            print("\nApplicants: ")
            for key in APPLICANTS :
                print(f"{key}: {APPLICANTS[key].first_name} {APPLICANTS[key].last_name}")
            print("")
        elif option == 3:# Sign in to User
            member_sign_in()
        elif option == 4:# Add Card To Member
            if SIGNED_IN_MEMBER == None:
                print("\nSign into user in order to add a card.\n")
            else:
                card_types = [1,2]
                user_input = int(input("Enter card type:\n1: 'CREDIT'\n2: 'DEBIT\n"))
                while user_input not in card_types:
                    print("User choice invalid")
                    user_iput = int(input("Enter card type:\n1: 'CREDIT'\n2: 'DEBIT\n"))
                if user_input == 1:
                    add_card(SIGNED_IN_MEMBER, "CREDIT")
                else:
                    add_card(SIGNED_IN_MEMBER, "DEBIT")   
        elif option == 5:# add Banks and Branches
            number_banks = int(input("Enter number of Banks to Create: "))
            number_branch = int(input("Enter number of Branch to Create: "))
            while str(type(number_banks)) != "<class 'int'>":
                print("Invalid Entry!")
                number_banks = int(input("Enter number of Banks to Create: "))
            while str(type(number_branch)) != "<class 'int'>":
                print("Invalid Entry!")
                number_branch = int(input("Enter number of Branch to Create: "))
            create_bank_branch(number_banks, number_branch)
        elif option == 6:# Create Transaction for signed in user
            if SIGNED_IN_MEMBER == None:
                print("Sign into user in order to create transaction.")
            else:
                add_transaction()
        elif option == 7:
            print('Exiting')
            exit()
        else:
            print('Invalid option. Please enter a valid number.')


if __name__ == "__main__":
    main(sys.argv)
