#app/routes/ci_data  -- Carbon intensity data

from flask import Blueprint, redirect, make_response, request, current_app
from flask.helpers import url_for
from flask.templating import render_template
import pandas as pd
from app.data import *
from app.utils import *
import datetime
from os import path
from flask.helpers import send_file
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets.tables import DataTable, TableColumn



ci_bp = Blueprint('carbonintensity_bp', __name__)


@ci_bp.route('/protected', methods=['GET', 'POST'])
def protected():
    return render_template('datachoice_combo.html')

@ci_bp.route('/ci_data', methods=['GET', 'POST'])
def ci_data():
    return render_template('ci_find.html')

@ci_bp.route('/chooser', methods=["GET", "POST"])
def chooser():
    '''
    This serves as a gateway and path selection tool so enpoints can be combined in the UI.
    '''
    WT_names = pd.DataFrame([json.loads(x) for x in WT_Regions])[['name','abbrev']].dropna()
    end_point_choice = request.form['data']
    print(end_point_choice)

    dc_location = request.form['data_az']

    dc_balancing_authority = request.form['data_ba']
    print(dc_balancing_authority)
    if dc_location == 'nada':
        dc_location = dc_balancing_authority
        if dc_balancing_authority == 'nada':
            msg = 'be sure to select an Azure region or WattTime balancing authority for the search'
            return make_response(render_template('data_error.html', msg=msg), 400 )
    else:
        if dc_balancing_authority != 'nada':
            msg = 'only select one Region type'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
    WT_names = WT_names.reset_index()
    for l in range(len(WT_names)):
        if WT_names['name'][l] == dc_location:
            region_ba = dc_location
            print(f"found match at {l}")
            print(f"input = {dc_location}")
            print(f"match = {WT_names['name'][l]}")
        else:
            region_az = dc_location
    try:       
        if region_ba != 0:
            data = from_ba_helper(region_ba)
            print(data['abbrev'])
            print(f"data clue of (region_ba) = {data}")
    except:
        data = getloc_helper(region_az)
        print(f"data clue of (region_az) = {data}")




    # Grid data path for historical emissions over a time window
    if end_point_choice == 'grid':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('ci_error.html', msg=msg), 400 )
        start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() - datetime.timedelta(minutes=15))
        start = start.upper()
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('ci_error.html' , msg=msg), 404 ) 
        end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        try:
            user_name = request.form.get('user_name', None)
            pass_word = request.form.get('pass_word', None)
        except:
            msg = 'verify correct Username and Password'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
   
        return redirect(url_for('carbonintensity_bp.get_grid_data', ba=ba, starttime=starttime, endtime=endtime, user_name=user_name, pass_word=pass_word))
    
    # historical data path, gives zip file
    elif end_point_choice == 'historical':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('ci_error.html', msg=msg), 400 )
        try:
            user_name = request.form.get('user_name', None)
            pass_word = request.form.get('pass_word', None)
        except:
            msg = 'verify correct Username and Password'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        return redirect(url_for('carbonintensity_bp.get_historical_data', ba=ba,user_name=user_name,pass_word=pass_word))

    # real-time data path
    elif end_point_choice == 'index':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('ci_error.html', msg=msg), 400 )
        try:
            user_name = request.form.get('user_name', None)
            pass_word = request.form.get('pass_word', None)
        except:
            msg = 'verify correct Username and Password'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        return redirect(url_for('carbonintensity_bp.get_index_data', ba=ba,user_name=user_name,pass_word=pass_word))

    # marginal emissions forecast data for chosen region, 24hrs by default
    elif end_point_choice == 'forecast':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('ci_error.html', msg=msg), 400 )
        
        start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() - datetime.timedelta(minutes=15))
        start = start.upper()
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('ci_error.html', msg=msg), 400 ) 
        end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('ci_error.html', msg=msg), 400 ) 
        try:
            user_name = request.form.get('user_name', None)
            pass_word = request.form.get('pass_word', None)
        except:
            msg = 'verify correct Username and Password'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        return redirect(url_for('carbonintensity_bp.get_forecast_data', ba=ba, starttime=starttime, endtime=endtime,user_name=user_name,pass_word=pass_word))

    # azure-watttime data analysis, goes to dashboard like UI 
    elif end_point_choice == 'azure':
        gpuutil = request.form.get('gpuutil', 0)
        if gpuutil == 'on':
            gpuutil = 1
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('data_error.html', msg=msg), 400 )
        az_region = data['AZ_Region']
        print(f"region = {az_region}")
        filename = get_file_data()
        start, end = get_start_end(filename)
        
        #start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() - datetime.timedelta(hours=24))
        start = start.upper()
        print(start)
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        #end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        print(end)
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        return redirect(url_for('carbonintensity_bp.get_timeseries_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename, AZ_Region=az_region , gpuutil=gpuutil))



    # azure-watttime data file return, CSV of timeseries Time:Emissions:Energy 
    elif end_point_choice == 'azure2':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('data_error.html', msg=msg), 400 )
        az_region = data['AZ_Region']
        print(f"region = {az_region}")
        filename = get_file_data()
        start, end = get_start_end(filename)

        #start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() - datetime.timedelta(hours=24))
        start = start.upper()
        print(start)
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        #end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        print(end)
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        return redirect(url_for('carbonintensity_bp.get_timeseries_table_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename, AZ_Region=az_region))

    # azure-watttime data
    elif end_point_choice == 'sums':
        filename = get_file_data()
        start, end = get_start_end(filename)

        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('data_error.html', msg=msg), 400 )
        #start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() - datetime.timedelta(hours=24))
        start = start.upper()
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
            print(starttime)
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        #end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        return redirect(url_for('carbonintensity_bp.get_sum_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename))

    # azure-watttime data
    elif end_point_choice == 'peaks':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('data_error.html', msg=msg), 400 )
        filename = get_file_data()
        start, end = get_start_end(filename)
        #start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() - datetime.timedelta(hours=24))
        start = start.upper()
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        #end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400 ) 
        return redirect(url_for('carbonintensity_bp.get_peak_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename))
        
    else:
        msg = 'try different query parameters'
        return make_response(render_template('data_error.html',msg=msg), 404 )



@ci_bp.route('/get_grid_data', methods=["GET"])
def get_grid_data():
    token = protected_token()
    starttime = request.args.get("starttime", None)
    endtime = request.args.get("endtime", None)
    ba = request.args.get("ba", None)
    data_url = 'https://api2.watttime.org/v2/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba, 
            'starttime': starttime, 
            'endtime': endtime}
    rsp = requests.get(data_url, headers=headers, params=params)
    # check to see if location has a ba
    data_check = str.strip(rsp.text[2:7])
    print(data_check)
    if data_check == 'error':
        msg= 'check query parameters. WattTime response contained an error'
        return make_response(render_template('data_error.html',msg=msg), 400 )
    elif len(data_check) == 0:
        msg= 'check query parameters. No WattTime response returned.'
        return make_response(render_template('data_error.html', msg=msg), 404)
    return rsp.text 

    #return render_template('output_page.html', data=data)   # for html output

# route to get real-time ba data
@ci_bp.route('/get_index_data', methods=["GET"])
def get_index_data():
    token = protected_token()
    ba = request.args.get("ba", None)
    index_url  = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(index_url, headers=headers, params=params)
   
    return rsp.text # for text output


# route to get historical data for given ba
@ci_bp.route('/get_historical_data', methods=["GET"])
def get_historical_data():
    token = protected_token()
    ba = request.args.get("ba", None)
    historical_url = 'https://api2.watttime.org/v2/historical'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(historical_url, headers=headers, params=params)
    cur_dir = path.dirname(path.realpath('__file__'))
    historical_dir = path.join(cur_dir, 'historical_zipfiles')
    file_path = path.join(historical_dir, '{}_historical.zip'.format(ba))
    with open(file_path, 'wb') as fp:
        fp.write(rsp.content)
    return send_file(file_path, as_attachment=True)



# route too get marginal forecast data in designated time window for given ba
@ci_bp.route('/get_forecast_data', methods=["GET"])
def get_forecast_data():
    token = protected_token()
    starttime = request.args.get("starttime", None)
    endtime = request.args.get("endtime", None)
    ba = request.args.get("ba", None)
    forecast_url = 'https://api2.watttime.org/v2/forecast'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba, 
        'starttime': starttime, 
        'endtime': endtime}
    rsp = requests.get(forecast_url, headers=headers, params=params)
    data_check = str.strip(rsp.text[2:7])
    print(data_check)
    if data_check == 'error':
        msg= 'check query parameters. WattTime response contained an error'
        return make_response(render_template('data_error.html',msg=msg), 400 )
    elif len(data_check) == 0:
        msg= 'check query parameters. No WattTime response returned.'
        return make_response(render_template('data_error.html', msg=msg), 404)
    return rsp.text 


@ci_bp.route('/all_index', methods=["GET","POST"])
def all_index():
    mappy = get_mappy()
    print(f"mappy = {mappy}")
    #mappy.to_csv("Region_Info.csv", encoding='utf-8', index=False )
    #Scatter Map
    #Scatter Map
    fig5 = px.scatter_geo(mappy, lat =mappy['Latitude'], lon=mappy['Longitude'], hover_name=mappy['Azure Region'],
    hover_data=[mappy['Emission Percent'],mappy['MOER Value']] , color=mappy['MOER Value'],title='Global Azure Regions in WattTime Balancing Authorities', template='none')

    fig5 = plotly.io.to_html(fig5)
    
    # Data table
    # Using bokeh
    data_for_table = mappy[['Azure Region', 'MOER Value']]

    source = ColumnDataSource(data_for_table)

    columns = [
        TableColumn(field="Azure Region", title="Azure Region"),
        TableColumn(field="MOER Value", title="MOER Value"),
    ]

    data_table = DataTable(source=source, columns=columns, width=400, height=280)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(data_table)


    return render_template( 'footprint.html', plot1=fig5, 
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,) 


# /overview api
@ci_bp.route('/overview', methods=["GET", "POST"])
def overview():
    
    try:
        BA_name = request.form.get('data', request.args.get('data'))
        print(f"try BA = {BA_name}")
    except:
        msg = 'check query string for errors in formatting'
        return make_response(render_template('data_error.html',msg), 400)
    try:
        print(f"try BA = {BA_name}")
        if BA_name == 'nada':
            return make_response(render_template('ba_error.html'), 400)
    except:
        msg = 'select a WattTime balancing authority to inspect.'
        return make_response(render_template('data_error.html',msg=msg), 404 )
    abbrev = WattTime_abbrevs[BA_name]
    print(f"the BA Abbrev is {abbrev}")
    moer_value = get_realtime_data(abbrev)
    percent_zeros = get_percent_zero(abbrev)
    aoer_value = get_average_emission(abbrev)

    data={}

    data['moer_value'] = moer_value["moer"]
    data['percent_zeros'] = percent_zeros
    data['aoer_value'] = aoer_value
    data['name'] = BA_name

    token = get_token()
    endtime = datetime.datetime.now().isoformat()
    starttime = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
    data_url = 'https://api2.watttime.org/v2/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': abbrev, 
            'starttime': starttime, 
            'endtime': endtime}
    rsp = requests.get(data_url, headers=headers, params=params)
    
    vals  = rsp.json()

    # To plot the daily, weekly and monthly carbon emission trends

    if vals[0]['frequency'] != 300:
        daydata = vals[:int(round((len(vals)/30),0))]
        print(daydata[:3])
        print(len(daydata))
        weekdata = vals[:int(round((len(vals)/4),0))]
        print(len(weekdata))
        monthdata = vals
        print(len(monthdata))

        MOER_day_time = []
        MOER_day = []
        for x in range(0,len(daydata),int(round((len(daydata)/24),0))):
            val = daydata[x]['value']
            time = daydata[x]['point_time']
            MOER_day.append(val)
            MOER_day_time.append(time)
        Neat_day = pd.DataFrame([MOER_day_time,MOER_day]).T
        Neat_day.columns = ['Time (UTC)' , 'Marginal Carbon Intensity']  

        MOER_week_time = []    
        MOER_week = []
        for x in range(0,len(weekdata),int(round((len(weekdata)/24),0))):
            val = weekdata[x]['value']
            time = weekdata[x]['point_time']
            MOER_week.append(val)
            MOER_week_time.append(time)
        Neat_week = pd.DataFrame([MOER_week_time,MOER_week]).T
        Neat_week.columns = ['Time (UTC)' , 'Marginal Carbon Intensity']

        MOER_month_time = []    
        MOER_month = []
        for x in range(0,len(monthdata),int(round((len(vals)/24),0))):
            val = monthdata[x]['value']
            time = monthdata[x]['point_time']
            MOER_month.append(val)
            MOER_month_time.append(time)
        Neat_month = pd.DataFrame([MOER_month_time,MOER_month]).T
        Neat_month.columns = ['Time (UTC)' , 'Marginal Carbon Intensity']

    else:
    # When frequency == 300
        daydata = vals[:288]        # 24 hrs in day * 60 mins in an hr / 5 min interval
        weekdata = vals[:2016]      # 7 * 24 * 60 / 5
        monthdata = vals   

        # Getting MOER values at 5-min interval in a day 
        MOER_day_time = []
        MOER_day = []
        for x in range(len(daydata)):
            val = daydata[x]['value']
            time = daydata[x]['point_time']
            MOER_day.append(val)
            MOER_day_time.append(time)
        Neat_day = pd.DataFrame([MOER_day_time,MOER_day]).T
        Neat_day.columns = ['Time (UTC)' , 'Marginal Carbon Intensity']

        # Aggregating Moer values over an hour (60/5 = 12) 
        MOER_week = []
        MOER_week_time = []
        for x in range(0,len(weekdata), 12):
            aggregated_moer_60mins = 0
            for y in range(x, x+12):
                aggregated_moer_60mins += weekdata[y]['value']
                aggregated_moer_times = weekdata[y]['point_time']
            MOER_week.append(aggregated_moer_60mins//12)
            MOER_week_time.append(aggregated_moer_times)
        Neat_week = pd.DataFrame([MOER_week_time,MOER_week]).T
        Neat_week.columns = ['Time (UTC)' , 'Marginal Carbon Intensity']

        try:
            # Aggregating Moer values over 6 hours (6*60/5 = 72)     
            MOER_month = []
            MOER_month_time = []
            #print(f"monthdata = {monthdata}")
            print(f"len monthdata = {len(monthdata)}")
            if len(monthdata) == 8640:
                for x in range(0,len(monthdata), 72):
                    aggregated_moer_6hrs = 0
                    for y in range(x, x+72):
                        aggregated_moer_6hrs += monthdata[y]['value']
                        aggregated_moer_times = monthdata[y]['point_time']
                    MOER_month.append(aggregated_moer_6hrs//72)
                    MOER_month_time.append(aggregated_moer_times)
                Neat_month = pd.DataFrame([MOER_month_time,MOER_month]).T
                Neat_month.columns = ['Time (UTC)' , 'Marginal Carbon Intensity']
            else:
                msg2 = "Warning, WattTime data for this region is missing records.  Please be sure to inspect point times."
                counter = int(round((len(monthdata)/120 - 1), 0))
                print(counter)
                for x in range(0,len(monthdata), counter):
                    aggregated_moer_6hrs = 0
                    try:
                        for y in range(x, x+counter):
                            aggregated_moer_6hrs += monthdata[y]['value']
                            aggregated_moer_times = monthdata[y]['point_time']
                    except:
                        break
                    MOER_month.append(aggregated_moer_6hrs//counter)
                    MOER_month_time.append(aggregated_moer_times)
                Neat_month = pd.DataFrame([MOER_month_time,MOER_month]).T
                Neat_month.columns = ['Time (UTC)' , 'Marginal Carbon Intensity']
                print(f"MOER_month = {MOER_month}")
        except:
            msg2 = "Warning, WattTime data for this region is missing records.  Please be sure to inspect point times.  Some images may not render as a result."
            print('found exception')
            pass

        try:
            msg2 = msg2
        except:
            msg2 = ''
    # Percent times 0g carbon emission in a day
    count_moer_day = 0
    count_zero_day = 0   
    for i in daydata:
        if int(i["value"]) == 0:
            count_zero_day+=1    
        count_moer_day+=1

    day_zero = round((count_zero_day/count_moer_day)*100, 2)

    # Percent times 0g carbon emission in a week
    count_moer_week = 0
    count_zero_week = 0
    for i in weekdata:
        if int(i["value"]) == 0:
            count_zero_week+=1    
        count_moer_week+=1

    week_zero = round((count_zero_week/count_moer_week)*100, 2)

    # Percent times 0g carbon emission in a month
    count_moer_month = 0
    count_zero_month = 0
    for i in monthdata:
        if int(i["value"]) == 0:
            count_zero_month+=1    
        count_moer_month+=1

    month_zero = round((count_zero_month/count_moer_month)*100, 2)

    # For passing data to html
    data['day'] = day_zero
    data['week'] = week_zero
    data['month'] = month_zero
    data['num_day_0'] = count_zero_day
    data['num_week_0'] = count_zero_week
    data['num_month_0'] = count_zero_month
    data['avg_day'] = round(statistics.mean(MOER_day),0)
    data['avg_week'] = round(statistics.mean(MOER_week),0)
    data['avg_month'] = round(statistics.mean(MOER_month), 0 )
 
    # Bar plots - day, week and month
    day_plot = px.line(data_frame=Neat_day,x='Time (UTC)',
                        y='Marginal Carbon Intensity',
                        title='Carbon Intesity (CO<sub>2</sub>/MWh) over Time',
                        template='none')
    day_plot_layer_2 = go.Scatter(x=Neat_day['Time (UTC)'],
                        y=Neat_day['Marginal Carbon Intensity'], 
                        mode='lines', 
                        connectgaps=True, 
                        line_color='#077FFF',
                        hoverinfo='skip',
                        name='Intensity')
    day_plot.add_trace(day_plot_layer_2)
    day_plot.update_layout(showlegend=False)
    day_plot.update_xaxes(showspikes=True)
    day_plot.update_yaxes(showspikes=True)
    day_plot.update_xaxes(visible=False)
    week_plot = px.line(data_frame=Neat_week,x='Time (UTC)',
                        y='Marginal Carbon Intensity',
                        title='Average Carbon Intesity (CO<sub>2</sub>/MWh) over Aggregated Time: Week', 
                        template='none')
    week_plot_layer_2 = go.Scatter(x=Neat_week['Time (UTC)'], 
                        y=Neat_week['Marginal Carbon Intensity'], 
                        mode='lines', connectgaps=True, 
                        line_color='#077FFF',
                        hoverinfo='skip',
                        name='Intensity')
    week_plot.add_trace(week_plot_layer_2)    
    week_plot.update_layout(showlegend=False)
    week_plot.update_xaxes(showspikes=True)
    week_plot.update_yaxes(showspikes=True)
    week_plot.update_xaxes(visible=False)


    html_day_plot = plotly.io.to_html(day_plot)
    html_week_plot = plotly.io.to_html(week_plot)
    try:
        month_plot = px.line(data_frame=Neat_month,x='Time (UTC)',
                            y='Marginal Carbon Intensity',
                            title='Average Carbon Intesity (CO<sub>2</sub>/MWh) over Aggregated Time: Month',
                             template='none')
        month_plot_layer_2 = go.Scatter(x=Neat_month['Time (UTC)'],
                                         y=Neat_month['Marginal Carbon Intensity'],
                                          mode='lines', connectgaps=True,
                                           line_color='#077FFF',
                                           hoverinfo='skip',
                                           name='Intensity')
        month_plot.add_trace(month_plot_layer_2)
        month_plot.update_layout(showlegend=False)
        month_plot.update_xaxes(showspikes=True)
        month_plot.update_yaxes(showspikes=True)
        month_plot.update_xaxes(visible=False)
        html_month_plot = plotly.io.to_html(month_plot)

        if len(monthdata) < 8000:
            msg = monthdata[0]['frequency']
            return render_template('region_bad_freq.html', 
                                    plot1=html_day_plot, 
                                    plot2=html_week_plot, 
                                    plot3=html_month_plot, 
                                    data=data, 
                                    msg=msg)
        else:
            return render_template('region.html', 
                                    plot1=html_day_plot , 
                                    plot2=html_week_plot , 
                                    plot3=html_month_plot, 
                                    data=data, 
                                    msg=msg2)
    except:
        if len(monthdata) < 8000:
            msg = monthdata[0]['frequency']
            return render_template('region_bad_freq.html', 
                                    plot1=html_day_plot , 
                                    plot2=html_week_plot , 
                                    data=data, 
                                    msg=msg)
        else:
            return render_template('region.html', 
                                    plot1=html_day_plot , 
                                    plot2=html_week_plot , 
                                    data=data, 
                                    msg=msg2)


    
@ci_bp.route('/get_sum_data', methods=["GET", "POST"])
def get_sum_data():
    '''
    Retrieve dataframe, format it, and then utilize its inference start and endtimes to pull carbon and wattage expenditure data from WattTime
    Calculate sum of carbon emissions and wattage level before outputting results
    '''
    filename = str(request.args.get("filename", None))
    starttime = request.args.get("starttime", None)
    endtime = request.args.get("endtime", None)
    ba = request.args.get("ba", None)
    gpuutil_flag = int(request.args.get("gpuutil", 0))

    AZ_data = gather_azmonitor(filename, gpuutil_flag)
    print(filename)

    #pull data from WattTime & transform into dataframe
    rsp = gather_watttime(ba, starttime, endtime)
    data = json.loads(rsp.text)
    WT_data = pd.json_normalize(data).dropna()
    WT_data = WT_data.sort_index(ascending=False)
    MWh_Az = AZ_data['Total'].dropna()
    
    #power per time delta
    MegaWatth_per_five = MWh_Az*2.77778e-10
    # total power in time window
    MegaWatth_total = sum(MegaWatth_per_five)
    # pounds of carbon per time delta
    resource_emissions = MegaWatth_per_five*WT_data['value'].dropna()
    #print(resource_emissions)
    # total pounds of carbon in time window
    resource_emissions_total = sum(resource_emissions.dropna())
    print(len(WT_data['value']))

    return {"Total Carbon Emission (lbs)" : resource_emissions_total , "Total Energy Consumed (MWh)" : MegaWatth_total}




@ci_bp.route('/get_peak_data', methods=["GET", "POST"])
def get_peak_data():
    '''
    Retrieve dataframe, format it, and then utilize its inference start and endtimes to pull carbon and wattage expenditure data from WattTime
    Find and save peak emissions and wattage expenditure times as well as their values in a dictionary
    '''
    filename = str(request.args.get("filename", None))
    starttime = request.args.get("starttime", None)
    endtime = request.args.get("endtime", None)
    ba = request.args.get("ba", None)
    gpuutil_flag = int(request.args.get("gpuutil", 0))

    AZ_data = gather_azmonitor(filename, gpuutil_flag)

    rsp = gather_watttime(ba, starttime, endtime)
    data = json.loads(rsp.text)


    WT_data = pd.json_normalize(data).dropna()
    WT_data = WT_data.sort_index(ascending=False)
    MWh_Az = AZ_data['Total'].dropna()
    
    #power per time delta
    MegaWatth_per_five = MWh_Az*2.77778e-10

    # pounds of carbon per time delta
    resource_emissions = MegaWatth_per_five*WT_data['value'].dropna()
    print(resource_emissions)


    plot_data = {'resource_emissions' : resource_emissions, 'Time' : AZ_data['Time'], 'Energy' : MegaWatth_per_five}
    df = pd.DataFrame(plot_data)
    #peak id
    peak_c = f"{round(max(resource_emissions), 3)} lbs/per 5 minutes at {df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))]}"
    peak_e = f"{round(max(MegaWatth_per_five), 6)} MWh/per 5 minutes at {df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]}"
    peak_dict = {"Peak Carbon Emission Time" : {"Time_stamp" : df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))] , "Explaination" : peak_c} , "Peak Energy Consumption Time" : {"Time-stamp" : df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))], "Explaination" : peak_e}}
    
    peak_data = {}
    peak_data["peak_carbon_timestamp"] = df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))]
    peak_data["peak_carbon_time"] = df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))]
    peak_data["peak_carbon_date"] = df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))]
    peak_data["peak_carbon_val"] = round(max(resource_emissions), 3)
    peak_data["peak_energy_timestamp"] = df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]
    peak_data["peak_energy_time"] = df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]
    peak_data["peak_energy_date"] = df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]
    peak_data["peak_energy_val"] = round(max(MegaWatth_per_five), 6)

    return peak_dict



