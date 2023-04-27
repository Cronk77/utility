##### To run Program, you must give an int argument
##### for number of Applicants to use for Application
'''Creates an application from random applicant in order to generate Membership'''
import sys
import os
import logging
import random as ran
import json
import datetime
import requests
from dotenv import load_dotenv
import gen_applicant

load_dotenv()
APPLICATION_URL = os.getenv('APPLICATIONS_URL')
LOG_LOCATION = os.getenv('LOG_LOCATION')

DATE_TIME = datetime.datetime.now()

# pylint: disable=logging-fstring-interpolation
# pylint: disable=bare-except
if LOG_LOCATION == "":
    try:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    except:
        print("gen_applications:Logging: could not print to sys.stout")
else:
    try:
        logging.basicConfig(filename=LOG_LOCATION, level=logging.INFO)
    except:
        print(f"gen_bank_branch:Logging: {LOG_LOCATION} is not a valid PATH")

APPLICATION_TYPES = ["CHECKING", "SAVINGS", "CHECKING_AND_SAVINGS", "CREDIT_CARD", "LOAN"]
LOAN_TYPES = ["PERSONAL", "AUTO", "HOME", "BUSINESS", "SECURE"]


class Application:
    def __init__(self, application_type, account_number):
        self.application_type = application_type
        self.account_number = account_number

def get_dummy_application_type():
    '''Gets a dummy application type'''
    random_num = ran.randint(0,4)
    target = APPLICATION_TYPES[random_num]
    return target

def get_dummy_loan_type():
    '''Gets a dummy application type'''
    random_num = ran.randint(0,4)
    target = LOAN_TYPES[random_num]
    return target

def create_general_application(applicant, application_type):
    '''Creates a single application given a applicant
    for Checking, Savings, Checking And Savings
    , and Credit Cards'''
    applicant_exist = False
    applicant_id = None
    if applicant.applicant_id is not None:
        applicant_exist = True
        applicant_id = int(applicant.applicant_id)
    logging.info(f"{DATE_TIME}: application: General Application Creation")
    json_applicant = gen_applicant.create_applicant_for_application(applicant)
    application = {
        "applicationType": application_type,
        "applicantIds": [applicant_id],
        "noNewApplicants": applicant_exist,
        "applicants": [json_applicant],
        "cardOfferId": ran.randint(1,4),
        "applicationAmount": 1000000
    }
    return application

def create_loan_application(applicant, loan_type=None):
    '''Creates a single loan application'''
    logging.info(f"{DATE_TIME}: application: Loan Application Creation")
    if loan_type is None:
            loan_type = get_dummy_loan_type()
    applicant_id = applicant.applicant_id
    account_num = None
    for application in applicant.applications:
        if application.application_type == "CHECKING":
            account_num = application.account_number
            break
    json_applicant = gen_applicant.create_applicant_for_application(applicant)
    application = {
        "applicationType": "LOAN",
        "noNewApplicants": True,
        "loanType": loan_type,
        "applicantIds": [applicant_id],
        "applicants": [json_applicant],
        "depositAccountNumber": account_num,
        "applicationAmount": ran.randint(10000, 1000000)        
    }
    return application

def post_application(application, token=None):
    logging.info(f"{DATE_TIME}: application: Application posting")
    json_string = json.dumps(application)
    try:
        response = requests.post(
                url = f"{APPLICATION_URL}/applications",
                data = json_string,
                headers={
                    'accept': '*/*',
                    'content-type': 'application/json',
                    'Authorization': f'{token}'
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
        logging.info(f"{DATE_TIME}: Application ACCEPTED\n{response}\n{application_info}")
    else:
        logging.info(f"{DATE_TIME}: Application NOT ACCEPTED:{response}")
    return response