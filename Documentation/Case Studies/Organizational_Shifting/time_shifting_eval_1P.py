# -*- coding: utf-8 -*-
"""
Temporal Shifting at Scale 


"""

import json
import pandas as pd
import os
import requests
from requests.auth import HTTPBasicAuth
import datetime
from datetime import datetime as dt
import dateutil.parser as parser
import statistics
from tqdm import tqdm
import time


# mapping Data Center name to display name
NAME_TO_DISPLAY = json.load(open('./static/name_to_display.json', 'r'))




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


def get_data():
    '''
    Returns
    -------
    data_set : DataFrame
        grabs the data set file from the static folder and removes any null values. 
    '''

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    csv_url = os.path.join(SITE_ROOT, "static", "data_set.csv")
    data_set = pd.read_csv(csv_url).dropna()
    return data_set


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
    #print(rsp.text)

# combining on index values 
data_center_WattTime_overlap = [data_center_coords, WattTime_Regions]
WattTime_names = pd.DataFrame([json.loads(x) for x in WattTime_Regions])[['name','abbrev']].dropna()



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

    data_center_info = get_az()


    # setting which key to search and the value to  
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


def Geo_filter(SKU_data_table, sensitive_check_box, Az_region):
    '''
    Parameters
    ----------
    SKU_data_table : DataFrame
        DataFrame that contains region:geo mapping and available GPUs in the regions..
    sensitive_check_box : string
        determines if the shift needs to stay in the same geo due to sensative data.
        'on' keeps in the same geo, and 'off' permits any available Data Center
    Az_region : string
        Azure Data Center display name.

    Returns
    -------
    SKU_data_table_filtered : DataFrame
            function based on sovereignty laws which can restrain searches to single geo 
            R_Tag_Lock sets the buckets of regions if the geo is going to be restrained. 
        
    '''
    try:
        if sensitive_check_box == 'on':
            geo = pd.DataFrame([SKU_data_table[SKU_data_table['region']==Az_region]['R_Tag_lock'].values])
            #print(f"Regional Lock Tag for current region is {geo}")
            SKU_data_table_filtered = SKU_data_table[SKU_data_table['R_Tag_lock'] == geo[0].values[0]].reset_index()
        else:
            SKU_data_table_filtered = SKU_data_table.reset_index()
    except KeyError:   # if name was provided as an name not displayName
        if sensitive_check_box == 'on':
            geo = pd.DataFrame([SKU_data_table[SKU_data_table['region']==NAME_TO_DISPLAY[Az_region]]['R_Tag_lock'].values])
            #print(f"Regional Lock Tag for current region is {geo}")
            SKU_data_table_filtered = SKU_data_table[SKU_data_table['R_Tag_lock'] == geo[0].values[0]].reset_index()
        else:
            SKU_data_table_filtered = SKU_data_table.reset_index()
        
    return SKU_data_table_filtered
   
    
def Gpu_filter(SKU_data_table_filtered, used_GPU):
    '''
    Parameters
    ----------
    SKU_data_table_filtered : DataFrame
        DataFrame of sku/regions that has passed the geo filter.
    used_GPU : string
        the GPU for the compute to then search by.

    Returns
    -------
    GPU_Regions : List
            function to take in region sku/geo list which is either filtered by geo or not
            looks at if a region has the desired GPU available
            if not, removes the region from potential evaluation list

    '''
    
    GPU_Regions = []
    if used_GPU == 'nada':
        for x in range(len(SKU_data_table_filtered)):
            GPU_Regions.append(SKU_data_table_filtered['region'][x])
    else:
        for x in range(len(SKU_data_table_filtered)):
            if used_GPU in SKU_data_table_filtered['sku'][x]:
                GPU_Regions.append(SKU_data_table_filtered['region'][x])
    
    return GPU_Regions



