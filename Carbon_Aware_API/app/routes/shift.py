#/app/routes/shift

from flask import Blueprint, redirect, make_response, request, current_app
from flask.helpers import url_for
from flask.templating import render_template
import pandas as pd
from app.utils import *
import datetime
from datetime import datetime as dt
from app.caches.AzureDataCenter import AzureDataCenterInfo

shift_bp = Blueprint('shift_bp', __name__)

azure_data_center_info = AzureDataCenterInfo()

def get_avg_moer(region_name, starting_time, deltaminutes=60):
    with open("./local_files/all_regions_forecasts.json", "r") as file_in:
        all_regions_forecasts = json.loads(json.load(file_in)) # Read in as string json. doing a second json.loads deserializes into json/dict object. 
    if region_name not in all_regions_forecasts.keys(): # Means there's no forecast data for this region. 
        return None

    point_times, moer_vals = all_regions_forecasts[region_name]['point_times'], all_regions_forecasts[region_name]['values']
    ending_time = starting_time + datetime.timedelta(minutes=deltaminutes)
    valid_moer_vals = []
    for point_time, moer_val in zip(point_times, moer_vals):
        point_time = dt.fromisoformat(point_time)
        if point_time >= starting_time and point_time <= ending_time:
            valid_moer_vals.append(moer_val)
    if not valid_moer_vals: # Current time not found within the forecasted data. The all regions forecast json file may be outdated. 
        return -1
    return sum(valid_moer_vals) / len(valid_moer_vals)

# 1. Real-time carbon info for BA - from the /get_index_api
# @app.route('/get_index_data', methods=["GET"])
def get_realtime_data(ba):
    token = get_token()
    index_url  = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(index_url, headers=headers, params=params)
    return rsp.json()

def geo_shifting(window_size):

    #if not region_name:
    #    print("Invalid region name. TODO: Display error page")
    # If a valid region display name was chosen/given

    if not os.path.isfile("./local_files/all_regions_forecasts.json"): # If file doesn't exist, run the update function to generate the cached file first then open this same file. 
        update_all_regions_forecast_data()
    else: 
        print("All Region forecast data exists... Using existing cache.")
        
    current_time = datetime.datetime.now(tz=datetime.timezone.utc).replace(tzinfo=None)
    return_dict = {}
    for region_name in NAME_TO_DISPLAY.keys(): # keys are all the AZ region names. 
        avg_moer_value = get_avg_moer(region_name = region_name, starting_time=current_time, deltaminutes=window_size)
        if not avg_moer_value:
            #print(f"No forecast data available for the region: {region_name}")
            continue
        if avg_moer_value == -1:
            print("Current time not found within the forecasted data... check the forecast JSON file under local_files")
            continue
        return_dict[region_name] = {
            'data_center_name' : region_name,
            'current_starttime' : current_time.isoformat(),
            'window_size_minutes' : window_size,
            'average_moer_value' : avg_moer_value
        }
    return return_dict

def get_SKU_table():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    print(SITE_ROOT)
    csv_url = os.path.join(current_app.config['ROOT_DIR'], "app/static", "Region-SKU-Tags.csv")
    SKU_data_table = pd.read_csv(csv_url).dropna()
    return SKU_data_table

def Law_filter(SKU_data_table, sensitive_check_box, Az_region):
    '''
    function to filter based on sovereignty laws.  
    if user specifies the shift contains protected data that is subject to migration laws
    limits regions in geo shift to only compliant regions
    '''
    try:
        if sensitive_check_box == 'on':
            geo = pd.DataFrame([SKU_data_table[SKU_data_table['region']==Az_region]['R_Tag_lock'].values])
            print(f"Regional Lock Tag for current region is {geo}")
            SKU_data_table_filtered = SKU_data_table[SKU_data_table['R_Tag_lock'] == geo[0].values[0]].reset_index()
        else:
            SKU_data_table_filtered = SKU_data_table.reset_index()
    except KeyError:   # if name was provided as an name not displayName
        if sensitive_check_box == 'on':
            geo = pd.DataFrame([SKU_data_table[SKU_data_table['region']==NAME_TO_DISPLAY[Az_region]]['R_Tag_lock'].values])
            print(f"Regional Lock Tag for current region is {geo}")
            SKU_data_table_filtered = SKU_data_table[SKU_data_table['R_Tag_lock'] == geo[0].values[0]].reset_index()
        else:
            SKU_data_table_filtered = SKU_data_table.reset_index()
        
    return SKU_data_table_filtered
   
def Gpu_filter(SKU_data_table_filtered,desired_GPU):
    '''
    function to take in region sku/law list which is either filtered by law or not
    looks at if a region has the desired GPU available
    if not, removes the region from potential shifting list
    '''
    GPU_Regions = []
    if desired_GPU == 'nada':
        for x in range(len(SKU_data_table_filtered)):
            GPU_Regions.append(SKU_data_table_filtered['region'][x])
    else:
        for x in range(len(SKU_data_table_filtered)):
            if desired_GPU in SKU_data_table_filtered['sku'][x]:
                GPU_Regions.append(SKU_data_table_filtered['region'][x])
    
    return GPU_Regions

