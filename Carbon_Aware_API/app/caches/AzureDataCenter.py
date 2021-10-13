import json

from openpyxl.compat.singleton import Singleton

from Carbon_Aware_API.constant_definitions import DATA_CENTER_INFO_LOCATION


class AzureDataCenterInfo(metaclass=Singleton):
    """This class provide an interface to get all azure data center"""
    def __init__(self):
        self.data_center_info = []

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