def roundTime(dtt=None, roundTo=5*60):
    '''
    Parameters
    ----------
    dtt : datetime, optional
        datetime timestamp. The default is None.
    roundTo : int, optional
        number of seconds scaled to the time interval to round to. The default is 5*60 for 5min. 

    Returns
    -------
    datetime 
        returns datetime rounded to the nearest interval in seconds.

    '''
    
    if dtt == None : 
        dtt = dt.now()
        seconds = (dtt.replace(tzinfo=None) - dtt.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        return dtt + datetime.timedelta(0,rounding-seconds,-dtt.microsecond)
    else:
        dtt = dt.fromisoformat(dtt)
        seconds = (dtt.replace(tzinfo=None) - dtt.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        return dtt + datetime.timedelta(0,rounding-seconds,-dtt.microsecond)
    
    

def gather_watttime(ba, starttime, endtime, token, row):
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
    params = {'ba': ba, 
        'starttime': starttime, 
        'endtime': endtime}
    
    rsp = requests.get(data_url, headers=headers, params=params)

    
    ## integrity check
    data_check = str.strip(rsp.text[2:7])
    
    if len(data_check) < 1:
        msg = "There was an error! CI data returned an empty list due to short run time"
        print('===============================================')
        print(msg)
        print('===============================================')
        end = data_set["FinishTime"][row]
        print(end)
        rounded_endtime = roundTime(parser.parse(end).isoformat()) 
        print(rounded_endtime)
        headers = {'Authorization': 'Bearer {}'.format(token)}
        params = {'ba': ba, 
            'starttime': starttime, 
            'endtime': rounded_endtime}
        print('===============================================')
        print(f"used a rounded endtime at index {row} to correct error")
        print('===============================================')
    rsp = requests.get(data_url, headers=headers, params=params)

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



def GpuSKUconvert(sku):
    '''
    Parameters
    ----------
    sku : string
        VM SKU of the compute.

    Returns
    -------
    gpu_type : string
        common GPU type name for geo-shifting. ex: V100.
        print out of new SKU if data contains an unknown.
        will cause error with this print statement at top of stack trace

    '''
    
    if sku == "STANDARD_NC24RS_V3":
       gpu_type = "V100"
    elif sku == "STANDARD_ND40RS_V2":
        gpu_type = "V100"
    elif sku == "STANDARD_NC24S_V3":
        gpu_type = "V100"
    else:
        print(f"new gpu type found in list. please add {sku} to sku list")
    return gpu_type



def DataPrep(start, end):
    '''
    Parameters
    ----------
    sku : string
        VM SKU for the compute.
    start : datetime string
        starting time of the run's execution.
    end : datetime string
        finsih time for the run.

    Returns
    -------
    gpu_type : string
        common GPU name.
    starttime : datetime string
        iso6801 formatted datetime for the run start.
    endtime : datetime string
        iso6801 formatted datetime for the run end.
    '''
    
    #gpu_type = GpuSKUconvert(sku)
    start = start.upper()
    starttime = parser.parse(start).isoformat()
    end = end.upper()
    endtime = parser.parse(end).isoformat()
    return starttime, endtime

# setting static reference for functions
az_coords = get_az()

def get_coords(Key, region_displayName):
    '''
    Parameters
    ----------
    Key : String
        the list of keys to search trough.
    region_displayName : String
        DisplayName of the Data Center being searched for.

    Returns
    -------
    geo coordinates of the datacenter as strings

    '''
    location_dict = next(filter(lambda x: x.get(Key) == region_displayName, az_coords), None)
    data_center_latitude = location_dict['metadata']['latitude']
    data_center_longitude = location_dict['metadata']['longitude']
    return data_center_latitude, data_center_longitude


data_set = get_data()



sensitive_check_box = "on"
GPU_data_table = get_SKU_table()



def emissions_avg(emissions_data):
    '''
    Parameters
    ----------
    emissions_data : list
        list of MOER values over the run window.

    Returns
    -------
    mean_run_emission : float
        mean MOER over the run window.

    '''
    
    
    moer_vals = []
    for n in range(len(emissions_data)):
        try:
            moer_vals.append(emissions_data[n]["value"])
        except KeyError:
            # if too short of run no data can be retrieved
            msg = 'Missing Data'
            print(msg)
            moer_vals.append(msg)
    try:
        mean_run_emission = statistics.mean(moer_vals)
    except:
        mean_run_emission = 10000000
    return mean_run_emission

def alt_emissions_avg(emissions_data, start, end):
    moer_vals = []
    # print("Data: ", emissions_data)

    for n in range(len(emissions_data)):
        match = datetime.datetime.fromisoformat(emissions_data[n]['point_time'][:-5])
        # print("Start: ", start)
        # print("End: ", end)
        # print("Match: ", match)
        # print(match >= start)
        # print(match <= end)
        if (match >= start) & (match <= end):
            #print('1')
            try:
                moer_vals.append(emissions_data[n]["value"])
            except KeyError:
                # if too short of run no data can be retrieved
                msg = 'Missing Data'
                print(msg)
                moer_vals.append(msg)
    try:
        mean_run_emission = statistics.mean(moer_vals)
    except:
        mean_run_emission = 10000000
    return mean_run_emission


def counterfactual_emissions(location_data, starttime, endtime, token, row):
    '''
    Parameters
    ----------
    available_regions : List
        list of regions available for the evaluation, after geo/gpu filters
    starttime : datetime string
        starting time of the run.
    endtime : datetime string
        finsish time for the run.
    token : string
        access token to request data from CI source.
    row : int
        row index of evaluation.

    Returns
    -------
    counterfactual : List
        Nested list giving counterfactual mean emissions for each available region

    '''
    counterfactual = []
    #print("Inputs: ", starttime, endtime)
    start_dt = datetime.datetime.fromisoformat(starttime)
    end_dt = datetime.datetime.fromisoformat(endtime)

    starttime_vals = [start_dt + datetime.timedelta(minutes=30*x) for x in range(0, 48)]
    endtime_vals = [end_dt + datetime.timedelta(minutes=30*x) for x in range(0, 48)]

    for start, end in zip(starttime_vals, endtime_vals):
    
        # get emissions data for the run and convert to dict
        shift_emissions_data_string  = gather_watttime(location_data["abbrev"], start, end, token, row).text
        #print("Normal counterfactual", shift_emissions_data_string)
        shift_emissions_data = json.loads(shift_emissions_data_string)
        #print(shift_emissions_data)
        
        # get average marginal emissions over the window of the run in used region
        mean_run_emission = emissions_avg(shift_emissions_data)
        
        counterfactual.append({'Starttime':start, 'mean_run_emission':mean_run_emission})
    return counterfactual
        
def alt_counterfactual_emissions(location_data, starttime, endtime, token, row):

    counterfactual = []
    #print("Inputs: ", starttime, endtime)
    start_dt = datetime.datetime.fromisoformat(starttime)
    end_dt = datetime.datetime.fromisoformat(endtime)

    starttime_vals = [start_dt + datetime.timedelta(minutes=30*x) for x in range(0, 48)]
    endtime_vals = [end_dt + datetime.timedelta(minutes=30*x) for x in range(0, 48)]

    end_24 = end_dt + datetime.timedelta(days = 1)

    shift_emissions_data_string  = gather_watttime(location_data["abbrev"], start_dt, end_24, token, row).text
    shift_emissions_data = json.loads(shift_emissions_data_string)
    #print(pd.DataFrame(shift_emissions_data))

    for start, end in zip(starttime_vals, endtime_vals):
        mean_run_emission = alt_emissions_avg(shift_emissions_data, start, end)
        counterfactual.append({'Starttime':start, 'mean_run_emission':mean_run_emission})
    return counterfactual


def min_counterfactual(shift_emissions_data):
    '''
    Parameters
    ----------
    shift_emissions_data : dict
        CI data for each regional shift counterfactual.

    Returns
    -------
    min_counterfactual : dict
        entry from shift_emissions_data which has the minimum mean CI over the run window.

    '''
    counterfactual_mean_moer = []
    for n in range(len(shift_emissions_data)):
        counterfactual_mean_moer.append(shift_emissions_data[n]["mean_run_emission"])
    min_counterfactual_emission_index = counterfactual_mean_moer.index(min(counterfactual_mean_moer))
    min_counterfactual = shift_emissions_data[min_counterfactual_emission_index]
    
    return min_counterfactual



def MOER_PercentDifference(truth_moer, counterfactual_moer):
    '''
    Parameters
    ----------
    truth_moer : float
        Mean MOER for the region where the run was executed.
    counterfactual_moer : float
        Mean MOER for the region where the run could have been executed..

    Returns
    -------
    moer_perc_diff : float
        gives the percent difference between the region where the run was executed and a greener choice.
        negative value states the regional shift would have reduced the carbon footprint
        if MOER is equal to 0 exactly, there was no green region shift and thus not eligble, flagged by setting MOER to 10000000
        if the MOER of the region that executed the run was 0 at the time, assuming error in CI data and flagged for removal same as above

    '''
    try:
        moer_perc_diff = 100*((counterfactual_moer - truth_moer)/truth_moer)
        if moer_perc_diff == 0:
            moer_perc_diff = 10000000
    except ZeroDivisionError:
        moer_perc_diff = 10000000
    return moer_perc_diff




def counterfactual_evaluation(data_set, duration):
    '''
    Parameters
    ----------
    data_set : DataFrame
        Data set containing parmeters for executed runs. ex: start and finish times for runs
    duration : range
        range of rows in the data set to evaluate for counterfactual emissions.

    Returns
    -------
    data_set_counterfactual : list
        Nested list. with the following schema
        {'current_region', 'green_region', 'carbon_delta_percent', 'index_value'}
        this function exectutes the evaluation for a specified range of rows in of the data set

    '''
    data_set_counterfactual = []
    print("Beginning at {}".format(duration[0]))
    for row in tqdm(duration):
        #print(row)
        try:
            # get region where compute was executed
            cluster_region = NAME_TO_DISPLAY[data_set["ClusterRegion"][row]]
            #print("Cluster Region: ", cluster_region)
            
            # grab run parameters
            starttime, endtime = DataPrep(data_set["StartTime"][row], data_set["FinishTime"][row])
            #print("Params: ", gpu_type, starttime, endtime)

            
            #restrict to current region geo with sensitive_check_box == 'on'
            #GPU_data_table_filtered = Geo_filter(GPU_data_table, sensitive_check_box, cluster_region)
            #print("GPU Data Table: ", GPU_data_table_filtered)
            
            # get data center balancing authority for CI query
            location_data = getloc_helper(cluster_region, token)
            #print("Location data", location_data)
            
            # get emissions data for the run and convert to dict
            emissions_data_string  = gather_watttime(location_data["abbrev"], starttime, endtime, token, row).text
            emissions_data = json.loads(emissions_data_string)
            #print("Emissions data for run", emissions_data[1]["value"])
            
            # get average marginal emissions over the window of the run in used region
            mean_run_emission = emissions_avg(emissions_data)
            #print(f"the mean MOER between {starttime} and {endtime} is {mean_run_emission}")
            
            ## Good until here

            # get average marginal emissions over the window of the run in used region
            shifting_counterfactual = alt_counterfactual_emissions(location_data, starttime, endtime, token, row)
            #shifting_counterfactual = counterfactual_emissions(location_data, starttime, endtime, token, row)

            #print(shifting_counterfactual == alt_shifting_counterfactual)
            #print("Shifting counterfactual comparison: ", pd.DataFrame(shifting_counterfactual), '\n\n', pd.DataFrame(alt_shifting_counterfactual))
            
            # finding the greenest counterfactual 
            green_time_info = min_counterfactual(shifting_counterfactual)
            #print(f"the green start time was {green_time_info['Starttime']} but the run was exectuted at {starttime}")
            #print(f"the green average emission was {green_time_info['mean_run_emission']} but the run average emissions was {mean_run_emission}")
            
            # calculating the percent difference for the green region compared to used region
            carbon_delta_percent = MOER_PercentDifference(mean_run_emission, green_time_info['mean_run_emission'])

            if carbon_delta_percent > 100000:
                carbon_delta_percent = 10000000
            #print(f"the counterfactual percent difference for {starttime} compared to {green_time_info['Starttime']} is {carbon_delta_percent}%")
            
        
            data_set_counterfactual.append({'current_starttime':starttime, 'green_starttime':green_time_info['Starttime'].isoformat(), 'carbon_delta_percent':carbon_delta_percent, 'index_value':row})
                #print('\n')
        except:
            print("Token died aborting at {}".format(row))
            return data_set_counterfactual, row

    return data_set_counterfactual, row


# EXAMPLE.  submits first 10 rows for counterfactual evaluation
N = 10
# N = len(data_set)


duration = range(N)
output_df = []
print("evaluation in-progress....")

for i in duration:
    try:
        data_set_eval, i = counterfactual_evaluation(data_set = data_set, duration = duration)
        output_df = output_df + data_set_eval
        duration = range(i, len(data_set))

        data_set_eval_df = pd.DataFrame(output_df)
        data_set_eval_df.to_csv('./output/data_set_eval_check.csv')
    except KeyboardInterrupt:
        data_set_eval_df = pd.DataFrame(output_df)
        data_set_eval_df.to_csv('./output/data_set_eval_fin.csv')
        break
    except:
        print("Unknown error found")
        break

try:
    data_set_eval_df = pd.DataFrame(output_df)
except:
    data_set_eval_df = pd.DateOffset(data_set_eval)
#print('DF: ', data_set_eval_df)
data_set_eval_df.to_csv('./output/data_set_eval_fin.csv')