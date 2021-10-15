import json
import os
import requests
from openpyxl.compat.singleton import Singleton
from flask import request, make_response
from requests.auth import HTTPBasicAuth
from collections import namedtuple
from datetime import datetime
from datetime import timedelta
from constant_definitions import DATA_CENTER_INFO_LOCATION


def get_password():
    if 'WT_PASSWORD' not in os.environ:
        print("Please set WT_PASSWORD as environment variable.")
        exit(-1)

    return os.environ['WT_PASSWORD']


def get_username():
    if 'WT_USERNAME' not in os.environ:
        print("Please set WT_USERNAME as environment variable.")
        exit(-1)

    return os.environ['WT_USERNAME']


class AzureDataCenterInfo(metaclass=Singleton):
    """This class provide an interface to get all azure data center"""

    def __init__(self):
        self.data_center_info = []
        # wattime token will expired in 30 minutes cache the token for 29 minutes before requesting another token.
        self.max_age = timedelta(minutes=29)
        self.CacheData = namedtuple("CacheData", "value createdDateTime")
        self.cache = {}
        self.login_url = 'https://api2.watttime.org/v2/login'

    def get_az(self):
        """
            this gets Data Center information from a static file.
            work around to implementing OAUTH2 login for a live feed of Azure regions
            slowly changing list
            file is JSON of data stream from: subprocess.check_output("az account list-locations", shell=True)
        """

        if not self.data_center_info:
            self.data_center_info = json.load(open(DATA_CENTER_INFO_LOCATION))

        return self.data_center_info

    def get_token(self, username=get_username(), password=get_password()):
        """
            This gets user name and password for WattTime from static file
            uses the credentials to ping WattTime API to generate a token to retrieve data
        """

        if 'token' in self.cache and self.cache['token'].createdDateTime + self.max_age >= datetime.utcnow():
            return self.cache.get('token').value

        # WattTime ping with creds
        token = requests.get(self.login_url, auth=requests.auth.HTTPBasicAuth(username, password)).json()['token']
        self.cache['token'] = self.CacheData(token, datetime.utcnow())
        return token
