
from app.utils import *
from app.caches.AzureDataCenter import AzureDataCenterInfo

azure_data_center_info = AzureDataCenterInfo()

az_coords = azure_data_center_info.get_az()


token = get_token()
# loop to associate WattTime regions to AZ regions
for i in range(len(az_coords)):
    region_url = 'https://api2.watttime.org/v2/ba-from-loc'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'latitude': az_coords[i]['metadata']['latitude'],
              'longitude': az_coords[i]['metadata']['longitude']}
    rsp = requests.get(region_url, headers=headers, params=params)
    WT_Regions.append(rsp.text)
    # print(rsp.text)

# combining on index
az_coords_WT_joined = [az_coords, WT_Regions]
WT_names = pd.DataFrame([json.loads(x) for x in WT_Regions])[
    ['name', 'abbrev']].dropna()


# strips values of symbol chars
no_symbol = re.compile(r'[^\d.]+')


az_coords_df = pd.DataFrame(az_coords)
wt_region_df = pd.DataFrame(WT_Regions)
az_coords_WT_joined = [az_coords, WT_Regions]
az_coords_df = az_coords_df.reset_index()


az_coords_df.columns = ['OldIndex', 'displayName', 'id', 'metadata', 'name',
                        'regionalDisplayName', 'subscriptionId']
wt_region_df = wt_region_df.reset_index()
wt_region_df.columns = ['OldIndex', 'WattTimeData']


AZ_WT_join = az_coords_df.join(wt_region_df, how='left',
                               rsuffix='_right')
AZ_WT_join = AZ_WT_join.drop('OldIndex_right', axis=1)


# AZ_WT_join is a df of all data


AZ_WT_join = AZ_WT_join.sort_values(by='WattTimeData', ascending=False)
AZ_WT_join = AZ_WT_join.reset_index()
AZ_WT_join = AZ_WT_join.drop('index', axis=1)


# Azure Data Centers that are supported by WattTime balancing authorities
AZ_with_WattTime = AZ_WT_join[:26]

# Azure Data Centers that have no geo-coordinates associated with them
AZ_with_no_coords = AZ_WT_join[26:46]

# Azure Data Centers that are NOT supported by WattTime balancing authorities
AZ_with_no_WattTime = AZ_WT_join[46:65]

# DisplayNames of Azure Data Centers that are supported by WattTime balancing authorities
AZ_with_WattTime_names = AZ_with_WattTime['displayName']


def get_mappy():
    # finding coords for the passed AZ_region
    regions = []
    Key = "displayName"
    for region_name in AZ_with_WattTime_names:
        areaDict = next(filter(lambda x: x.get(Key) ==
                        region_name, az_coords), None)
        region_name = areaDict[Key]
        lat, lon = areaDict['metadata']['latitude'], areaDict['metadata']['longitude']
        regions.append({'region_name': region_name,
                        'latitude': float(lat),
                        'longitude': float(lon)
                        })

    # print("!!!\n", regions) # Just lets me know I didn't mess up anything with the slight refactor.

    index_url = 'https://api2.watttime.org/index'
    real_time_az = []
    token = get_token()
    """
    NOTE: A lot of latency had to do with grabbing a new auth token for every single api request... instead of reusing one that's active. 
    Might introduce issues in token timing out but based on the code logic, it should be grabbing a new api token everytime the endpoint is called which
    would avoid this. One future thing to implement could be having a background task update "token" and reuse the same one until it times out. 
    If we know how long each auth token lasts, it could be as simple as using a subprocess + sleep for x seconds/minutes. 
    ####
    token lasts for 30min
    ####
    """

    for region in regions:
        headers = {'Authorization': 'Bearer {}'.format(token)}
        params = {'latitude': region['latitude'],
                  'longitude': region['longitude']}
        rsp = requests.get(index_url, headers=headers, params=params)
        real_time_az.append(rsp.text)

    # print(real_time_az)

    data = []
    for val in real_time_az:
        region_vals = json.loads(val)
        percent = int(region_vals['percent'])
        ba = region_vals['ba']
        moer = int(float(region_vals['moer']))
        data.append([ba, percent, moer])

    map_data = pd.DataFrame(
        data, columns=["Balancing Authority", "Emission Percent", "MOER Value"])
    #########

    map_locs = pd.DataFrame(regions)
    map_locs.columns = ['Azure Region', 'Latitude', 'Longitude']

    mappy = pd.concat([map_locs, map_data], axis=1)
    return mappy


def gather_watttime(ba, starttime, endtime):
    '''
    Retrieve WattTime data and output as JSON object
    Arguments:
        ba: Region Abbreviation - string
        starttime: Starting datetime of inference session - dt
        endtime: Ending datetime of inference session - dt

    Output:
        JSON object containing WattTime response
    '''
    token = get_token()
    data_url = 'https://api2.watttime.org/v2/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba,
              'starttime': starttime,
              'endtime': endtime}

    rsp = requests.get(data_url, headers=headers, params=params)

    # integrity check
    data_check = str.strip(rsp.text[2:7])
    print(f"data_check = {data_check}")
    if data_check == 'error':
        msg = 'check query parameters. WattTime response contained an error'
        return make_response(render_template('data_error.html', msg=msg), 400)
    elif len(data_check) == 0:
        msg = 'check query parameters. No WattTime response returned.'
        return make_response(render_template('data_error.html', msg=msg), 404)

    return rsp


def gather_azmonitor(filename, gpuutil_flag):
    # if file is csv, format it so it is in the order of [Index, Time, Totals, {Optional: GPUUtil}]
    if filename[-3:] == 'csv':
        az_file = format_dataframe(pd.read_csv(filename), gpuutil_flag)

        print(az_file['Time'].dtype)
        print(az_file['Total'].dtype)

        try:
            assert az_file['Time'].dtype == 'object'

        except:
            msg = 'use either a .xlsx, .csv, or .json file with the proper data type formats.'
            return make_response(render_template('data_error.html', msg=msg), 412)

    # if json, convert to pandas dataframe
    elif filename[-4:] == 'json':
        az_file = format_json(filename)
        print(az_file[:3])

    # if file is xlsx, format it so it is in the order of [Index, Time, Totals, {Optional: GPUUtil}]
    elif filename[-4:] == 'xlsx':
        az_file = format_dataframe(pd.read_excel(filename), gpuutil_flag)
        # print(az_file)
        print(az_file['Time'].dtype)
        print(az_file['Total'].dtype)

    # if none of the above, throw error
    else:
        msg = 'input a valid .xlsx, .csv, or .json file'
        return make_response(render_template('data_error.html', msg=msg), 413)

    # ensure datetime intervals are 5 minutes (300 seconds)
    if not compare_intervals(az_file):
        msg = 'use either a .xlsx, .csv, or .json file with 5 min time aggregation.'
        return make_response(render_template('data_error.html', msg=msg), 415)
    return az_file


def get_realtime_data(ba):
    token = get_token()
    index_url = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(index_url, headers=headers, params=params)
    return rsp.json()