# round to closest 5 min
def roundTime(dtt=None, roundTo=5*60):
    if dtt == None : 
        dtt = datetime.datetime.now()
        seconds = (dtt.replace(tzinfo=None) - dtt.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        return dtt + datetime.timedelta(0,rounding-seconds,-dtt.microsecond)
    else:
        dtt = dt.fromisoformat(dtt)
        seconds = (dtt.replace(tzinfo=None) - dtt.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        return dtt + datetime.timedelta(0,rounding-seconds,-dtt.microsecond)

def get_mean_window_time(some_dict, start_time, window_size):
    """
    the start_time is appended to the end of the list, so we can calculate its datetime format
    at the same time as the other ranges. 
    """
    forecast_dict = some_dict['forecast']
    print("=========================")
    #print(forecast_dict)
    print("=========================")
    point_time_strings = [time['point_time'] for time in forecast_dict]
    point_time_strings.append(start_time)
    moers = [moer['value'] for moer in forecast_dict]
    point_times = []
    pattern = r'(\d{4}-\d{1,2}-\d{1,2}).*(\d{2}:\d{2}:\d{2})'
    for point_time in point_time_strings:
        match = re.search(pattern, point_time)
        #print(match.group(1), match.group(2))
        #break
        year, month, day = [int(ymd) for ymd in match.group(1).split("-")] #ymd = year month date
        hour, minute, second = [int(hms) for hms in match.group(2).split(":")]
        point_times.append(datetime.datetime(year, month, day, hour, minute, second))
    delta_minutes = int(window_size)
    start_time = point_times[0] # Removes last element of the list which is the starting time to look out for and saves
    end_time = start_time + datetime.timedelta(minutes=delta_minutes)
    print(f"No shift start time: {start_time}. Its end time: {end_time}")
    moer_vals = [] # Holds MOER values that fit within start_time and start_time + delta_minutes
    for point_time, moer in zip(point_times, moers):
        # If the current window of time being examined goes past the last point time, break. 
        #print(point_time)
        if point_time > end_time:
            break
        
        if point_time >= start_time and point_time <= end_time:
            #print(point_time)
            moer_vals.append(moer)
    average_moer = sum(moer_vals) / len(moer_vals)
    return average_moer

def find_forecast_window_min(some_dict, start_index, end_index, window_size):
    if window_size == "no_window":
        print("No window size specified. Returning single minimum.")
        return find_forecast_min(some_dict, start_index, end_index)
    # Else utilize the window size accordingly
    print("=========================================")
    print(f"Querying with window size: {window_size}")
    forecast_dict = some_dict['forecast']
    
    # Need to convert to datetime for easier comparison and ranging
    point_time_strings = [time['point_time'] for time in forecast_dict]
    moers = [moer['value'] for moer in forecast_dict]
    """
    NOTE: This is a really ugly way of doing things. Haven't worked with date time ranges
    enough to know if there's a much easier way... I'm assuming there is but I was short on time.
    TODO: Refactor datetime preparation. 
    """
    point_times = []
    pattern = r'(\d{4}-\d{1,2}-\d{1,2}).*(\d{2}:\d{2}:\d{2})'
    for point_time in point_time_strings:
        match = re.search(pattern, point_time)
        year, month, day = [int(ymd) for ymd in match.group(1).split("-")] #ymd = year month date
        hour, minute, second = [int(hms) for hms in match.group(2).split(":")]
        point_times.append(datetime.datetime(year, month, day, hour, minute, second))
    #print(point_times)
    # At this point, all times are in datetime format and in chronological order. 
    """
    if window_size == "0hour30min":
        delta_minutes = 30
    elif window_size == "1hour0min":
        delta_minutes = 60
    elif window_size == "3hour0min":
        delta_minutes = 180
    else:
        delta_minutes = 360
    """
    
    print(f"Time Window Duration is {window_size} minutes")

    """
    Will iterate through moers values using point_time. 
    Initially, the index representing the start of the window is -1 and the 
    minimum mean values of MOERS is positive infinity. 
    Will sum up values from each index to index + window_size worth of datetime values using
    delta_minutes. Then compare with the current min_moer_mean. If the current mean calculated
    is lower than the min_moer_mean, then min_moer_mean is set to this new value and the min_index
    is set to the current index value. 
    """
    min_index, min_moer_mean = -1, float('inf')
    min_moer_vals = [] # Confirmation. 
    for index, moer in enumerate(moers):
        # Current moer total added up. num_moers = how many elements we've added to calculate the mean.

        current_moer_vals = [] # will hold the current time window's worth of moers. 

        # end_time is the upper datetime limit. If the current time we're examining is
        # greater than this, we've passed the window size. 
        end_time = point_times[index] + datetime.timedelta(minutes=window_size)

        # If the current window of time being examined goes past the last point time, break. 
        if end_time > point_times [-1]: 
            break
        for moer, point_time in zip(moers[index:], point_times[index:]):
            if point_time > end_time: break # past window_size if so
            current_moer_vals.append(moer)
        current_moer_mean = sum(current_moer_vals) / len(current_moer_vals)
        if current_moer_mean < min_moer_mean:
            min_index = index
            min_moer_mean = current_moer_mean
            min_moer_vals = current_moer_vals

    print(f"Current starting time with window size of {window_size} minutes is {point_times[min_index]} UTC")
    print(f"The average MOER value during this time window is {min_moer_mean}")
    print(f"Minimum index is {min_index}")
    print(f"Here is a list of the moer vals in that window for confirmation:\n {min_moer_vals}")
    #print(f"Here is the list of point times for this region: {point_times}")
    # Time format: 2021-07-23T21:30:00+00:00
    """
    print("NEW VALUES")
    print(point_time[:5])
    print(moers[:5])
    print(type(point_time[0]))
    print(type(moers[0]))
    """
    
    #forecast_dict = {'point_time': forecast_dict['forecast']['point_time'],
    #                    'value': forecast_dict['forecast']['value']}
    #print(forecast_dict)


    #print(some_dict)
    #MOER_preds = pd.DataFrame([some_dict['forecast'][k]['value'] for k in range(len(some_dict['forecast']))])
    #print("Moer preds is!!!", MOER_preds)
    print("=========================================")
    min_window_dict = {'point_time': forecast_dict[min_index]['point_time'], 
                        'value': min_moer_mean,
                        'ba': forecast_dict[min_index]['ba']
                        }
    return min_window_dict
    #return forecast_dict[min_index]

# Returns az region given input
def ba_region_helper(region_ba, dc_location):
    # get helper data using balancing authority or 
    try:
        data = from_ba_helper(region_ba)
        print(f"data clue of (region_ba) = {data}")

    except:
        try:
            data = getloc_helper(dc_location)
            print(f"data clue of (region_az) = {data}")
        except:
            return None
    az_region = data['AZ_Region']
    return az_region
    

def recent_region_data():
    '''
    same as amulet_test except this returns all 3 of the data entries instead of
    the last one.
    '''
    data_path = './local_files/data_for_table.json'
    if not os.path.exists(data_path):
        print("Cached copy does not exist. Creating first...")
        update_data_table()
    data_for_table = json.load(open(data_path,))
    
    return data_for_table

@shift_bp.route('/geotime_shift', methods=["GET"])
def geotime_shift(current_region=None):
    #update_all_regions_forecast_data() # FOR TESTING. Remove in production
    if not os.path.isfile("./local_files/all_regions_forecasts.json"): # If file doesn't exist, run the update function to generate the cached file first then open this same file. 
        print("All Region forecast data exists... Using existing cache.")
        update_all_regions_forecast_data()
    with open("./local_files/all_regions_forecasts.json", "r") as file_in:
        all_regions_forecasts = json.loads(json.load(file_in)) # Read in as string json. doing a second json.loads deserializes into json/dict object. 
    
    """
    What datetime.datetime.now() does: Will grab the local machine time. Mine is in Pacific Time which is 7 hours behind UTC... 
    But the Watt-time api returns times in UTC. 
    So... We grab the local time as in UTC, however this sets the tzinfo abstract class within the datetime.datetime. 
    The datetime library does not let you compare naive objects (datetime objects without tzinfo set) and aware objects (datetime objects
    with tzinfo set). So... we grab the time in UTC, then essentially set the tzinfo to None to be able to compare later. 
    """
    current_time = datetime.datetime.now(tz=datetime.timezone.utc).replace(tzinfo=None)
    # TODO: Do a check if current_region is valid or not. Get from request.form.get otherwise.
    # Then check if this value is valid or not. 
    
    #current_region = request.form.get("data_az")
    SKU_table = get_SKU_table()
    sensitive_check_box = request.form.get('sensitive', 'off') # Change this to request.form.get with HTML page added on
    desired_GPU = request.form.get("gpu_type", "nada") # Change this to request.form.get with HTML page added on
    filter_list = Law_filter(SKU_table, sensitive_check_box, current_region)
    try:
        filtered_regions_list = Gpu_filter(filter_list, desired_GPU)
    except KeyError:
        msg = 'verify chosen resource GPU. This GPU is unavailable in current workspace location'
        return make_response(render_template('data_error.html', msg=msg), 404)

    print('/n =============================')
    print('made it past the error handle')

    print(f"Based on GPU and Law filtering, geo and time-shifting over these regions:\n{filtered_regions_list}")
    # Grabbing window size and converting to minutes. 
    
    # TODO: Get window size input more efficiently. E.g. have users input values themselves. 

    window_minutes = request.form.get("window_size_minutes", default=0)
    window_hours = request.form.get("window_size_hours", default=0)
    

    try:
        window_hours = int(window_hours)
    except ValueError:
        window_hours = 0

    try:
        window_minutes = int(window_minutes)
    except ValueError:
        window_minutes = 0
    
    deltaminutes = window_minutes + (60 * window_hours)
    # If the window size is less than 30 minutes, set it to a minimum value of 30 minutes. 
    if deltaminutes < 30: deltaminutes = 30
    print(f"Querying with the following, CURRENT_AZ_REGION of {current_region}, CURRENT_TIME of {current_time}, WINDOW_SIZE of {deltaminutes} minutes")
    # These variables keep track of which region had the minimum average MOER value for the given window size as well as that given value. 
    minimum_region, minimum_avg_moer, greenest_starttime = None, float("inf"), datetime.datetime.now()
    current_region_moers = [] # Variables to keep track of current region's average moer for the given window. 
    for az_region, time_moer in all_regions_forecasts.items():
        print("==========================================================")
        displayName = all_regions_forecasts[az_region]['displayName']
        print(az_region, displayName)
        if displayName not in filtered_regions_list:
            print(f"Region: {displayName} not in filtered list for LAW and GPU. Skipping\n")
            continue
        print(f"Display name of current region: {displayName}")
        print(f"Region in filtered list?: {displayName in filtered_regions_list}")
        print()
        point_times, moer_vals = time_moer['point_times'], time_moer['values']
        print(f"Region being searched: {az_region}, Current Region Selected: {current_region}")
        if current_region == displayName: # find average window value for current region given the current time
            for moer, point_time in zip(moer_vals, point_times):
                point_time = datetime.datetime.fromisoformat(point_time)
                if point_time > current_time + datetime.timedelta(minutes=deltaminutes):
                    break
                if point_time >= current_time and point_time <= current_time + datetime.timedelta(minutes=deltaminutes):
                    current_region_moers.append(moer)

        for index, time in enumerate(point_times):
            current_moer_vals = [] # keep track of the current window
            start_time = datetime.datetime.fromisoformat(point_times[index]) # convert datetime string format to datetime object for comparison
            end_time = start_time + datetime.timedelta(minutes=deltaminutes)

            # If the ending time is greater than the last point_time, we are not getting a full window size. 
            if end_time > datetime.datetime.fromisoformat(point_times[-1]):
                break

            for moer, point_time in zip(moer_vals[index:], point_times[index:]):
                point_time = datetime.datetime.fromisoformat(point_time) # string datetime --> datetime object
                if point_time > end_time: break
                current_moer_vals.append(moer)

            average_moer = sum(current_moer_vals) / len(current_moer_vals)

            if average_moer < minimum_avg_moer: 
                minimum_region, minimum_avg_moer = az_region, average_moer
                greenest_starttime = time
    
    current_region_avg = sum(current_region_moers) / len(current_region_moers)
    print(current_region_avg)
    print(minimum_avg_moer)
    perc_diff = ((current_region_avg - minimum_avg_moer) / current_region_avg) * 100
    ba = all_regions_forecasts[minimum_region]['ba']
    return_dict = {
        'current_region' : current_region,
        'current_region_avg' : current_region_avg,
        'current_starttime' : current_time.isoformat(),
        'greenest_region' : NAME_TO_DISPLAY[minimum_region], 'greenest_starttime' : greenest_starttime,
        'greenest_region_BA' : ba,
        'minimum_avg_moer' : minimum_avg_moer, 'percentage_decrease' : round(perc_diff, 2), 
        'window_size_in_minutes': deltaminutes
    }
    #print(return_dict)
    return return_dict # Need to return as normal dictionary. Don't use jsonify(). It'll return as a response object. 


@shift_bp.route('/get_current_min_region', methods=["GET"])
def get_current_min_region(filtered_regions_list,current_region):
    '''
    function for if forecast data is not available. this takes in the list of regions that
    are filtered by Law and Gpu and gets average current data to use in for a replacement
    error handle geo shift.  
    takes the last 15 min of data for each region and finds the min average moer
    this is the region which is suggested for a geo shift and related data gathered for
    '''
    # reduces to only regions that pass the input parameter search
    region_history_dict = recent_region_data()
    position_numbers = []
    for entry in region_history_dict[0]["Azure Region"]:
        if region_history_dict[0]["Azure Region"][entry] in filtered_regions_list:
            position_numbers.append(entry)
    print(f"position_numbers is {position_numbers}")

@shift_bp.route('/shift_predictions', methods=["GET", "POST"])
def shift_predictions():
    print('step 1')
    WT_names = pd.DataFrame([json.loads(x) for x in WT_Regions])[['name','abbrev']].dropna()
    # set the shift type and direct
    
    
    
    
    shift_type = request.form.get('data_shifter', None)
    print(f"GET shift_type = {shift_type}")

    if shift_type:
        print('shift_choice is not equal to none')
        print(shift_type)
        dc_location = request.form.get('data_az', None)
        dc_balancing_authority = request.form.get('data_ba', None)
        if dc_balancing_authority != 'nada':
            dc_location = dc_balancing_authority
            print(f"now dc_location is the balancing authority {dc_balancing_authority}")
        else:
            ba = getloc_helper(dc_location)['name']
            print(f"ba = {ba}")
            print(f"dc_location didn't change and is {dc_location}")
            print("shift choice came from swagger route")

    else:
        try:
            print("starting form route")
            shift_type = request.form['data_shifter']
            # determine if AZ or BA was input
            print(f"Shift type selected: {shift_type}")
            dc_location = request.form.get('data_az', None)
            print(f"dc_location is {dc_location}")
            dc_balancing_authority = request.form.get('data_ba', None)
            print(f"dc_balancing_authority is {dc_balancing_authority}")
            #id the drop down choice and make sure there is 1 and only 1 chosen
            if dc_location == 'nada':
                dc_location = dc_balancing_authority
                print(f"now dc_location is the balancing authority {dc_balancing_authority}")
            else:
                print(f"dc_location didn't change and is {dc_location}")
                if dc_balancing_authority != 'nada':
                    msg = 'only select one Region type'
                    return make_response(render_template('pred_error.html', msg=msg), 400 )

            WT_names = WT_names.reset_index()
            print(WT_names)
            print(f"tring to call from df {WT_names['name'][1]}")
            print(f"the shift type is {shift_type}")
            if shift_type == 'nada':
                msg= 'select a shift type.'
                return make_response(render_template('pred_error.html', msg=msg), 404 )
        except:
            msg= 'begin a search first'
            return make_response(render_template('pred_error.html', msg=msg), 502 )




    ######
    # BOTH GEOGRAPHIC AND TIME SHIFTING
    ######

    if shift_type == 'Geographic and Time Shift':
        print('step 2.geotime')
        # determine if AZ or BA was input
        # determine if AZ or BA was input

        WT_names = WT_names.reset_index()
        #print(f"WT_names: {WT_names}")
        print(f"tring to call from df {WT_names['name'][1]}")
        #wt_list = WT_names.name.tolist()
        #for w in wt_list:
        #    if w == dc_location: print(w)
        #print(dc_location)
        # find what name matches:abbrev pair
        if dc_location in WT_names.name.tolist():
            region_ba = dc_location
            print(f"region_ba is {dc_location}")
            print(f"input = {dc_location}")
            az_region = ba_region_helper(region_ba, dc_location)
        else:
            az_region = ba_region_helper(None, dc_location)
        """
        for l in range(len(WT_names)):
            if WT_names['name'][l] == dc_location:
                region_ba = dc_location
                print(f"region_ba is {dc_location}")
                print(f"found match at {l}")
                print(f"input = {dc_location}")
                print(f"match = {WT_names['name'][l]}")
        """
        
        print(az_region)
        az_coords = azure_data_center_info.get_az()

        try:
            geo_time_shift_data = geotime_shift(current_region=az_region)
        except ZeroDivisionError:
            try:
                
                SKU_table = get_SKU_table()
                sensitive_check_box = request.form.get('sensitive', 'off')
                desired_GPU = request.form.get('gpu_type', None)
                filter_list = Law_filter(SKU_table, sensitive_check_box, az_region)
                filtered_regions_list = Gpu_filter(filter_list, desired_GPU)
                
                data = get_current_min_region(filtered_regions_list, az_region)
                print(f"data package is {data}")
                return render_template('load_shift_eval_2.html', data=data)
            except:
                print("input region does not have desired resource. no data for comparison.")
                msg = 'begin with a region that has the desired resource to make a predictive comparison.'
                return make_response(render_template('pred_error.html',msg=msg), 400) 


        #print(geo_time_shift_data)
        return render_template('load_shift_eval_geotime.html' ,data=geo_time_shift_data)













   
#####################################################################
#####################################################################
#####################################################################
    ######
    # GEOGRAPHIC SHIFTING ONLY
    ######    
#####################################################################
#####################################################################
#####################################################################

    
    if shift_type == 'Geographic Shift Only':
        print('step 2.geo')
        # determine if AZ or BA was input

        
        # find what name matches:abbrev pair
        try:
            if dc_location in WT_names.name.tolist():
                print(f"region_ba is {dc_location}")
                print(f"found match at {l}")
                print(f"input = {dc_location}")
                print(f"match = {WT_names['name'][l]}")
                print('using dc_location')
            """
            for l in range(len(WT_names)):
                if WT_names['name'][l] == dc_location:
                    region_ba = dc_location
                    print(f"region_ba is {dc_location}")
                    print(f"found match at {l}")
                    print(f"input = {dc_location}")
                    print(f"match = {WT_names['name'][l]}")
                    print('using dc_location')
            """    
        except:
            for l in range(len(WT_names)):
                if WT_names['name'][l] == ba:
                    region_ba = ba
                    print(f"region_ba is {ba}")
                    print(f"found match at {l}")
                    print(f"input = {ba}")
                    print(f"match = {WT_names['name'][l]}")
                    print('using ba')
                    break

        print('exited loop')
        # get helper data using balancing authority or 
        try:
            print('starting try')
            data = from_ba_helper(region_ba)
            print(f"data clue of (region_ba) = {data}")

        except:
            print('found exception')
            try:
                data = getloc_helper(dc_location)
                print(f"data clue of (region_az) = {data}")
            except:
                print('found another exception')
                msg = 'pick an Azure region or a WattTime balancing authority.'
                return make_response(render_template('pred_error.html', msg=msg), 400 )

        az_region = data['AZ_Region']
        print(az_region)
        az_coords = azure_data_center_info.get_az()

        
        '''
        switching from basic search of regions to allow filtering based on
        laws/compliance for data sets and desired GPU types
        updates region list to search for minimum MOER based on filtered data
        '''


        SKU_table = get_SKU_table()
        sensitive_check_box = request.form.get('sensitive', 'off')
        desired_GPU = request.form.get('gpu_type', None)
        filter_list = Law_filter(SKU_table, sensitive_check_box, az_region)
        filtered_regions_list = Gpu_filter(filter_list, desired_GPU)


        #window_size = request.form['window_size']
        window_size_hours, window_size_minutes = (request.form['window_size_hours']), (request.form['window_size_minutes'])

        try:
            window_size_hours = int(window_size_hours)
        except ValueError:
            window_size_hours = 0

        try:
            window_size_minutes = int(window_size_minutes)
        except ValueError:
            window_size_minutes = 0

        # max window size of 1 day (24 hours == 3600 minutes)
        if window_size_hours == HOURS_IN_DAY: 
            window_size = MINUTES_IN_DAY
            window_size_minutes = 0
        # minimum window size of 1 hour (60 minutes)
        if window_size_hours == 0 and window_size_minutes < MINUTES_IN_HOUR: 
            window_size_minutes = MINUTES_IN_HOUR

        window_size = (window_size_hours * 60) + window_size_minutes
        print(f"\n=======\nQuerying with window size of {window_size_hours} hours and {window_size_minutes} minutes\n========\n")
        print(f"Delta minutes (Window size in minutes) is {window_size} minutes")
         
        region_data = geo_shifting(window_size)

        filtered_emissions_list = []
        for data_center in filtered_regions_list:
            try:
                selected_data = region_data[DISPLAY_TO_NAME[data_center]]
                filtered_emissions_list.append(selected_data)
            except KeyError:
                print(f" this area did not have forecast data {data_center}")
        

        print(f"filtered_emissions_list = {filtered_emissions_list}")

        #print(f"list_location_data = {list_location_data}")
        #finding coords for the Az Regions in the geography
        window_moer = []
        window_data_center = []
        for data_center in range(len(filtered_emissions_list)):
            emissions_avg = filtered_emissions_list[data_center]['average_moer_value']
            window_moer.append(emissions_avg)
            window_data_center.append(filtered_emissions_list[data_center])
        try:
            current_region_moer = region_data[DISPLAY_TO_NAME[az_region]]['average_moer_value']
        except KeyError:
            data = get_current_min_region(filtered_regions_list, az_region)
            print(f"data package is {data}")
            return render_template('load_shift_eval_2.html', data=data)

        minimum_window_moer = min(window_moer)
        minimum_window_moer_index = window_moer.index(minimum_window_moer)
        minimum_region = window_data_center[minimum_window_moer_index]['data_center_name']
        percent_difference = 100*(current_region_moer - minimum_window_moer)/current_region_moer

        print(f"minimum_window_moer = {minimum_window_moer}")
        print(f"minumum_region = {minimum_region}")
        minimum_region_ba = getloc_helper(NAME_TO_DISPLAY[minimum_region])['name']


        page_data ={}
        page_data['greenest_moer'] = minimum_window_moer
        page_data['inputRegion'] = az_region
        page_data['shiftAZ'] = NAME_TO_DISPLAY[minimum_region]
        page_data['shift_perc'] = round(percent_difference, 2)
        page_data['shiftBA'] = minimum_region_ba
        page_data['window_size_in_minutes'] = window_size


        response = {}
        try:   
            response['shiftDateTime'] = page_data['shiftDateTime']
            response['shift_perc'] = page_data['shift_perc']
            response['shiftAZ']  = page_data['shiftAZ'] 

        except:
            response['shiftDateTime'] = dt.now().isoformat()
            response['shift_perc'] = page_data['shift_perc']
            response['shiftAZ']  = page_data['shiftAZ'] 


        if request.method == 'POST':
            # For output interface
            return render_template('load_shift_geo_eval.html' , data = page_data)
        else:
            return response
    
  
       

        """
##################################################
##################################################
##################################################
        here is the start of TIME SHIFT ONLY
#################################################
##################################################
###################################################
        """





    elif shift_type == 'Time Shift Only':
        print('step 2.time')

       # find what name matches:abbrev pair
        try:
            if dc_location in WT_names.name.tolist():
                region_ba = dc_location
                print(f"region_ba is {dc_location}")
                print(f"found match at {l}")
                print(f"input = {dc_location}")
                print(f"match = {WT_names['name'][l]}")
                print('using dc_location')
            """
            for l in range(len(WT_names)):
                if WT_names['name'][l] == dc_location:
                    region_ba = dc_location
                    print(f"region_ba is {dc_location}")
                    print(f"found match at {l}")
                    print(f"input = {dc_location}")
                    print(f"match = {WT_names['name'][l]}")
                    print('using dc_location')
            """
            
        except:
            for l in range(len(WT_names)):
                if WT_names['name'][l] == ba:
                    region_ba = ba
                    print(f"region_ba is {ba}")
                    print(f"found match at {l}")
                    print(f"input = {ba}")
                    print(f"match = {WT_names['name'][l]}")
                    print('using ba')
                    break

        print('exited loop')
        # get helper data using balancing authority or 
        try:
            print('starting try')
            data = from_ba_helper(region_ba)
            print(f"data clue of (region_ba) = {data}")

        except: 
            print('found exception')
            try:
                data = getloc_helper(dc_location)
                print(f"data clue of (region_az) = {data}")
            except:
                print('found another exception')
                msg = 'pick an Azure region or a WattTime balancing authority.'
                return make_response(render_template('pred_error.html', msg=msg), 400 )


        print(f"data = {data}")
        az_region = data['AZ_Region']
        print(az_region)
        az_coords = azure_data_center_info.get_az()


        #finding coords for the Az Regions in the geography
        geo = []
     

        Key = "displayName"
        Region_Name = az_region
        
        

    # finding coords for the passed AZ_region
        
        areaDict = next(filter(lambda x: x.get(Key) == Region_Name, az_coords), None)
        if areaDict == None:
            msg= 'use a different region to get a carbon analysis. There was no pre-paired Azure Data center available.'
            return make_response(render_template('pred_error.html', msg=msg), 404 )

        #calling coords of AZ region
        data_center_latitude = areaDict['metadata']['latitude']
        data_center_longitude = areaDict['metadata']['longitude']

        # getting data to choose geogrpahy
        realT = get_realtime_data_loc(data_center_latitude, data_center_longitude)
        print(realT)
        
        try:
            geo.append({'percent':realT['percent'],'abbrev':realT['ba'],'moer':realT['moer']})
        except:
            pass
            
        # making sure data was retrieved
        try:
            print(f"the MOER of {geo[0]['abbrev']} is {geo[0]['moer']}")
        except:
            print(f"No WattTime data was available for {az_region}")
            msg = 'use a Azure region supported by a WattTime balancing authority'
            return make_response(render_template('pred_error.html' , msg=msg), 404 ) 
            

        start = request.form.get('starttime', None)
        if not start:
            start = datetime.datetime.now()
        starttime = start.isoformat()
        print(f"Start time: {starttime}")
        end = request.form.get('endtime', None)
        if not end:
            end = start + datetime.timedelta(hours=24)
        endtime = end.isoformat()
        print(f"End time: {endtime}")

        """
        # get start and end times for window, empty defaults: start=now end=now+24hours
        start = request.form.get('starttime', None)
        if start != None:
            if len(start) == 0:
                start = str(datetime.datetime.now())
            start = start.upper()
        else: 
            start = str(datetime.datetime.now())
        print('swagger starttime works')
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
            print(f"input start {starttime}")
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('pred_error.html' , msg=msg), 404 ) 
        end = request.form.get('endtime', None)
        if end != None:
            if len(end) == 0:
                end = str(end + datetime.timedelta(hours=24))
            end = end.upper()
        else: 
            end = end = str(datetime.datetime.now() + datetime.timedelta(hours=24))
        print('swagger starttime works')

        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
            print(f"input end {endtime}")
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('pred_error.html', msg=msg), 400 ) 
        """
        
        #window_size = request.form['window_size']
        window_size_hours, window_size_minutes = (request.form['window_size_hours']), (request.form['window_size_minutes'])

        try:
            window_size_hours = int(window_size_hours)
        except ValueError:
            window_size_hours = 0

        try:
            window_size_minutes = int(window_size_minutes)
        except ValueError:
            window_size_minutes = 0

        # max window size of 1 day (24 hours == 3600 minutes)
        if window_size_hours == HOURS_IN_DAY: 
            window_size = MINUTES_IN_DAY
            window_size_minutes = 0
        # minimum window size of 1 hour (60 minutes)
        if window_size_hours == 0 and window_size_minutes < MINUTES_IN_HOUR: 
            window_size_minutes = MINUTES_IN_HOUR

        window_size = (window_size_hours * 60) + window_size_minutes
        print(f"\n=======\nQuerying with window size of {window_size_hours} hours and {window_size_minutes} minutes\n========\n")
        print(f"Delta minutes (Window size in minutes) is {window_size} minutes")
        # round timestamp to make ensure match to set window bounds
        rounded_starttime = roundTime(dtt=starttime, roundTo=5*60)
        rounded_endtime = roundTime(dtt=endtime, roundTo=5*60)
        print(f"starttime = {starttime}")
        print(f"rounded_starttime = {rounded_starttime}")

        geo_df = pd.DataFrame(geo)    
        min_geo = geo_df.loc[geo_df['moer'] == min(geo_df['moer'])]  
        print(f"min_geo = {min_geo}")

        # get MOER forecast for New Azure region
        pred_forecast = get_region_forcast(min_geo['abbrev'])
        print(str(pred_forecast)[:6])
        
        #print(f"pred_forecast['forecast'] = {pred_forecast['forecast']}")

        ########
        ### if no MOER forecast data available for the region submethod of only geog shift w/ no time shift
        ########
        if str(pred_forecast)[:6] == "{'erro":
            SKU_table = get_SKU_table()
            sensitive_check_box = request.form.get('sensitive', 'off')
            desired_GPU = request.form.get('gpu_type', None)
            filter_list = Law_filter(SKU_table, sensitive_check_box, az_region)
            filtered_regions_list = Gpu_filter(filter_list, desired_GPU)
            
            data = get_current_min_region(filtered_regions_list, az_region)
            print(f"data package is {data}")

            if request.method == 'POST':
                # For output interface
                return render_template('load_shift_eval_2.html' , data=data )
            else:
                msg = 'use a Region which has marginal forecast data from WattTime.'
                return make_response(render_template('pred_error.html', msg=msg), 400 ) 



        #print(f"pred_forecast = {pred_forecast}")


        # df to parse with input time window
        time_filter = pd.DataFrame([pred_forecast['forecast'][k] for k in range(len(pred_forecast['forecast']))])

        for i in range(len(time_filter["point_time"])):
            time_filter["point_time"][i] = time_filter["point_time"][i].split('+')[0]
            #print(time_filter["point_time"][i])

        print(f"in {rounded_starttime}")
        print(f"in {rounded_endtime}")

        # formatting start and end times to be able to find a match to create window
        starttime = pd.to_datetime([rounded_starttime], utc = True)
        starttime = str(starttime).split("'")[1]
        starttime = str(starttime).replace(" ", "T")
        endtime = pd.to_datetime([rounded_endtime], utc = True)
        endtime = str(endtime).split("'")[1]
        endtime = str(endtime).replace(" ", "T")


        print(f"altered start {starttime}")
        print(f"altered end  {endtime}")

        start = starttime[:16]
        end = endtime[:16]

        #start = starttime
        #end = endtime
        print(f"out {start}")
        print(f"out {end}")

        start_ind = []
        end_ind = []

        # finding matches to set the time window with the start/end times
        print('starting loop')
        for k in range(len(time_filter["point_time"])):
            if time_filter["point_time"][k][:16] == start:
                starter = time_filter["point_time"][k]
                start_ind.append(k)
                #print(f"start_ind is {start_ind}")

                
            if time_filter["point_time"][k][:16] == end:
                ender = time_filter["point_time"][k]
                end_ind.append(k)
                #print(f"end_ind is {end_ind}")
        
        try:
            start_ind = start_ind[0]
        except:
            start_ind = 0

        try:
            end_ind = end_ind[0]
        except:
            end_ind = len(time_filter)

        # getting unshifted results
        rt_in_reg = get_realtime_data(data['abbrev'])
        print(f"start_ind = {start_ind}")
        print(f"end_ind = {end_ind}")
        print(f" pref_f = {len(pred_forecast)}")
        #print(pred_forecast)

        pred_best_shift = find_forecast_window_min(pred_forecast, start_ind, end_ind, window_size)
        print(f"pred_best_shift = {pred_best_shift}")
        #print(f"the length of pred_best_shift is {len(pred_best_shift)}")
        #data checks
        print(f"pred_forecast min = {find_forecast_window_min(pred_forecast, start_ind, end_ind, window_size)}")
        print(f"rt_in_reg min = {rt_in_reg}")
        new_region = from_ba_helper(pred_best_shift['ba'])
        print(f"new_AZ = {new_region}")

        # set data for output
        page_data = {}
        page_data['inputRegion'] = data['AZ_Region']
        page_data['shift_choice'] = new_region['AZ_Region']
        page_data['shiftAZ'] = new_region['AZ_Region']
        page_data['no_shift'] = rt_in_reg
        page_data['inputBA'] = data['abbrev']
        #page_data['shiftBA'] = list(WattTime_abbrevs.keys())[list(WattTime_abbrevs.values()).index(new_region['name'])]
        page_data['shiftBA'] = new_region['name']
        page_data['shiftTime'] = pred_best_shift['point_time']
        page_data['no_shiftTime'] = rt_in_reg['point_time']
        page_data['shiftMOER'] = pred_best_shift['value']
        def get_noshift_moer(rt_in_reg, window_size):
            pass
        #def get_mean_window_time(some_dict, start_time, window_size):
        page_data['no_shiftMOER'] = get_mean_window_time(pred_forecast, rt_in_reg['point_time'], window_size) #rt_in_reg['moer']
        shiftDateTime = str(page_data['shiftTime'])
        shiftDateTime = shiftDateTime.split('+')[0]
        page_data['shiftDateTime'] = shiftDateTime
        no_shiftDateTime = str(page_data['no_shiftTime'])
        no_shiftDateTime = no_shiftDateTime.split('Z')[0]
        page_data['no_shiftDateTime'] = no_shiftDateTime

        shiftDate = str(shiftDateTime).split('T')[0]
        shiftTime = str(shiftDateTime).split('T')[1]
        print("=================================================")
        print(f"rt_in_reg = {rt_in_reg}")
        print("=================================================")

        FMT = '%Y-%m-%dT%H:%M:%S'

        page_data['shift_delta'] = dt.strptime(shiftDateTime, FMT) - dt.strptime(no_shiftDateTime, FMT)
        shift_perc = ((float(page_data['no_shiftMOER']) - float(page_data['shiftMOER']))/float(page_data['no_shiftMOER']))*100
        page_data['shift_perc'] = round(shift_perc,2)
        page_data['shiftDate'] = shiftDate
        page_data['shiftTime'] = shiftTime
        page_data['shiftMOER'] = round(pred_best_shift['value'], 0)
        page_data['window_size'] = window_size

        print('\n')
        print(f"page_data = {page_data}")


        print(f"time_filter = {time_filter}")

        

        
        response = {}
        try:   
            response['shiftDateTime'] = page_data['shiftDateTime']
            response['shift_perc'] = page_data['shift_perc']
            response['shiftAZ']  = page_data['shiftAZ'] 

        except:
            response['shiftDateTime'] = dt.now().isoformat()
            response['shift_perc'] = page_data['shift_perc']
            response['shiftAZ']  = page_data['shiftAZ'] 

        
        if request.method == 'POST':
            # For output interface
            return render_template('load_shift_eval.html' , data = page_data)
        else:
            return response
        
    else:
        msg = 'select a shifting type.'
        return make_response(render_template('pred_error.html', msg=msg), 400 ) 

@shift_bp.route('/pred_shift_find', methods=["GET", "POST"])
def shift_predictions_ui():
    return render_template('pred_shift_find.html')


@shift_bp.route('/prediction_rejected', methods=["GET", "POST"])
def prediction_rejected():
    '''    
    Pathway if the prediction was not used.
    Will log prediction data and that it was not used.
    Redirects to make a new prediction
    '''
    log = update_usage_data()

    return render_template("pred_shift_find.html")

@shift_bp.route('/prediction_made', methods=["GET", "POST"])
def prediction_made():
    '''
    Pathway if the prediction was to be used.
    Will log the prediction data and that it was used.
    Point of connection for cron scheduler.
    '''
    log = update_usage_data()
    carbon_to_date = avg_carbon_saved()


    return render_template("prediction_made.html", data = carbon_to_date)