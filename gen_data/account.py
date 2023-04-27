'''gets account information from account microservice'''
import sys
import os
import json
import logging
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()
ACCOUNT_URL = os.getenv('ACCOUNT_URL')
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


def get_account_by_accout_id(authorization_token, memb_id):
    target_url = f"{ACCOUNT_URL}/accounts/{memb_id}"
    resp_info = ""
    try:
        resp = requests.get(
                url=target_url,
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
    print(resp)
    if str(resp) == "<Response [200]>":
        logging.info(f"{DATE_TIME}: account: Got account information:")
    else:
        logging.info(f"{DATE_TIME}: account: getting user: failed to get account information.")
    return resp, resp_info

def get_account_by_member_id(authorization_token, memb_id):
    target_url = f"{ACCOUNT_URL}/members/{memb_id}/accounts"
    resp_info = ""
    try:
        resp = requests.get(
                url=target_url,
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
    if str(resp) == "<Response [200]>":
        logging.info(f"{DATE_TIME}: account: Got account information:")
        logging.info(f"{DATE_TIME}{str(resp)}")
        logging.info(f"{DATE_TIME}{str(resp_info)}")
    else:
        logging.info(f"{DATE_TIME}: account: getting user: failed to get account information.")
    return resp, resp_info
