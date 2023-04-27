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
from gen_applicant import gen_applicants_by_amount, create_applicant_for_application, Applicant
import gen_user

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

application_types = ["CHECKING", "SAVINGS", "CHECKING_AND_SAVINGS", "CREDIT_CARD", "LOAN"]
loan_types = ["PERSONAL", "AUTO", "HOME", "BUSINESS", "SECURE"]

def get_dummy_application_type():
    '''Gets a dummy application type'''
    random_num = ran.randint(0,4)
    target = application_types[random_num]
    return target

def get_dummy_deposit_account_num():
    '''Ceates a random deposit account number'''
    depo_acc_num = ""
    for _ in range(12):
        depo_acc_num += str(ran.randint(0,9))
    return depo_acc_num

def create_application(app=None, app_type=None):
    print("CREATE_APPLICATION: " + str(app_type))####################################################################
    '''Creates a single application given a applicant
    for Checking, Savings, Checking And Savings
    , and Credit Cards'''
    if app is None:
        app = Applicant()
    if app_type is None:
        app_type = get_dummy_application_type()
    applicant = create_applicant_for_application(app)
    application = {
            "applicationType": app_type,
            "applyAmount": 10000,
            "noNewApplicants": False,
            "applicants": [applicant],
            "cardOfferId": ran.randint(1,4),
            "applicationAmount": 1000000,
    }
    return application

def create_loan_application(app, applicant_id, account_num, loan_type=None):
    '''Creates a Loan type application and depends on an already existing applicant'''
    app_type = "LOAN"
    if loan_type is None:
        loan_type = loan_types[ran.randint(0, 4)]
    applicant = create_applicant_for_application(app)
    application = {
            "applicationType": app_type,
            "noNewApplicants": True,
            "loanType": loan_type,
            "applicantIds": [applicant_id],
            "applicants": [applicant],
            "depositAccountNumber": account_num,
            "applicationAmount": ran.randint(10000, 1000000)
    }
    return application

def get_applications(applicants=None, num=None, app_type=None, loan_type=None):
    '''Given a list of applicants create a list of applications for each applicant'''
    print("GET_APPLICATION: " + str(app_type))####################################################################################
    if applicants is None:
        if num is None:
            num = 1
        applicants = gen_applicants_by_amount(num)
    applications = []
    tokens = []
    for applicant in applicants:
        if app_type is None:
            app_type = get_dummy_application_type()
        app = ""
        if app_type == "LOAN":
            temp_app_list = [applicant]
            user_list, user_info_list = gen_user.create_users(user_role="member", \
                applicants=temp_app_list, app_type="CHECKING")
            registered_info_list, _, updated_users = gen_user.register_users(user_list)
            _, _ = gen_user.user_creation_confirmation(registered_info_list)
            applicant_id = user_info_list[0].get('applicants')[0].get('id')
            account_num = user_info_list[0].get('createdAccounts')[0].get('accountNumber')
            user_name = updated_users[0].get('username')
            password = updated_users[0].get('password')
            _, authorization_token = gen_user.login(user_name, password)
            app = create_loan_application(app=applicant, applicant_id=applicant_id, \
                account_num=account_num, loan_type=loan_type)
            tokens.append(authorization_token)
        else:
            # all applications tpyes but Loan
            app = create_application(app=applicant, app_type=app_type)
            tokens.append("EMPTY TOKEN")
        applications.append(app)
        print(app)
    return applications, tokens

def hit_api_applications(json_string, token=None):
    '''helper method for posting applications by
        sending a post request(ensure correct port
        if changed)'''
    try:
        resp = requests.post(
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
        resp = "Request has timed out"
    except requests.RequestException:
        resp = "Request Failed"
    logging.info(f"{DATE_TIME}: gen_application: Application Creation")
    return resp

def post_requests(request_types, hit_api_method, tokens=None):
    '''takes a list of requests such as applications
       and makes requests to the hit_api_method function
    '''
    response_codes = []
    info_list = []
    i = 0
    for request in request_types:
        json_string = json.dumps(request)
        resp = ""
        if tokens is None:
            resp = hit_api_method(json_string)
        else:
            resp = hit_api_method(json_string, tokens[i])
        logging.info(f"{DATE_TIME}: {str(resp)}")
        try:
            resp_info = json.loads(resp.text)
            logging.info(f"{DATE_TIME}: {str(resp_info)}")
            info_list.append(resp_info)
        except json.decoder.JSONDecodeError:
            logging.info(f"{DATE_TIME}: {str(resp.text)}")
            info_list.append(resp.text)
        response_codes.append(resp)
        i += 1
    return info_list, response_codes

def main(argv):
    '''Driver for gen application'''
    applicant_num = ""
    app_type = None
    if len(argv) == 1:
        applicant_num = 1
    elif len(argv) == 2:
        applicant_num = int(argv[1])
    elif len(argv) == 3:
        applicant_num = int(argv[1])
        if argv[2].upper() not in application_types:
            logging.info(f"{DATE_TIME}: gen_application: given application type not known")
            sys.exit()
        app_type = argv[2].upper()
    elif len(argv) > 3:
        logging.info(f"{DATE_TIME}: gen_application: Too many arguments given")
        sys.exit()
    applicants = gen_applicants_by_amount(applicant_num)
    applications, tokens = get_applications(applicants, app_type=app_type)
    _, _ = post_requests(applications, hit_api_applications, tokens)

if __name__ == "__main__":
    main(sys.argv)
    