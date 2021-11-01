import json
import pandas as pd
import os
import requests
from requests.auth import HTTPBasicAuth
import datetime


# important info

# all_run_datafram
# multi_index_dataframe   
# metadata_list
# runid_name_index

# load in outputs from unpack.py
with open('./CaseStudy4_Data/metadata.json', 'r') as fp:
    metadata_list = json.load(fp)
    
all_run_dataframe = pd.read_csv('./CaseStudy4_Data/all_run_dataframe.csv')

multi_index_dataframe = pd.read_hdf('./CaseStudy4_Data/multi_index.h5', key='runid')

runid_name_index = pd.read_csv('./CaseStudy4_Data/runid_name_index.csv')


 
def get_az():
    '''
    Returns
    -------
    data_center_info : dict
            this gets Data Center information from a static file.
            file is JSON of data stream from: subprocess.check_output("az account list-locations", shell=True).
    '''

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "az_regions.json")
    data_center_info = json.load(open(json_url))
    return data_center_info    
     


def get_token():
    '''
    Returns
    -------
    token : string
        this gets user name and password for WattTime API from static file
        uses the credentials to ping WattTime API to generate a token to retrieve data
    '''
    
    # calling creds
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "login_creds.json")
    login_data = json.load(open(json_url))
    # WattTime ping with creds
    login_url = 'https://api2.watttime.org/v2/login'
    token = requests.get(login_url, auth=HTTPBasicAuth(login_data['username'], login_data['password'])).json()['token']
    return token



################################################
# Static data. uncomment for first run 
################################################ 
'''
# list initialization for static data
WattTime_Regions = []
# calling Data Center information from json file in static folder. 
data_center_coords = get_az()
# getting token to access CI source API
token = get_token()
# loop to associate WattTime regions to Azure data centers for a static reference  
for i in range(len(data_center_coords)):
    region_url = 'https://api2.watttime.org/v2/ba-from-loc'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'latitude': data_center_coords[i]['metadata']['latitude'],
              'longitude': data_center_coords[i]['metadata']['longitude']}
    rsp=requests.get(region_url, headers=headers, params=params)
    WattTime_Regions.append(rsp.text)
'''


# mapping Data Center name to display name
NAME_TO_DISPLAY = json.load(open('./static/name_to_display.json', 'r'))


 
# for data lookup via Data Center input
def getloc_helper(data_center_diplayName, token):
    '''
    Parameters
    ----------
    data_center_diplayName : string
        Common display name of the data center. ex: East US.
    token : string
        token for requesting data from CI source API.
    Returns
    -------
    dict
        this function takes in the full name of a Data Center grabs usefull data
        that can be used for various operations
        the data schema is:
        {Data Center Display Name, Balancing Authority Name, Balancing Authority Abbreviation, 
         Latitude of DC, Longitude of DC, Balancing Authority id}
    '''
    # grabbing data center coords and names
    data_center_info = get_az()

    # setting which key to search and match the value to  
    key = "displayName"

    # finding coords for the passed AZ_region
        # finds where the value of the key is equal to the input query value
            # this parses the Data Center information json  
    data_center_dict = next(filter(lambda x: x.get(key) == data_center_diplayName, data_center_info), None)


    #calling coords of AZ region
    data_center_latitude = data_center_dict['metadata']['latitude']
    data_center_longitude = data_center_dict['metadata']['longitude']

    # WattTime connection to get ba
    region_url = 'https://api2.watttime.org/v2/ba-from-loc'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'latitude': data_center_latitude, 'longitude': data_center_longitude}
    rsp=requests.get(region_url, headers=headers, params=params)

    # WattTime response and adding the azure region for output
    data = json.loads(rsp.text)
    data['AZ_Region'] = data_center_diplayName
    #print(f"getloc_helper data = {data}")

    return data


def get_SKU_table():
    '''
    Returns
    -------
    SKU_data_table : DataFrame
        DataFrame that contains region:geo mapping and available GPUs in the regions.
    '''
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    csv_url = os.path.join(SITE_ROOT, "static", "Region-SKU-Tags.csv")
    SKU_data_table = pd.read_csv(csv_url).dropna()
    return SKU_data_table
    