@ci_bp.route('/get_timeseries_data', methods=["GET", "POST"])
def get_timeseries_data():
    filename = str(request.args.get("filename", None))
    gpuutil_flag = int(request.args.get("gpuutil", None))
    starttime = request.args.get("starttime", None)
    endtime = request.args.get("endtime", None)
    ba = request.args.get("ba", None)
    data_url = 'https://api2.watttime.org/v2/data'

    AZ_data = gather_azmonitor(filename, gpuutil_flag)
    az_file = gather_azmonitor(filename, gpuutil_flag)
    
    #try:
    rsp = gather_watttime(ba, starttime, endtime)
    data = json.loads(rsp.text)


    WT_data = pd.json_normalize(data).dropna()
    WT_data = WT_data.sort_index(ascending=False)
    MWh_Az = AZ_data['Total'].dropna()
    
    #power per time delta
    MegaWatth_per_five = MWh_Az*2.77778e-10
    # total power in time window
    MegaWatth_total = sum(MegaWatth_per_five)
    # pounds of carbon per time delta
    resource_emissions = MegaWatth_per_five*WT_data['value'].dropna()
    # total pounds of carbon in time window
    carbon_total = sum(resource_emissions.dropna())
    print(len(WT_data['value']))

    #stats
    avg = format(statistics.mean(resource_emissions.dropna()), '.4g')
    #real-time MOER
    ba = request.args.get("ba", None)
    index_url  = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    realtime_rsp = requests.get(index_url, headers=headers, params=params)
    realtime_data = json.loads(realtime_rsp.text)
    realtime_data = pd.json_normalize(realtime_data)
    
    plot_data = {'resource_emissions' : resource_emissions, 'Time' : AZ_data['Time'], 'Energy' : MegaWatth_per_five}
    df = pd.DataFrame(plot_data)

    #peak id
    peak_threshold = 0.05
    peak_span = df['Time'].iloc[pd.Series(resource_emissions.loc[resource_emissions > (max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)]


    peak = f"{round(max(resource_emissions), 3)} lbs/per 5 minutes at {df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))]}"
    #peak_e = f"{round(max(MegaWatth_per_five), 6)} MWh at {df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]}"

    Carbon = df['resource_emissions']


    #plotting

    emissions_plot_custom_layer = go.Scatter(x=df['Time'][:len(df['resource_emissions'])], 
                                            y=Carbon, 
                                            mode='lines', 
                                            connectgaps=True ,
                                            hoverinfo='skip', 
                                            line_color='#077FFF',
                                            name='Emissions')
    peak_emissions_index = pd.Series(resource_emissions.loc[resource_emissions > (max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)
    emissions_plot_peak_layer = go.Scattergl(x=peak_span, 
                                            y=Carbon.iloc[peak_emissions_index],
                                            mode='markers', 
                                            marker_color='rgb(270,0,0)',
                                            marker={'size':7},
                                            name='Highest 5%' )
    energy_plot_custom_layer = go.Scattergl(x=df['Time'], 
                                            y=df['Energy'], 
                                            mode='lines', 
                                            connectgaps=True ,
                                            hoverinfo='skip', 
                                            line_color='#077FFF', 
                                            name='Data' )
                                            
    peak_energy_x = [df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))], df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]]                                        
    peak_energy_y = [df['Energy'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))], df['Energy'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]]
    energy_plot_peak_layer = go.Scattergl(x=peak_energy_x,
                                        y=peak_energy_y,
                                        mode='markers', 
                                        marker_color='rgb(270,0,0)', 
                                        marker={'size':7} , 
                                        name='Max Consuption')

    df.columns = ['Carbon Emitted (lbs)', 'Time', 'Energy (MWh)']
    try:
        layout = dict(
        xaxis=dict(
            tickvals = df['Time'][::int(len(df['Time'])/4)],
            ticktext=df['Time'][::int(len(df['Time'])/4)],
            tickangle=0,
        )
        
        )
    except:
        layout = dict(
        xaxis=dict(tickangle=0,
        )
        
        )
    
    emissions_plot = px.line(df, x='Time', 
                            y='Carbon Emitted (lbs)', 
                            title='Emissions (lbs) by Time', 
                            template='none')
    emissions_plot.add_trace(emissions_plot_custom_layer)


    try:
        try:
            time_1_choice = df['Time'][0]
            print(time_1_choice)
            t1 = time_1_choice.split(" ")[1]
            print(t1)
        except:
            try:
                FMT = '%H:%M:%S'
                time_1_choice = dt.strftime(time_1_choice, FMT)
                print(time_1_choice)
                t1 = time_1_choice
            except:
                FMT = '%H:%M'
                t1 = time_1_choice
    except:
        msg= 'check input time accuracy and format. If problem persists please contact support team.'
        return make_response(render_template('data_error.html', msg=msg), 404)
    try:
        time_2_choice = df['Time'][len(df['Time'])-1]
        t2 = time_2_choice.split(" ")[1]
        print(f"t2 = {t2}")
    except:
        try:
            try:
                FMT = '%H:%M:%S'
                time_2_choice = dt.strftime(time_2_choice, FMT)
                t2 = time_2_choice
                print(f"t2 = {t2}")
            except:
                FMT = '%H:%M'
                t2 = time_2_choice
                print(f"t2 = {t2}")
        except:
            msg= 'check input time accuracy and format. If problem persists please contact support team.'
            return make_response(render_template('data_error.html', msg=msg), 404)


    try:   
        try:
            print(f"t1 = {t1}")
            print(f"t2 = {t2}")
            FMT = '%H:%M:%S'
            tdelta = dt.strptime(t2, FMT) - dt.strptime(t1, FMT)
        except:
            print(f"t1 = {t1}")
            print(f"t2 = {t2}")
            FMT = '%H:%M'
            tdelta = dt.strptime(t2, FMT) - dt.strptime(t1, FMT)
        base = tdelta
        print(f"tdelta = {tdelta}")
        try:
            tdelta = str(tdelta).split(",")[1]
        except:
            tdelta = base
        print(f"tdelta = {tdelta}")
    except:
        try:
            try:
                FMT = '%Y%m%d %H:%M:%S'
                tdelta = dt.strptime(df['Time'][len(df['Time'])-1], FMT) - dt.strptime(df['Time'][0], FMT)
            except:
                FMT = '%Y%m%d %H:%M'
                tdelta = df['Time'][len(df['Time'])-1] - df['Time'][0]
        except:
            try:
                FMT = '%Y-%m-%dT%H:%M:%SZ'
                tdelta = dt.strptime(df['Time'][len(df['Time'])-1], FMT) - dt.strptime(df['Time'][0], FMT)
            except:
                FMT = '%Y-%m-%dT%H:%M:%SZ'
                tdelta = df['Time'][len(df['Time'])-1] - df['Time'][0]

        base = tdelta
        print(f"tdelta = {tdelta}")
        try:
            print(str(tdelta).split(",")[0])
            if str(tdelta).split(",")[0] == '0':
                
                tdelta = str(tdelta).split(",")[1]
            else:
                tdelta = str(tdelta)

        except:
            tdelta = base
        print(f"tdelta = {tdelta}")
        


    emissions_plot.add_trace(emissions_plot_peak_layer)
    emissions_plot.update_xaxes(showspikes=True)
    emissions_plot.update_yaxes(showspikes=True)
    emissions_plot.update_layout(showlegend=False)
    emissions_plot.update_layout(layout)
    emissions_plot.update_layout(title_font_size=26)

    #emissions_plot.add_trace(figl)

    energy_plot = px.line(df, x='Time', y='Energy (MWh)', 
                        title='Energy Consumed (MWh) by Time ', 
                        template='none')
    energy_plot.add_trace(energy_plot_custom_layer)
    energy_plot.add_trace(energy_plot_peak_layer)
    energy_plot.update_xaxes(showspikes=True)
    energy_plot.update_yaxes(showspikes=True)
    energy_plot.update_layout(showlegend=False) 
    energy_plot.update_layout(layout)
    energy_plot.update_layout(title_font_size=26)
    #print(df)


    abbrev = request.args.get("ba", None)
    print(abbrev)
    moer_value = get_realtime_data(abbrev)
    percent_zeros = get_percent_zero(abbrev)


    page_data={}

    page_data['moer_value'] = moer_value["moer"]
    page_data['percent_zeros'] = percent_zeros
    page_data['name'] = ba
    
    # if GPUUtil exists, save it in the dict
    if gpuutil_flag:
        gpu_util = AZ_data['GPUUtil'].mean()
        page_data['gpu_util'] = format(gpu_util, '.4g')
    #token = get_token()

    data_url = 'https://api2.watttime.org/v2/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': abbrev, 
            'starttime': starttime, 
            'endtime': endtime}
    rsp = requests.get(data_url, headers=headers, params=params)
    
    vals  = rsp.json()

    # To plot the daily, weekly and monthly carbon emission trends

    if vals[0]['frequency'] != 300:
        daydata = vals[:int(round((len(vals)/30),0))]
        print(daydata[:3])
        print(len(daydata))


        MOER_day_time = []
        MOER_day = []
        for x in range(0,len(daydata),int(round((len(daydata)/24),0))):
            val = daydata[x]['value']
            time = daydata[x]['point_time']
            MOER_day.append(val)
            MOER_day_time.append(time)
        Neat_day = pd.DataFrame([MOER_day_time,MOER_day]).T
        Neat_day.columns = ['Time (UTC)' , 'Region Intensity']  


    else:
    # When frequency == 300
        daydata = vals       # 24 hrs in day * 60 mins in an hr / 5 min interval


        # Getting MOER values at 5-min interval in a day 
        MOER_day_time = []
        MOER_day = []
        for x in range(len(daydata)):
            val = daydata[x]['value']
            time = daydata[x]['point_time']
            MOER_day.append(val)
            MOER_day_time.append(time)
        Neat_day = pd.DataFrame([MOER_day_time,MOER_day]).T
        Neat_day.columns = ['Time (UTC)' , 'Region Intensity']



    # Percent times 0g carbon emission in a day
    count_moer_day = 0
    count_zero_day = 0   
    for i in daydata:
        if int(i["value"]) == 0:
            count_zero_day+=1    
        count_moer_day+=1

    day_zero = round((count_zero_day/count_moer_day)*100, 2)



    # For passing data to html
    page_data['day'] = day_zero
    page_data['num_day_0'] = count_zero_day
    page_data['avg_day'] = round(statistics.mean(MOER_day),0)

    descend = Neat_day['Time (UTC)'].sort_index(ascending=False)
    descend = descend.reset_index()

    df['Time (UTC)'] = descend['Time (UTC)']
    df['Region Intensity'] = Neat_day['Region Intensity']


    # plots
    large_CI_plot = px.line(data_frame=Neat_day,x='Time (UTC)',
                            y='Region Intensity',
                            title='Region Intensity (<span><sup>lbs</sup>/<sub>MWh</sub></span>) by Time', 
                            template='none')
    large_CI_plot_custome_layer = go.Scatter(x=Neat_day['Time (UTC)'], 
                                            y=Neat_day['Region Intensity'], 
                                            mode='lines', 
                                            connectgaps=True ,
                                            hoverinfo='skip', 
                                            line_color='#077FFF' ,
                                            name='Data')
    large_CI_plot.add_trace(large_CI_plot_custome_layer)
    large_CI_plot.update_layout(showlegend=False)
    large_CI_plot.update_xaxes(showspikes=True)
    large_CI_plot.update_yaxes(showspikes=True)
    large_CI_plot.update_layout(title_font_size=26)


    html_emissions_plot = plotly.io.to_html(emissions_plot)
    html_energy_plot = plotly.io.to_html(energy_plot)
    html_large_CI_plot = plotly.io.to_html(large_CI_plot)

    page_data['peak'] = peak
    page_data['ba'] = ba
    page_data['total_carbon'] =format(carbon_total, '.4g')
    page_data['energy'] = format(MegaWatth_total*1000, '.4g')
    page_data['peak_e_max'] = format(max(MegaWatth_per_five)*1000, '.4g')
    page_data['peak_e_time'] = df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]
    page_data['peak_c_max'] = format(max(resource_emissions), '.4g')
    page_data['peak_c_time'] = df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))]
    page_data['realtime_data'] = realtime_data.values[0,3]
    page_data['avg'] = avg
    page_data['length'] = tdelta
    page_data['AZ'] = request.args.get("AZ_Region", None)


    mini_C_plot = go.Scatter(x=df['Time (UTC)'][:len(df['Carbon Emitted (lbs)'])], 
                            y=Carbon, 
                            mode='lines', 
                            connectgaps=True, 
                            line_color='#077FFF',
                            name='Emissions')
    mini_peak_C_x = df['Time (UTC)'].iloc[pd.Series(resource_emissions.loc[resource_emissions > (max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)]
    mini_peak_C_y = Carbon.iloc[pd.Series(resource_emissions.loc[resource_emissions > (max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)]
    mini_C_peak_layer = go.Scattergl(x= mini_peak_C_x,
                                    y= mini_peak_C_y,
                                    mode='markers', 
                                    marker_color='rgb(270,0,0)', 
                                    marker={'size':6} ,
                                    name='Highest 5%' )
    mini_E_plot = go.Scattergl(x=df['Time (UTC)'], 
                                y=df['Energy (MWh)'], 
                                mode='lines', 
                                connectgaps=True, 
                                line_color='#077FFF', 
                                name='Consumption' )
    mini_peak_E_x = [df['Time (UTC)'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))], 
                        df['Time (UTC)'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]]
    mini_peak_E_y = [df['Energy (MWh)'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))], 
                        df['Energy (MWh)'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]]                      
    mini_E_peak_layer = go.Scattergl(x=mini_peak_E_x, 
                                    y=mini_peak_E_y,
                                    mode='markers', 
                                    marker_color='rgb(270,0,0)', 
                                    marker={'size':6}, 
                                    name='Max Consuption')
    CI_plot = go.Scatter(x=Neat_day['Time (UTC)'], 
                        y=Neat_day['Region Intensity'], 
                        mode='lines', 
                        connectgaps=True, 
                        line_color='#077FFF', 
                        name='Intensity')
    CI_peak_layer = go.Scattergl(x=df['Time (UTC)'].iloc[pd.Series(resource_emissions.loc[resource_emissions > (max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)], 
                                y=Neat_day['Region Intensity'].iloc[pd.Series(resource_emissions.loc[resource_emissions > (max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)],
                                mode='markers', 
                                marker_color='rgb(270,0,0)', 
                                marker={'size':6} ,
                                name='Highest 5%' )
    
    # Initialize figure with subplots
    three_mini_plots = make_subplots(
        rows=1, cols=3,
        column_titles=['Emissions (lbs) by Time','Energy Consumed (MWh) by Time',"Region Intensity (<span><sup>lbs</sup>/<sub>MWh</sub></span>) by Time"],
        x_title='Time (UTC)'
        )
    three_mini_plots.append_trace(mini_C_plot, 1, 1)
    three_mini_plots.append_trace(mini_C_peak_layer, 1, 1)
    three_mini_plots.append_trace(mini_E_plot, 1, 2)
    three_mini_plots.append_trace(mini_E_peak_layer, 1, 2)
    three_mini_plots.update_layout(showlegend=False,template=None)
    three_mini_plots.append_trace(CI_plot, 1, 3)
    #fig82.append_trace(CI_peak_layer, 1, 3)
    three_mini_plots.update_xaxes(spikemode='across+marker')
    three_mini_plots.update_yaxes(spikemode='across+marker')


    html_three_mini_plots = plotly.io.to_html(three_mini_plots)

    
    az_region = request.args.get("AZ_Region", None)
    az_coords = get_az()

    
    SKU_table = get_SKU_table()
    sensitive_check_box = request.form.get('sensitive', 'on')
    desired_GPU = request.form.get('gpu_type', 'nada')
    filter_list = Law_filter(SKU_table, sensitive_check_box, az_region)
    filtered_regions_list = Gpu_filter(filter_list, desired_GPU)

    all_region_counterfactual = []

    for n in filtered_regions_list:

        Key = "displayName"
        Region_Name = n
        #token = get_token()
        

    # finding coords for the passed AZ_region
        
        areaDict = next(filter(lambda x: x.get(Key) == Region_Name, az_coords), None)
        if areaDict == None:
            msg= 'use a different region to get a carbon analysis. There was no pre-paired Azure Data center available.'
            return make_response(render_template('data_error.html', msg=msg), 404 )

            
        
        
        #calling coords of AZ region
        data_center_latitude = areaDict['metadata']['latitude']
        data_center_longitude = areaDict['metadata']['longitude']


        data_url = 'https://api2.watttime.org/v2/data'
        headers = {'Authorization': 'Bearer {}'.format(token)}
        params = {'latitude': data_center_latitude, 'longitude': data_center_longitude, 
            'starttime': starttime, 
            'endtime': endtime }
        rsp = requests.get(data_url, headers=headers, params=params)
        data_check = str.strip(rsp.text[2:7])
        print(data_check)
        if data_check == 'error':
            msg= 'check query parameters. WattTime response contained an error'
            return make_response(render_template('data_error.html',msg=msg), 400 )
        elif len(data_check) == 0:
            msg= 'check query parameters. No WattTime response returned.'
            return make_response(render_template('data_error.html', msg=msg), 404)
        rsp_data = json.loads(rsp.text)


        WT_data_counterfactual = pd.json_normalize(rsp_data)
        WT_data_counterfactual = WT_data_counterfactual.sort_index(ascending=False)
        
        #power per time delta
        MegaWatth_per_five_counterfactual = MWh_Az*2.77778e-10
        # pounds of carbon per time delta
        Carbon_counterfactual = MegaWatth_per_five_counterfactual*WT_data_counterfactual['value']
        #print(Carbon_counterfactual)
        # total pounds of carbon in time window
        Carbon_counterfactual_total = sum(Carbon_counterfactual.dropna())
        print(len(WT_data_counterfactual['value']))
        print(f"New total is {Carbon_counterfactual_total} using {Region_Name} ")
        Carbon_counterfactual_total_region = [Carbon_counterfactual_total , Region_Name]
        all_region_counterfactual.append(Carbon_counterfactual_total_region)

    all_region_counterfactual_df = pd.DataFrame(all_region_counterfactual)
    all_region_counterfactual_df.columns = ['Sum', 'Name']
    #print(all_region_counterfactual_df)
    minimum_index = all_region_counterfactual_df.loc[all_region_counterfactual_df['Sum']==min(all_region_counterfactual_df['Sum'])].index
    min_counterfactual = all_region_counterfactual_df.iloc[pd.Series(minimum_index)]
    min_counterfactual = min_counterfactual.reset_index()
    suggested_region_displayName = str(min_counterfactual['Name'])
    suggested_region_displayName  = suggested_region_displayName.split(":")[0]
    suggested_region_displayName  = suggested_region_displayName.split("Name")[0]
    suggested_region_displayName  = suggested_region_displayName.split("0")[1]


    page_data['option'] = format(float(min_counterfactual['Sum'][0]), '.4g')
    page_data['pair'] = suggested_region_displayName


    delta_carbon_percent = ((float(page_data['total_carbon']) - float(page_data['option']))/float(page_data['total_carbon']))*100
    page_data['delta'] = format(float(delta_carbon_percent), '.4g')
    print(delta_carbon_percent)
    print(page_data['delta'])


    times_vals = [3,6,9,12,15]
    try:
        FMT = ("%Y-%m-%dT%H:%M:%S%z")
        format_starttime = dt.strptime(str(starttime), FMT)
        format_endtime = dt.strptime(str(endtime), FMT)
    except:
        FMT = ("%Y-%m-%dT%H:%M:%S")
        format_starttime = dt.strptime(str(starttime), FMT)
        format_endtime = dt.strptime(str(endtime), FMT)

    time_MOER = []
    time_carbon_counterfactual = []

    try:
        for k in times_vals:
            new_start = (format_starttime + datetime.timedelta(hours=k)).isoformat()
            print(f"new_start = {new_start}")
            new_end = (format_endtime + datetime.timedelta(hours=k)).isoformat()
            print(f"new_end = {new_end}")


            Key = "displayName"
            Region_Name = az_region
            #token = get_token()
            

        # finding coords for the passed AZ_region
            
            areaDict = next(filter(lambda x: x.get(Key) == Region_Name, az_coords), None)
            if areaDict == None:
                msg= 'use a different region to get a carbon analysis. There was no pre-paired Azure Data center available.'
                return make_response(render_template('data_error.html', msg=msg), 404 )


            #calling coords of AZ region
            data_center_latitude = areaDict['metadata']['latitude']
            data_center_longitude = areaDict['metadata']['longitude']

            try:
                data_url = 'https://api2.watttime.org/v2/data'
                headers = {'Authorization': 'Bearer {}'.format(token)}
                params = {'latitude': data_center_latitude, 'longitude': data_center_longitude, 
                    'starttime': new_start, 
                    'endtime': new_end }
                rsp = requests.get(data_url, headers=headers, params=params)
            except:
                break
            data_check = str.strip(rsp.text[2:7])
            print(data_check)
            if data_check == 'error':
                msg= 'check query parameters. WattTime response contained an error'
                return make_response(render_template('data_error.html',msg=msg), 400 )
                
            elif len(data_check) == 0:
                msg= 'check query parameters. No WattTime response returned.'
                return make_response(render_template('data_error.html', msg=msg), 404)
            
            try:
                data4 = json.loads(rsp.text)
                #print(f"data4 = {data4}")
                time_MOER.append(data4[-1])
            except:
                print('passed but can not display')

            


            WT_data3 = pd.json_normalize(data4)
            WT_data3 = WT_data3.sort_index(ascending=False)
            #print(f"WT_data3 = {WT_data3}")
            MWh_Az3 = AZ_data['Total']
            
            #power per time delta
            MegaWatth_per_five3 = MWh_Az3*2.77778e-10
            # pounds of carbon per time delta
            MOER_Az3 = MegaWatth_per_five3*WT_data3['value']
            if len(MOER_Az3.dropna()) < len(az_file['Total']):
                break
            #print(f"MOER_Az3 = {MOER_Az3}")
            # total pounds of carbon in time window
            MOER_Az_day3 = sum(MOER_Az3.dropna())
            print(len(WT_data3['value']))
            print(f"New total is {time_carbon_counterfactual} using {Region_Name} ")
            MOER_Az_day3 = MOER_Az_day3

            time_carbon_counterfactual.append(MOER_Az_day3)

        
        time_carbon_counterfactual_total = pd.DataFrame(time_carbon_counterfactual)
        time_carbon_counterfactual_total.columns = ['Sum']

        
        min_time_carbon_counterfactual = time_carbon_counterfactual_total.iloc[pd.Series(time_carbon_counterfactual_total.loc[time_carbon_counterfactual_total['Sum']==min(time_carbon_counterfactual_total['Sum'])].index)]

        shift_amount = pd.DataFrame(times_vals).iloc[pd.Series(min_time_carbon_counterfactual.loc[min_time_carbon_counterfactual['Sum']==min(min_time_carbon_counterfactual['Sum'])].index)]
        shift_amount.columns = ['hours']
        page_data['time_carbon'] = min_time_carbon_counterfactual['Sum']

        time_carbon_percent = ((float(page_data['total_carbon']) - float(page_data['time_carbon']))/float(page_data['total_carbon']))*100
        page_data['delta_shift'] = format(float(time_carbon_percent), '.4g')
        page_data['hour_shift'] = format(float(shift_amount['hours']), '.4g')
    except:
        pass


    if gpuutil_flag == 1:
        return render_template( 'report_final_util.html', data= page_data , plot1=html_emissions_plot , plot2 = html_energy_plot , plot3=html_large_CI_plot ,plot4=html_three_mini_plots)
    else:
        return render_template( 'report_final.html', data= page_data , plot1=html_emissions_plot , plot2 = html_energy_plot , plot3=html_large_CI_plot ,plot4=html_three_mini_plots) 




@ci_bp.route('/get_timeseries_table_data', methods=["GET", "POST"])
def get_timeseries_table_data():
    token = get_token()
    filename = request.args.get("filename", None)
    checker = str(filename)
    if checker[-3:] == 'csv':
        az_file = pd.read_csv(checker).dropna()
        if len(az_file.columns) != 3:
            if len(az_file.columns) != 2:
                msg = 'use either a .xlsx, .csv, or .json file with the  proper column formatting.'
                return make_response(render_template('data_error.html',msg=msg), 411 ) 
            else:
                az_file.columns = ['Time', 'Total']
        else:
            az_file.columns = ['Index','Time', 'Total']

        print(az_file['Time'].dtype)
        print(az_file['Total'].dtype)
        
    
        try:
            assert az_file['Time'].dtype == 'object'

        except:
            msg = 'use either a .xlsx, .csv, or .json file with the proper data type formats.'
            return make_response(render_template('data_error.html',msg=msg), 412 ) 
    
    elif checker[-4:] == 'json':
        Monitor_data = json.load(open(checker))
        az_file = pd.DataFrame(Monitor_data['value'][0]['timeseries'][0]['data']).dropna()
        az_file.columns = ['Time', 'Total']
        print(az_file[:3])

    elif checker[-4:] == 'xlsx':
        az_file = pd.read_excel(checker)[10:].dropna()
        #print(az_file)
        if len(az_file.columns) != 3:
            if len(az_file.columns) != 2:
                msg = 'use either a .xlsx, .csv, or .json file with the proper column formatting.'
                return make_response(render_template('data_error.html',msg=msg), 411 ) 
            else:
                az_file.columns = ['Time', 'Total']
                az_file = az_file.reset_index()
                print(az_file)
                print(az_file['Time'])
                pd.to_numeric(az_file['Total'])
        else:
            az_file.columns = ['Index','Time', 'Total']
        #print(az_file)
        print(az_file['Time'].dtype)
        print(az_file['Total'].dtype)

    else:
        msg = 'input a valid .xlsx, .csv, or .json file'
        return make_response(render_template('data_error.html', msg=msg), 413 ) 
    
    try:
        AZ_data = az_file
        time_1_choice = AZ_data['Time'][int(len(AZ_data)/2)]
        print(f"time_1_choice try1 = {time_1_choice}")
        try:
            t1 = time_1_choice.split(" ")[1]
        except:
            try:
                print('t1 except try')
                FMT = '%H:%M:%S'
                time_1_choice = dt.strftime(time_1_choice, FMT)
                print(f"time_1_choice = {time_1_choice}")
                t1 = time_1_choice
            except:
                print('t1 except except')
                FMT = '%H:%M'
                t1 = time_1_choice
        
        time_2_choice = AZ_data['Time'][int(len(AZ_data)/2)+1]
        try:
            print('t2 try')
            t2 = time_2_choice.split(" ")[1]
        except:
            try:
                print('t2 except try')
                FMT = '%H:%M:%S'
                time_2_choice = dt.strftime(time_2_choice, FMT)
                print(f"time_2_choice = {time_2_choice}")
                t2 = time_2_choice
            except:
                print('except except t2')
                FMT = '%H:%M'
                print(f"time_2_choice = {time_2_choice}")
                t2 = time_2_choice
    
        try:
            set1='9:40:00'
            set2='9:45:00'
            FMT = '%H:%M:%S'
            FMT2 = '%Y-%m-%dT%H:%M:%SZ'
            try:
                tdelta = dt.strptime(t2, FMT) - dt.strptime(t1, FMT)
            except:
                tdelta = dt.strptime(t2, FMT2) - dt.strptime(t1, FMT2)

            bench = dt.strptime(set2, FMT) - dt.strptime(set1, FMT)

            print(f"bench = {bench}")
            print(f"tdelta = {tdelta}")
        except:
            print('except')
            set1='9:40'
            set2='9:45'
            FMT = '%H:%M'
            bench = dt.strptime(set2, FMT) - dt.strptime(set1, FMT)
            print(f"bench = {bench}")
            tdelta = dt.strptime(t2, FMT) - dt.strptime(t1, FMT)

            print(f"tdelta = {tdelta}")

        if tdelta != bench:
            msg = 'use either a .xlsx, .csv, or .json file with 5 min time aggregation.'
            return make_response(render_template('data_error.html',msg=msg), 415 ) 
        print(filename)
        starttime = request.args.get("starttime", None)
        endtime = request.args.get("endtime", None)
        ba = request.args.get("ba", None)
        data_url = 'https://api2.watttime.org/v2/data'
        headers = {'Authorization': 'Bearer {}'.format(token)}
        params = {'ba': ba, 
            'starttime': starttime, 
            'endtime': endtime}
        rsp = requests.get(data_url, headers=headers, params=params)
        data_check = str.strip(rsp.text[2:7])
        print(f"check = {data_check}")
        if data_check == 'error':
            msg= 'check query parameters. WattTime response contained an error'
            return make_response(render_template('data_error.html',msg=msg), 400 )
        elif len(data_check) == 0:
            msg= 'check query parameters. No WattTime response returned.'
            return make_response(render_template('data_error.html', msg=msg), 404)
        data = json.loads(rsp.text)


        WT_data = pd.json_normalize(data).dropna()
        WT_data = WT_data.sort_index(ascending=False)
        MWh_Az = AZ_data['Total'].dropna()
        
        #power per time delta
        MegaWatth_per_five = MWh_Az*2.77778e-10
        # pounds of carbon per time delta
        resource_emissions = MegaWatth_per_five*WT_data['value'].dropna()
        #print(resource_emissions)


        plot_data = {'resource_emissions' : resource_emissions, 'Time' : AZ_data['Time'], 'Energy' : MegaWatth_per_five}
        df = pd.DataFrame(plot_data)
        
        #peak id
       
    
        df.columns = ['Carbon Emitted (lbs)', 'Time', 'Energy (MWh)']
        print(f"the DataFrame v1 is {df[:10]}")

        time_series_data = df.to_dict()
        print(time_series_data)


    except:
        msg= 'check that query parameters match file values.'
        return make_response(render_template('data_error.html', msg=msg), 404)

    df.to_csv("./local_files/time_series_table_data.csv")
    return send_file('./local_files/time_series_table_data.csv',
        mimetype='text/csv',
        attachment_filename="time_series_table_data.csv",
        as_attachment=True)