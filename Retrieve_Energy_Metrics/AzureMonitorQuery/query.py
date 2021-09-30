import requests
import json
import subprocess
import az    
# install the above packages if not already done, will throw an error if not in device path



# Steps to Query Data:

# FIRST: ensure your device has the az cli enabled for account
    # run command:    "az login"   in the terminal. this should open a browser page
        # https://aka.ms/devicelogin  if no browser page is opened, this is the link
            # reference: https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli


# SECOND: change working directory to /AzureMonitorQuery (folder that contains this script)
     

# THIRD: fill in the following parameters:
    # subscription name/ID, start time, end time, resource groups, workspaces


# subscription name and ID for the ML resource
sub_name = ''
sub_id = '########-####-####-####-############'

# enter timespan to be searched (up to 30 day history)
    # times in UTC ISO = yyyy-mm-ddTHH:MM:SS.000Z
        # e.g. 2021-09-23T19:30:00.000Z
starttime = '####-##-##T##:##:##.000Z'
endtime = '####-##-##T##:##:##.000Z'

# list of the available resource groups, or the resource group(s) which you would like to pull data for
    # include all names of resource groups from the input subscription 
        # e.g. resourceGroup_list = ['resourceGroup1', 'resourceGroup2', .....]
resourceGroup_list = ['', ]

# list of the available workspaces, or the workspace(s) which you would like to pull data for
    # include all names of workspaces from all resource groups input into one list
        # e.g. workspace_list = ['workspace_name1', 'workspace_name2', .....]
workspace_list = ['',]



# With active az login and the 5 parameters filled out, the script is ready to run


def get_AML_token(sub_id):
    '''
    Parameters
    ----------
    sub_id : string
        the subscription ID for the AML resources/workspaces.

    Returns
    -------
    AML_token['accessToken'] : string
        bearer token belonging to user for the input AML subscription.
    '''
    AML_token = subprocess.check_output(f"az account get-access-token --subscription {sub_id}", shell=True)
    AML_token = json.loads((AML_token.decode("utf-8")))
    return AML_token['accessToken']


def get_resource_energy_data(workspace, resourceGroup, token):
    '''
    Parameters
    ----------
    workspace : string
        workspace within the the resource group .
    resourceGroup : string
        resource group to be searched for data.
    token : string
        Subscription bearer token.

    Returns
    -------
    AML_energy_data : dictionary
        std out of Az Mon query. Each workspace over window, split on RunId
    '''
    # define uri and build url for query
    req_url_sub_id = f"https://management.azure.com//subscriptions/{sub_id}/"
    req_url_resourceGroup = f"resourceGroups/{resourceGroup}/"
    req_url_workspace = f"providers/Microsoft.MachineLearningServices/workspaces/{workspace}/"
    req_url_metrics = "providers/microsoft.insights/metrics?api-version=2018-01-01&metricnames=GpuEnergyJoules&"
    req_url_timespan = f"interval=PT5M&timespan={timespan}&"
    req_url_aggregation = "aggregation=total&"
    req_url_filter = "$filter=RunId eq '*' and DeviceId eq '*'"
    # assemble pieces into request url
    req_url = (req_url_sub_id + req_url_resourceGroup + req_url_workspace + 
                req_url_metrics + req_url_timespan + req_url_aggregation + req_url_filter)            
    # make request to Azure Monitor
    AML_headers = {'Authorization': 'Bearer {}'.format(token)}
    AML_energy_data = requests.get(req_url, headers=AML_headers)
    AML_energy_data = json.loads(AML_energy_data.text)

    
    return AML_energy_data


# creating formatted time window from start and end times
time_divider = '/'
timespan = starttime + time_divider + endtime

# calling bearer token for user of the subscription
token = get_AML_token(sub_id)

# initializing counter to id number of files 
file_count = 0
# getting Az Mon GpuEnergyJoules data/metadata and saving to json if valid
for resourceGroup in resourceGroup_list:
    for workspace in workspace_list: 
        data = get_resource_energy_data(workspace, resourceGroup, token)
        if len(data) > 2:   # bad response has length of 1
            if len(data['value'][0]['timeseries']) != 0:    # if a valid resource-workspace, make sure data exists in time window
                with open(f"energy_profile_{sub_name}_{resourceGroup}_{workspace}.json", 'w') as fp:     
                    json.dump(data, fp)
                print('===========================')
                print(f"Energy data found during time window for workspace: {workspace}")
                print(f"Saving the file as energy_profile_{sub_name}_{resourceGroup}_{workspace}.json")
                print('')
                file_count += 1
            else:    # if time series is an empty list due to no activity in the time window, disregard workspace
                print(f"No energy data found during time window for workspace: _{sub_name}_{resourceGroup}_{workspace}")
                print('')


print(f"Number of files saved = {file_count}")
print("Files saved in working directory folder as energy_profile_{sub_name}_{resourceGroup}_{workspace}.json")
print('')


 