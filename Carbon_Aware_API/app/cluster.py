import requests
from requests.auth import HTTPBasicAuth
from app.caches.AzureDataCenter import AzureDataCenterInfo
from openpyxl.compat.singleton import Singleton


class Cluster(metaclass=Singleton):

    def __init__(self):
        self.wt_regions = []
        self.azure_data_center_info = AzureDataCenterInfo()
        self.region_url = 'https://api2.watttime.org/v2/ba-from-loc'

    def get_wt_regions(self):
        if not self.wt_regions:
            self.convert_azure_cluster_to_wt_region()
        return self.wt_regions

    def get_header(self):
        return {'Authorization': 'Bearer {}'.format(self.azure_data_center_info.get_token())}

    def convert_azure_cluster_to_wt_region(self):
        azure_data_center = self.azure_data_center_info.get_az()
        login_url = 'https://api2.watttime.org/v2/login'
        token = requests.get(login_url, auth=HTTPBasicAuth("wibuchan", "greenAI")).json()['token']
        headers = {'Authorization': 'Bearer {}'.format(token)}
        headers = self.get_header()
        for i in range(len(azure_data_center)):
            params = {'latitude': azure_data_center[i]['metadata']['latitude'],
                      'longitude': azure_data_center[i]['metadata']['longitude']}
            rsp = requests.get(self.region_url, headers=headers, params=params)
            self.wt_regions.append(rsp.text)