def gather_watttime(ba, starttime, endtime, token):
    '''
    Retrieve WattTime data and output as JSON object
    Arguments:
        ba: Region Abbreviation - string
        starttime: Starting datetime of inference session - dt
        endtime: Ending datetime of inference session - dt
    
    Output:
        JSON object containing WattTime response
    '''

    data_url = 'https://api2.watttime.org/v2/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    if ba == "IESO_NORTH":
        ba = 'IESO'
    params = {'ba': ba, 
        'starttime': starttime, 
        'endtime': endtime}
    #print(params)
    rsp = requests.get(data_url, headers=headers, params=params)

    ## integrity check, ensure that data is returned, else print flag
    data_check = str.strip(rsp.text[2:7])

    if len(data_check) < 1:
        print("DATA ERROR, COULD NOT GET CI DATA.")
        print("Verify that CI data is available for run parameters")
        print("Look at start and end times to assess appropriate action")
        
            
    if data_check == 'error':
        msg = "There was an error! No CI data was returned due to data source coverage"
        print('===============================================')
        print(msg)
        print('===============================================')

        
    return rsp




def emissions_total(ba, starttime, endtime, az_energy, token):
    '''
    Parameters
    ----------
    ba : string
        balancing authority abbreviation.
    starttime : string
        UTC ISO format start time for run.
    endtime : string
        UTC ISO end time for run.
    az_energy : array
        energy consumption timeseries values in joules.
    token : string
        CI dta source API auth token.
    Returns
    -------
    resource_emissions : DataFrame
        emissions in lbs/MWh for a specific run.
    '''
    
    # get CI data and format
    rsp = gather_watttime(ba, starttime, endtime, token)
    data = json.loads(rsp.text)
    WattTime_data = pd.json_normalize(data).dropna()
    WattTime_data = WattTime_data.sort_index(ascending=False)
    
    
    #power per time delta
    MegaWatth_per_five_min = az_energy*2.77778e-10

    # pounds of carbon per time delta
    resource_emissions = pd.DataFrame(MegaWatth_per_five_min*WattTime_data['value'].dropna())
    
    return resource_emissions



def get_real_emissions(token):
    '''
    Parameters
    ----------
    token : string
        CI dta source API auth token.
        
    Returns
    -------
    real_emissions_df : DataFrame
        emissions of each run for the region where it was executed.
        sum of carbon in lbs, runid, data center, balancing authority abbreviation.
    '''
    carbon_list = []
    for runid in runid_name_index['runid']:
        az_energy = multi_index_dataframe['total', runid].values
        for n in range(len(metadata_list)):
            if runid == metadata_list[n]['runid']:
                region = metadata_list[n]['metadata']['region']
                region_displayName = NAME_TO_DISPLAY[region]
        ba = getloc_helper(region_displayName, token)['abbrev']
        starttime = multi_index_dataframe.index[0]
        endtime = multi_index_dataframe.index[-1]
        
        emissions = emissions_total(ba, starttime, endtime, az_energy, token).set_index(multi_index_dataframe.index).sum().value
        carbon_list.append({'emissions':emissions, 'runid':runid, 'ba_abbrev':ba, 'region':region_displayName, 'starttime':starttime, 'endtime':endtime})
        
        real_emissions_df = pd.DataFrame(carbon_list)
        #print(real_emissions_df)
        
    return real_emissions_df


def get_counterfactual_emissions(real_df, token):
    '''
    Parameters
    ----------
    real_df : DataFrame
        output from get_real_emissions() that serves to provide region and ba data for a given runid
    token : string
        CI dta source API auth token.
    Returns
    -------
    counterfactual_carbon_list : list
        contains carbon counterfactuals for all potential regions in filtered_region_list.
    '''
    counterfactual_carbon_list = []

    real_starttime = datetime.datetime.fromisoformat(multi_index_dataframe.index[0][:-1])
    real_endtime = datetime.datetime.fromisoformat(multi_index_dataframe.index[-1][:-1])

    starttime_vals = [real_starttime + datetime.timedelta(minutes=30*x) for x in range(0, 48)]
    endtime_vals = [real_endtime + datetime.timedelta(minutes=30*x) for x in range(0, 48)]

    for runid in runid_name_index['runid']:
        az_energy = multi_index_dataframe['total', runid].values
        ba = real_df[real_df['runid'] == runid]['ba_abbrev'].iloc[0]
        region_displayName = real_df[real_df['runid'] == runid]['region'].iloc[0]

        for starttime, endtime in zip(starttime_vals, endtime_vals):
        
            emissions = emissions_total(ba, starttime, endtime, az_energy, token).set_index(multi_index_dataframe.index).sum().value
            counterfactual_carbon_list.append({'emissions':emissions, 'runid':runid, 'ba_abbrev':ba, 'inspected_region':region_displayName, 'starttime': datetime.datetime.isoformat(starttime), 'endtime':datetime.datetime.isoformat(endtime)})
        
        if runid == 'dec2_1632581832_065c9709':
            tmp = pd.DataFrame(counterfactual_carbon_list)
            tmp[tmp['runid'] == 'dec2_1632581832_065c9709'].to_csv('sanity.csv', index=False)
    
    return counterfactual_carbon_list

