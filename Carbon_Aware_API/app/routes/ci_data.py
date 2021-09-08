#app/routes/ci_data  -- Carbon intensity data

from flask import Blueprint, redirect, make_response, request, current_app
from flask.helpers import url_for
from flask.templating import render_template
import pandas as pd
from app.utils import *
import datetime

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
   
        return redirect(url_for('get_grid_data', ba=ba, starttime=starttime, endtime=endtime, user_name=user_name, pass_word=pass_word))
    
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
        return redirect(url_for('get_historical_data', ba=ba,user_name=user_name,pass_word=pass_word))

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
        return redirect(url_for('get_index_data', ba=ba,user_name=user_name,pass_word=pass_word))

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
        return redirect(url_for('get_forecast_data', ba=ba, starttime=starttime, endtime=endtime,user_name=user_name,pass_word=pass_word))

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
        return redirect(url_for('get_timeseries_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename, AZ_Region=az_region , gpuutil=gpuutil))



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
        return redirect(url_for('get_timeseries_table_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename, AZ_Region=az_region))





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
        return redirect(url_for('get_sum_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename))

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
        return redirect(url_for('get_peak_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename))
        
    else:
        msg = 'try different query parameters'
        return make_response(render_template('data_error.html',msg=msg), 404 )