def counterfactual_minimums(counterfactual_carbon_list):
    '''
    finds minimum emission for each unique runid
    chunks based on number of regions permitted in the shift search
    
    Parameters
    ----------
    counterfactual_carbon_list : list
        contains carbon counterfactuals for all potential regions in filtered_region_list.
    Returns
    -------
    minimum_values : DataFrame
        minimum emission for each unique runid.
    '''
    counterfactual_emissions_df = pd.DataFrame(counterfactual_carbon_list)
    minimum_val = []
    for n in range(int(len(counterfactual_emissions_df)/48)):
        
        # stepwise chunk inspection.
        chunk = counterfactual_emissions_df.iloc[n*48:(n+1)*48]
        
        # stores the minimum in the inspected data chunk
        chunk_minimum = chunk[chunk['emissions'] == chunk['emissions'].min()]
        minimum_val.append(chunk_minimum)

    minimum_values = pd.concat(minimum_val)
    
    return minimum_values



def get_minimum_counterfactuals(real_df):
    '''
    get counterfactual emissions using new execution parameters.
    
    Parameters
    ----------
    real_df : DataFrame
        output from get_real_emissions() that serves to provide region and ba data for a given runid

    Returns
    -------
    min_run_emissions_df : DataFrame
        lowest emittor of counterfactual run trials.
    '''

    token = get_token()

    data_set_counterfactual = get_counterfactual_emissions(real_df, token)
    counterfactual_minimum_df = counterfactual_minimums(data_set_counterfactual)
    min_run_emissions_df = pd.DataFrame(counterfactual_minimum_df).reset_index()
    #print(min_run_emissions_df)
    
    return min_run_emissions_df


def percent_difference(truth_df, wtf_df):
    '''
    Parameters
    ----------
    truth_df : DataFrame
        real run emissions.
        output from get_real_emissions().
    wtf_df : DataFrame
        counterfacutal run emissions.
        output from get_minimum_counterfactals()
    Returns
    -------
    per_diff_df : DataFrame
        the percent difference between actual emissions and the counterfactual emissions.
        positive values indicate the counterfactual would reduce the footprint
    '''
    perc_diff_list = []
    for i in range(len(wtf_df)):
        perc_diff = 100*((truth_df['emissions'][i] - wtf_df['emissions'][i])/truth_df['emissions'][i]) 
        perc_diff_list.append({'percent_difference':perc_diff,
                               'region':truth_df['region'][i],
                               'starttime':truth_df['starttime'][i],
                               'endtime':truth_df['endtime'][i],
                               'shifted_starttime':wtf_df['starttime'][i],
                               'shifted_endtime': wtf_df['endtime'][i],
                               'runid':truth_df['runid'][i]})
    per_diff_df = pd.DataFrame(perc_diff_list)
    print(per_diff_df)
    
    return per_diff_df


###############################
# performing evaluation
################################

# getting CI data source token
token = get_token()
#print("Multi: ", multi_index_dataframe)

# getting actual emissions for each unique runid
real_emissions_df = get_real_emissions(token)

# finding the best carbon counterfactual
min_run_emissions_df = get_minimum_counterfactuals(real_emissions_df)

# calculating the percent difference between actual and counterfactual
percent_difference_df = percent_difference(real_emissions_df, min_run_emissions_df)

# output to csv
percent_difference_df.to_csv('time_shifting_output.csv', index=False)