import requests
from requests.auth import HTTPBasicAuth
import json
from flask import Flask, jsonify, make_response, request, render_template, redirect, send_from_directory, url_for, Response
from flask_swagger_ui import get_swaggerui_blueprint
import re
import pandas as pd
import os
import datetime
import dateutil.parser as parser
import plotly
import plotly.graph_objects as go
import plotly.express as px
import statistics
from os import path
from flask.helpers import send_file
from werkzeug.utils import secure_filename
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets.tables import DataTable, TableColumn
from datetime import datetime as dt
from plotly.subplots import make_subplots
from flask_apscheduler import APScheduler

# Constant declarations
app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
cur_dir = path.dirname(path.realpath('__file__'))
UPLOAD_FOLDER = path.join(cur_dir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['csv', 'json', 'xlsx'])

# may need to comment out and run load_region_displayname_dict()
NAME_TO_DISPLAY = json.load(open('./static/name_to_display.json', 'r'))
DISPLAY_TO_NAME = json.load(open('./static/display_to_name.json', 'r'))
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger5.yaml'


HOURS_IN_DAY = 24
MINUTES_IN_HOUR = 60
MINUTES_IN_DAY = 3600

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Carbon API testing"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/")
def start():
    return redirect(url_for('home'))


@app.route("/home")
def home():
    return render_template('start.html')


@app.route('/docs_page')
def docs_page():
    return render_template('appendix.html')


@app.route('/deck')
def deck():
    return render_template('deck.html')


@app.route('/api_docs')
def api_docs():
    return render_template('api_docs.html')


@app.route('/monitor_docs')
def monitor_docs():
    return render_template('monitor_docs2.html')


@app.route('/case_study')
def case_study():
    return render_template('case_study.html')


@app.route('/kb_cite')
def kb_cite():
    return render_template('kb_cite.html')


@app.route('/kb_summary')
def kb_summary():
    return render_template('kb_summary.html')


@app.route('/api_use')
def api_use():
    return render_template('api_use.html')


@app.route('/other')
def other():
    return render_template('miro.html')


@app.route('/protected', methods=['GET', 'POST'])
def protected():
    return render_template('datachoice_combo.html')


@app.route('/ci_data', methods=['GET', 'POST'])
def ci_data():
    return render_template('ci_find.html')


def get_token():
    '''
    this gets user name and password for WattTime from static file
    uses the credentials to ping WattTime API to generate a token to retrieve data
    '''

    # calling creds
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "login_creds.json")
    login_data = json.load(open(json_url))
    # WattTime ping with creds
    login_url = 'https://api2.watttime.org/v2/login'
    token = requests.get(login_url, auth=HTTPBasicAuth(
        login_data['username'], login_data['password'])).json()['token']
    return token


def protected_token():
    '''
    this gets user name and password for WattTime from a user input
    uses the credentials to ping WattTime API to generate a token to retrieve data
    '''

    user_name = request.args.get("user_name", None)
    pass_word = request.args.get("pass_word", None)
    login_url = 'https://api2.watttime.org/v2/login'
    token = requests.get(login_url, auth=HTTPBasicAuth(
        user_name, pass_word)).json()['token']
    return token


def get_az():
    '''
    this gets Data Center information from a static file.
    work around to implementing OAUTH2 login for a live feed of Azure regions
    slowly changing list
    file is JSON of data stream from: subprocess.check_output("az account list-locations", shell=True)
    '''

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url2 = os.path.join(SITE_ROOT, "static", "az_regions.json")
    data_center_info = json.load(open(json_url2))
    return data_center_info

#az_coords = subprocess.check_output("az account list-locations", shell=True)
#az_coords = (az_coords.decode("utf-8"))
#az_coords = json.loads(az_coords)


# initialization
WT_Regions = []

# calling Data Center information from json file in static folder.
az_coords = get_az()

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


# for balancing authority input
def from_ba_helper(BA_full_name):
    '''
    this function takes in the full name of a WattTime balancing authority grabs usefull data
    that can be used for various operations
    the data schema is:
    {Data Center Display Name, Balancing Authority Name, Balancing Authority Abbreviation, 
     Latitude of DC, Longitude of DC, Balancing Authority id}
    '''

    data_center_info = get_az()
    df = WT_Regions
    # allow for swagger GET
    if BA_full_name != None:
        pass
    # next
    else:
        try:
            if len(request.form.get('data', None)) == 0:
                return make_response(render_template('ba_error.html'), 404)
            elif len(request.form.get('data', None)) != 0:
                BA_full_name = request.form.get('data', None)
                if BA_full_name == 'nada':
                    return make_response(render_template('ba_error.html'), 404)
        # if no parameters are received throw an error
        except ValueError:
            msg = 'begin a search first'
            return make_response(render_template('data_error.html', msg=msg), 502)

    for sublist in df:
        if BA_full_name in sublist:
            index_val = df.index(sublist)
            print(df.index(sublist))
            data_center_displayName = (
                az_coords_WT_joined[0][index_val]['displayName'])
            df = str.strip(re.sub('[^A-Z]', ' ', df[index_val][18:42]))
            ba_abbrev = re.sub('[^A-Z]', '_', df)
            ba_abbrev = ba_abbrev.split('___', 1)[0]
            data = {'AZ_Region': data_center_displayName,
                    'name': BA_full_name, 'abbrev': ba_abbrev,
                    'latitude': data_center_info[index_val]['metadata']['latitude'],
                    'longitude': data_center_info[index_val]['metadata']['longitude'],
                    'id': no_symbol.sub('', WT_Regions[index_val][6:9])
                    }
            print(data)

            return data
    return ''


# for Data Center input
def getloc_helper(data_center_diplayName):
    '''
    this function takes in the full name of a Data Center grabs usefull data
    that can be used for various operations
    the data schema is:
    {Data Center Display Name, Balancing Authority Name, Balancing Authority Abbreviation, 
     Latitude of DC, Longitude of DC, Balancing Authority id}
    '''

    data_center_info = get_az()

    # allow query string to be used in place of form POST
    if data_center_diplayName != None:
        pass
    # if nothing was provided, grab the form POST
    else:
        try:
            data_center_diplayName = request.form.get('data', None)
            if data_center_diplayName == 'nada':
                msg = 'ensure all required parameters were entered'
                return make_response(render_template('data_error.html', msg=msg), 404)
        except ValueError:
            msg = 'begin a search first'
            return make_response(render_template('data_error.html', msg=msg), 502)

    key = "displayName"
    input_value = data_center_diplayName
    token = get_token()

    # finding coords for the passed AZ_region
    # finds where the value of the key is equal to the input query value
    # this parses the Data Center information json
    #
    data_center_dict = next(filter(lambda x: x.get(
        key) == input_value, data_center_info), None)
    if data_center_dict == None:
        msg = 'verify a valid Azure region was used.'
        return make_response(render_template('data_error.html', msg=msg), 404)

    # calling coords of AZ region
    data_center_latitude = data_center_dict['metadata']['latitude']
    data_center_longitude = data_center_dict['metadata']['longitude']

    # WattTime connection to get ba
    region_url = 'https://api2.watttime.org/v2/ba-from-loc'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'latitude': data_center_latitude,
              'longitude': data_center_longitude}
    rsp = requests.get(region_url, headers=headers, params=params)

    # WattTime response and adding the azure region for output
    data = json.loads(rsp.text)
    data['AZ_Region'] = data_center_diplayName
    print(f"getloc_helper data = {data}")

    return data


def get_start_end(filename):
    '''
    reads the last charcaters of the file name string to determine load method.
    this then finds and outputs the first and last timestamp as start and stop
    these are the start and end times for the energy profile
    '''

    file_type_check = str(filename)

    if file_type_check[-4:] == 'xlsx':
        intro = pd.read_excel(filename, engine='openpyxl')
        return get_start_end_tabular(intro)
    elif file_type_check[-3:] == 'csv':
        intro = pd.read_csv(filename)
        return get_start_end_tabular(intro)
    else:
        startstop = json.load(open(filename, 'rb'))['timespan'].split('/')
        start = pd.to_datetime(startstop[0]).isoformat()
        stop = pd.to_datetime(startstop[1]).isoformat()
        return start, stop


def get_start_end_tabular(intro):
    '''
    for xlsx and csv dtypes from get_start_end()
    grabs the first and last timestamps for the energy profile's start and
    end times
    '''

    intro_times = intro.iloc[1:3, 0]
    # print("\n\n")
    # print("Intro", intro.columns, intro.shape, intro.iloc[0:4,1:3])
    # If the file contains the local timezone in parentheses
    print(intro_times)
    if '(' in intro_times.iloc[0]:
        start = re.search(
            r"[... \d][^\(]+", intro_times.iloc[0]).group(0).strip()
        end = re.search(
            r"[... \d][^\(]+", intro_times.iloc[1]).group(0).strip()
        start = pd.to_datetime(re.search(
            r"^[A-Za-z1-9].+:\d\d", start).group(0) + re.search(r".{5}$", start).group(0)).isoformat()
        end = pd.to_datetime(re.search(
            r"^[A-Za-z1-9].+:\d\d", end).group(0) + re.search(r".{5}$", end).group(0)).isoformat()
    # Otherwise, the file is in UTC
    else:
        start = pd.to_datetime(re.search(
            r"\d{2} ... \d{4} \d{2}:\d{2}:\d{2}", intro_times.iloc[0]).group(0)).isoformat()
        end = pd.to_datetime(re.search(
            r"\d{2} ... \d{4} \d{2}:\d{2}:\d{2}", intro_times.iloc[1]).group(0)).isoformat()
    return start, end


# hard code of Time zone offsets from UTC
timezone_info = {
    "A": 1 * 3600, "ACDT": 10.5 * 3600, "ACST": 9.5 * 3600, "ACT": -5 * 3600, "ACWST": 8.75 * 3600, "ADT": 4 * 3600, "AEDT": 11 * 3600,
    "AEST": 10 * 3600, "AET": 10 * 3600, "AFT": 4.5 * 3600, "AKDT": -8 * 3600, "AKST": -9 * 3600, "ALMT": 6 * 3600, "AMST": -3 * 3600,
    "AMT": -4 * 3600, "ANAST": 12 * 3600, "ANAT": 12 * 3600, "AQTT": 5 * 3600, "ART": -3 * 3600, "AST": 3 * 3600, "AT": -4 * 3600,
    "AWDT": 9 * 3600, "AWST": 8 * 3600, "AZOST": 0 * 3600, "AZOT": -1 * 3600, "AZST": 5 * 3600, "AZT": 4 * 3600, "AoE": -12 * 3600,
    "B": 2 * 3600, "BNT": 8 * 3600, "BOT": -4 * 3600, "BRST": -2 * 3600, "BRT": -3 * 3600, "BST": 6 * 3600, "BTT": 6 * 3600,
    "C": 3 * 3600, "CAST": 8 * 3600, "CAT": 2 * 3600, "CCT": 6.5 * 3600, "CDT": -5 * 3600, "CEST": 2 * 3600, "CET": 1 * 3600,
    "CHADT": 13.75 * 3600, "CHAST": 12.75 * 3600, "CHOST": 9 * 3600, "CHOT": 8 * 3600, "CHUT": 10 * 3600, "CIDST": -4 * 3600,
    "CIST": -5 * 3600, "CKT": -10 * 3600, "CLST": -3 * 3600, "CLT": -4 * 3600, "COT": -5 * 3600, "CST": -6 * 3600,  "CT": -6 * 3600, "CVT": -1 * 3600,
    "CXT": 7 * 3600, "ChST": 10 * 3600, "D": 4 * 3600, "DAVT": 7 * 3600, "DDUT": 10 * 3600, "E": 5 * 3600, "EASST": -5 * 3600,
    "EAST": -6 * 3600, "EAT": 3 * 3600, "ECT": -5 * 3600, "EDT": -4 * 3600, "EEST": 3 * 3600, "EET": 2 * 3600, "EGST": 0 * 3600,
    "EGT": -1 * 3600, "EST": -5 * 3600, "ET": -5 * 3600,  "F": 6 * 3600, "FET": 3 * 3600, "FJST": 13 * 3600, "FJT": 12 * 3600,
    "FKST": -3 * 3600, "FKT": -4 * 3600, "FNT": -2 * 3600, "G": 7 * 3600, "GALT": -6 * 3600, "GAMT": -9 * 3600, "GET": 4 * 3600,
    "GFT": -3 * 3600, "GILT": 12 * 3600, "GMT": 0 * 3600, "GST": 4 * 3600, "GYT": -4 * 3600, "H": 8 * 3600, "HDT": -9 * 3600,
    "HKT": 8 * 3600, "HOVST": 8 * 3600, "HOVT": 7 * 3600, "HST": -10 * 3600, "I": 9 * 3600, "ICT": 7 * 3600, "IDT": 3 * 3600,
    "IOT": 6 * 3600, "IRDT": 4.5 * 3600, "IRKST": 9 * 3600, "IRKT": 8 * 3600, "IRST": 3.5 * 3600, "IST": 5.5 * 3600, "JST": 9 * 3600,
    "K": 10 * 3600, "KGT": 6 * 3600, "KOST": 11 * 3600, "KRAST": 8 * 3600, "KRAT": 7 * 3600, "KST": 9 * 3600, "KUYT": 4 * 3600,
    "L": 11 * 3600, "LHDT": 11 * 3600, "LHST": 10.5 * 3600, "LINT": 14 * 3600, "M": 12 * 3600, "MAGST": 12 * 3600, "MAGT": 11 * 3600, "MART": 9.5 * 3600, "MAWT": 5 * 3600,
    "MDT": -6 * 3600, "MHT": 12 * 3600, "MMT": 6.5 * 3600, "MSD": 4 * 3600, "MSK": 3 * 3600, "MST": -7 * 3600, "MT": -7 * 3600,
    "MUT": 4 * 3600, "MVT": 5 * 3600, "MYT": 8 * 3600, "N": -1 * 3600, "NCT": 11 * 3600, "NDT": 2.5 * 3600, "NFT": 11 * 3600,
    "NOVST": 7 * 3600, "NOVT": 7 * 3600, "NPT": 5.5 * 3600, "NRT": 12 * 3600, "NST": 3.5 * 3600, "NUT": -11 * 3600, "NZDT": 13 * 3600, "NZST": 12 * 3600,
    "O": -2 * 3600, "OMSST": 7 * 3600, "OMST": 6 * 3600, "ORAT": 5 * 3600, "P": -3 * 3600, "PDT": -7 * 3600, "PET": -5 * 3600,
    "PETST": 12 * 3600, "PETT": 12 * 3600, "PGT": 10 * 3600, "PHOT": 13 * 3600, "PHT": 8 * 3600, "PKT": 5 * 3600, "PMDT": -2 * 3600,
    "PMST": -3 * 3600, "PONT": 11 * 3600, "PST": -8 * 3600, "PT": -8 * 3600, "PWT": 9 * 3600, "PYST": -3 * 3600, "PYT": -4 * 3600,
    "Q": -4 * 3600, "QYZT": 6 * 3600, "R": -5 * 3600, "RET": 4 * 3600, "ROTT": -3 * 3600, "S": -6 * 3600, "SAKT": 11 * 3600, "SAMT": 4 * 3600, "SAST": 2 * 3600, "SBT": 11 * 3600,
    "SCT": 4 * 3600, "SGT": 8 * 3600, "SRET": 11 * 3600, "SRT": -3 * 3600, "SST": -11 * 3600, "SYOT": 3 * 3600, "T": -7 * 3600,
    "TAHT": -10 * 3600, "TFT": 5 * 3600, "TJT": 5 * 3600, "TKT": 13 * 3600, "TLT": 9 * 3600, "TMT": 5 * 3600, "TOST": 14 * 3600,
    "TOT": 13 * 3600, "TRT": 3 * 3600, "TVT": 12 * 3600, "U": -8 * 3600, "ULAST": 9 * 3600, "ULAT": 8 * 3600, "UTC": 0 * 3600, "UYST": -2 * 3600, "UYT": -3 * 3600,
    "UZT": 5 * 3600, "V": -9 * 3600, "VET": -4 * 3600, "VLAST": 11 * 3600, "VLAT": 10 * 3600, "VOST": 6 * 3600, "VUT": 11 * 3600, "W": -10 * 3600,
    "WAKT": 12 * 3600, "WARST": -3 * 3600, "WAST": 2 * 3600, "WAT": 1 * 3600, "WEST": 1 * 3600, "WET": 0 * 3600, "WFT": 12 * 3600,
    "WGST": -2 * 3600, "WGT": -3 * 3600, "WIB": 7 * 3600, "WIT": 9 * 3600, "WITA": 8 * 3600, "WST": 14 * 3600, "WT": 0 * 3600, "X": -11 * 3600,
    "Y": -12 * 3600, "YAKST": 10 * 3600, "YAKT": 9 * 3600, "YAPT": 10 * 3600, "YEKST": 6 * 3600, "YEKT": 5 * 3600, "Z": 0 * 3600,
}


def allowed_file(filename):
    '''
    calls the ALLOWED_EXTENSIONS folder to check and make sure the submitted file
    is an accepted type. .xslx , .csv , or .json are accepted
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_file_data():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print('file uploaded')
            SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
            file_url = os.path.join(SITE_ROOT, "uploads", filename)

            return file_url
    return ''


# ==========================================================
# begining logs for impact tracking
# ==========================================================

def update_usage_data():
    '''
    Updates json file with newest entry from user input
    Records the data from the prediction as well as if the prediction was used
    '''

    # get indicator of if the cron time was accepted
    usage = request.args.get('usage', None)
    payload = request.args.get('pred_data', None)  # output of prediction
    new_usage_data = [[usage, payload]].to_dict()
    # If this directory doesn't exist, the json file containing the history doesn't as well.
    if not os.path.isdir("./local_files"):
        os.mkdir("./local_files")
        data = [new_usage_data]
    else:  # Directory + cached file exists
        data = json.load(open("./local_files/usage_data.json",))
        data.append(new_usage_data)
    with open("./local_files/usage_data.json", "w") as cachedfile:
        json.dump(data, cachedfile)


def avg_carbon_saved():
    '''
    Opens cached log with schema {'usage', 'payload'} which is 
        a logical response of if the prediction was accepted 0=Not accepted, 1=accepted
        payload is the prediction data containing (see /geotime_shift) current_starttime
        and percentage_decrease which are the time the prediction was made and the percent
        difference of the current WS emissions and the prediciton WS emissions
    '''

    with open("./local_files/usage_data.json", "r") as file_in:
        # Read in as string json. doing a second json.loads deserializes into json/dict object.
        carbon_data = json.loads(json.load(file_in))

    used_preds_perc_diff = []
    # getting only perc_diff that were used. ignores unused predictions
    for prediction in range(len(carbon_data)):
        if carbon_data[prediction]['usage'] == 1:
            carbon_percdiff = carbon_data[prediction]['payload']['percentage_decrease']
            used_preds_perc_diff.append(carbon_percdiff)
    carbon_avg_percdiff = statistics.mean(used_preds_perc_diff)

    return carbon_avg_percdiff


@app.route('/prediction_made', methods=["GET", "POST"])
def prediction_made():
    '''
    Pathway if the prediction was to be used.
    Will log the prediction data and that it was used.
    Point of connection for cron scheduler.
    '''
    log = update_usage_data()
    carbon_to_date = avg_carbon_saved()

    return render_template("prediction_made.html", data=carbon_to_date)


@app.route('/prediction_rejected', methods=["GET", "POST"])
def prediction_rejected():
    '''    
    Pathway if the prediction was not used.
    Will log prediction data and that it was not used.
    Redirects to make a new prediction
    '''
    log = update_usage_data()

    return render_template("pred_shift_find.html")

# ============================================================
# ============================================================


@app.route('/chooser', methods=["GET", "POST"])
def chooser():
    '''
    This serves as a gateway and path selection tool so enpoints can be combined in the UI.
    '''
    WT_names = pd.DataFrame([json.loads(x) for x in WT_Regions])[
        ['name', 'abbrev']].dropna()
    end_point_choice = request.form['data']
    print(end_point_choice)

    dc_location = request.form['data_az']

    dc_balancing_authority = request.form['data_ba']
    print(dc_balancing_authority)
    if dc_location == 'nada':
        dc_location = dc_balancing_authority
        if dc_balancing_authority == 'nada':
            msg = 'be sure to select an Azure region or WattTime balancing authority for the search'
            return make_response(render_template('data_error.html', msg=msg), 400)
    else:
        if dc_balancing_authority != 'nada':
            msg = 'only select one Region type'
            return make_response(render_template('data_error.html', msg=msg), 400)
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
            return make_response(render_template('ci_error.html', msg=msg), 400)
        start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() -
                        datetime.timedelta(minutes=15))
        start = start.upper()
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('ci_error.html', msg=msg), 404)
        end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400)
        try:
            user_name = request.form.get('user_name', None)
            pass_word = request.form.get('pass_word', None)
        except:
            msg = 'verify correct Username and Password'
            return make_response(render_template('data_error.html', msg=msg), 400)

        return redirect(url_for('get_grid_data', ba=ba, starttime=starttime, endtime=endtime, user_name=user_name, pass_word=pass_word))

    # historical data path, gives zip file
    elif end_point_choice == 'historical':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('ci_error.html', msg=msg), 400)
        try:
            user_name = request.form.get('user_name', None)
            pass_word = request.form.get('pass_word', None)
        except:
            msg = 'verify correct Username and Password'
            return make_response(render_template('data_error.html', msg=msg), 400)
        return redirect(url_for('get_historical_data', ba=ba, user_name=user_name, pass_word=pass_word))

    # real-time data path
    elif end_point_choice == 'index':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('ci_error.html', msg=msg), 400)
        try:
            user_name = request.form.get('user_name', None)
            pass_word = request.form.get('pass_word', None)
        except:
            msg = 'verify correct Username and Password'
            return make_response(render_template('data_error.html', msg=msg), 400)
        return redirect(url_for('get_index_data', ba=ba, user_name=user_name, pass_word=pass_word))

    # marginal emissions forecast data for chosen region, 24hrs by default
    elif end_point_choice == 'forecast':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('ci_error.html', msg=msg), 400)

        start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() -
                        datetime.timedelta(minutes=15))
        start = start.upper()
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('ci_error.html', msg=msg), 400)
        end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('ci_error.html', msg=msg), 400)
        try:
            user_name = request.form.get('user_name', None)
            pass_word = request.form.get('pass_word', None)
        except:
            msg = 'verify correct Username and Password'
            return make_response(render_template('data_error.html', msg=msg), 400)
        return redirect(url_for('get_forecast_data', ba=ba, starttime=starttime, endtime=endtime, user_name=user_name, pass_word=pass_word))

    # azure-watttime data analysis, goes to dashboard like UI
    elif end_point_choice == 'azure':
        gpuutil = request.form.get('gpuutil', 0)
        if gpuutil == 'on':
            gpuutil = 1
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('data_error.html', msg=msg), 400)
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
            return make_response(render_template('data_error.html', msg=msg), 400)
        #end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        print(end)
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400)
        return redirect(url_for('get_timeseries_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename, AZ_Region=az_region, gpuutil=gpuutil))

    # azure-watttime data file return, CSV of timeseries Time:Emissions:Energy
    elif end_point_choice == 'azure2':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('data_error.html', msg=msg), 400)
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
            return make_response(render_template('data_error.html', msg=msg), 400)
        #end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        print(end)
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400)
        return redirect(url_for('get_timeseries_table_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename, AZ_Region=az_region))

    # azure-watttime data
    elif end_point_choice == 'sums':
        filename = get_file_data()
        start, end = get_start_end(filename)

        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('data_error.html', msg=msg), 400)
        #start = request.form.get('starttime', None)
        if len(start) == 0:
            start = str(datetime.datetime.now() - datetime.timedelta(hours=24))
        start = start.upper()
        try:
            starttime = parser.parse(start, tzinfos=timezone_info).isoformat()
            print(starttime)
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400)
        #end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400)
        return redirect(url_for('get_sum_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename))

    # azure-watttime data
    elif end_point_choice == 'peaks':
        try:
            ba = data['abbrev']
        except:
            msg = 'use an Azure region that is supported by a WattTime balancing authority'
            return make_response(render_template('data_error.html', msg=msg), 400)
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
            return make_response(render_template('data_error.html', msg=msg), 400)
        #end = request.form.get('endtime', None)
        if len(end) == 0:
            end = str(datetime.datetime.now().isoformat())
        end = end.upper()
        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('data_error.html', msg=msg), 400)
        return redirect(url_for('get_peak_data', ba=ba, starttime=starttime, endtime=endtime, filename=filename))

    else:
        msg = 'try different query parameters'
        return make_response(render_template('data_error.html', msg=msg), 404)


@app.route('/get_grid_data', methods=["GET"])
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
        msg = 'check query parameters. WattTime response contained an error'
        return make_response(render_template('data_error.html', msg=msg), 400)
    elif len(data_check) == 0:
        msg = 'check query parameters. No WattTime response returned.'
        return make_response(render_template('data_error.html', msg=msg), 404)
    return rsp.text

    # return render_template('output_page.html', data=data)   # for html output

# route to get real-time ba data


@app.route('/get_index_data', methods=["GET"])
def get_index_data():
    token = protected_token()
    ba = request.args.get("ba", None)
    index_url = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(index_url, headers=headers, params=params)

    return rsp.text  # for text output


# route to get historical data for given ba
@app.route('/get_historical_data', methods=["GET"])
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
@app.route('/get_forecast_data', methods=["GET"])
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
        msg = 'check query parameters. WattTime response contained an error'
        return make_response(render_template('data_error.html', msg=msg), 400)
    elif len(data_check) == 0:
        msg = 'check query parameters. No WattTime response returned.'
        return make_response(render_template('data_error.html', msg=msg), 404)
    return rsp.text


def get_SKU_table():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    csv_url = os.path.join(SITE_ROOT, "static", "Region-SKU-Tags.csv")
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
            geo = pd.DataFrame(
                [SKU_data_table[SKU_data_table['region'] == Az_region]['R_Tag_lock'].values])
            print(f"Regional Lock Tag for current region is {geo}")
            SKU_data_table_filtered = SKU_data_table[SKU_data_table['R_Tag_lock'] == geo[0].values[0]].reset_index(
            )
        else:
            SKU_data_table_filtered = SKU_data_table.reset_index()
    except KeyError:   # if name was provided as an name not displayName
        if sensitive_check_box == 'on':
            geo = pd.DataFrame([SKU_data_table[SKU_data_table['region']
                               == NAME_TO_DISPLAY[Az_region]]['R_Tag_lock'].values])
            print(f"Regional Lock Tag for current region is {geo}")
            SKU_data_table_filtered = SKU_data_table[SKU_data_table['R_Tag_lock'] == geo[0].values[0]].reset_index(
            )
        else:
            SKU_data_table_filtered = SKU_data_table.reset_index()

    return SKU_data_table_filtered


def Gpu_filter(SKU_data_table_filtered, desired_GPU):
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


def format_json(filename):
    '''
    Convert json file into a pandas dataframe
    '''
    Monitor_data = json.load(open(filename))
    az_file = pd.DataFrame(
        Monitor_data['value'][0]['timeseries'][0]['data']).dropna()
    az_file.columns = ['Time', 'Total']
    return az_file


def format_dataframe(df, gpuutil_flag):
    '''
    Reformat input pandas dataframe to match the requirements needed for latter functions. Check number of columns, ensure index is represented, followed by datetime. 
    Check for GPUUtilization column and name all of them properly.
    Arguments:
        df: pandas dataframe converted from either csv or xlsx filetype
        gpuutil_flag: boolean of whether or not the user wanted to add gputilization to their output
    '''
    df_loc = df[10:].dropna()
    # print(df_loc)

    columns = df.iloc[9, :]
    df_loc.columns = [col for col in columns]

    # If first column contains datetimes as datetimes or strings, add an index column
    if (type(df_loc.iloc[0, 0]) == type(datetime.datetime.now())) | (type(df_loc.iloc[0, 0]) == type('a')):
        df_loc.reset_index(inplace=True)
    # Else if first column is not an integer (is not an index), then return an error
    elif (type(df_loc.iloc[0, 0]) != type(1)):
        msg = 'use either a .xlsx, .csv, or .json file with the proper column formatting.'
        return make_response(render_template('data_error.html', msg=msg), 411)
    # Name first two cols
    df_loc.columns.values[0] = 'Index'
    df_loc.columns.values[1] = 'Time'

    # create new df to hold reconfigured data; begin with index and time
    az_file = df_loc[['Index', 'Time']]
    for col in df_loc.columns:
        print(col)
        # search for Joules metric; add it when found
        if 'GpuEnergyJoules' in col:
            az_file = pd.concat((az_file, df_loc[col]), axis=1)
            az_file.columns.values[2] = 'Total'
        # currently just check for if it exists; we should also decide on whether or not to add logic for the user filling out the form indicating GPUUtil option is active
        # grab GPUUtilization if it is found
        print('GpuUtilization' in col)
        print(gpuutil_flag == 1)
        if ('GpuUtilization' in col) & (gpuutil_flag == 1):
            az_file = pd.concat((az_file, df_loc[col]), axis=1)
            az_file.columns.values[3] = 'GPUUtil'
            print("Marked")
    # throw error if not found
    if 'Total' not in az_file.columns:
        msg = 'use either a .xlsx, .csv, or .json file with a column representing GPUEnergyJoules metric.'
        return make_response(render_template('data_error.html', msg=msg), 411)
    # print(az_file)
    return az_file


def compare_intervals(df):
    '''
    Integity check to ensure that time intervals are 300 seconds apart.
    Arguments:
        df: pandas dataframe properly formatted to contain the `Time` column

    Output:
        Boolean stating whether or not the time intervals are 300 seconds
    '''
    # grab the middle time value
    time_1_choice = df['Time'][int(len(df)/2)]
    try:
        t1 = time_1_choice.split(" ")[1]
    except:
        try:
            FMT = '%H:%M:%S'
            time_1_choice = dt.strftime(time_1_choice, FMT)
            print(time_1_choice)
            t1 = time_1_choice
        except:
            FMT = '%H:%M'
            t1 = time_1_choice
    # grab middle +1 time value
    time_2_choice = df['Time'][int(len(df)/2)+1]
    try:
        t2 = time_2_choice.split(" ")[1]
    except:
        try:
            FMT = '%H:%M:%S'
            time_2_choice = dt.strftime(time_2_choice, FMT)
            print(time_2_choice)
            t2 = time_2_choice
        except:
            FMT2 = '%H:%M'
            print(time_2_choice)
            t2 = time_2_choice

    # Setup comparison for 5 min intervals
    try:
        tdelta = dt.strptime(t2, FMT) - dt.strptime(t1, FMT)
    except:
        tdelta = dt.strptime(t2, FMT2) - dt.strptime(t1, FMT2)
    bench = datetime.timedelta(seconds=300)

    return tdelta == bench


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


@app.route('/get_timeseries_data', methods=["GET", "POST"])
def get_timeseries_data():
    filename = str(request.args.get("filename", None))
    gpuutil_flag = int(request.args.get("gpuutil", None))
    starttime = request.args.get("starttime", None)
    endtime = request.args.get("endtime", None)
    ba = request.args.get("ba", None)
    data_url = 'https://api2.watttime.org/v2/data'

    AZ_data = gather_azmonitor(filename, gpuutil_flag)
    az_file = gather_azmonitor(filename, gpuutil_flag)

    # try:
    rsp = gather_watttime(ba, starttime, endtime)
    data = json.loads(rsp.text)

    WT_data = pd.json_normalize(data).dropna()
    WT_data = WT_data.sort_index(ascending=False)
    MWh_Az = AZ_data['Total'].dropna()

    # power per time delta
    MegaWatth_per_five = MWh_Az*2.77778e-10
    # total power in time window
    MegaWatth_total = sum(MegaWatth_per_five)
    # pounds of carbon per time delta
    resource_emissions = MegaWatth_per_five*WT_data['value'].dropna()
    # total pounds of carbon in time window
    carbon_total = sum(resource_emissions.dropna())
    print(len(WT_data['value']))

    # stats
    avg = format(statistics.mean(resource_emissions.dropna()), '.4g')
    # real-time MOER
    ba = request.args.get("ba", None)
    index_url = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    realtime_rsp = requests.get(index_url, headers=headers, params=params)
    realtime_data = json.loads(realtime_rsp.text)
    realtime_data = pd.json_normalize(realtime_data)

    plot_data = {'resource_emissions': resource_emissions,
                 'Time': AZ_data['Time'], 'Energy': MegaWatth_per_five}
    df = pd.DataFrame(plot_data)

    # peak id
    peak_threshold = 0.05
    peak_span = df['Time'].iloc[pd.Series(resource_emissions.loc[resource_emissions > (
        max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)]

    peak = f"{round(max(resource_emissions), 3)} lbs/per 5 minutes at {df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))]}"
    #peak_e = f"{round(max(MegaWatth_per_five), 6)} MWh at {df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]}"

    Carbon = df['resource_emissions']

    # plotting

    emissions_plot_custom_layer = go.Scatter(x=df['Time'][:len(df['resource_emissions'])],
                                             y=Carbon,
                                             mode='lines',
                                             connectgaps=True,
                                             hoverinfo='skip',
                                             line_color='#077FFF',
                                             name='Emissions')
    peak_emissions_index = pd.Series(resource_emissions.loc[resource_emissions > (
        max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)
    emissions_plot_peak_layer = go.Scattergl(x=peak_span,
                                             y=Carbon.iloc[peak_emissions_index],
                                             mode='markers',
                                             marker_color='rgb(270,0,0)',
                                             marker={'size': 7},
                                             name='Highest 5%')
    energy_plot_custom_layer = go.Scattergl(x=df['Time'],
                                            y=df['Energy'],
                                            mode='lines',
                                            connectgaps=True,
                                            hoverinfo='skip',
                                            line_color='#077FFF',
                                            name='Data')

    peak_energy_x = [df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(
        MegaWatth_per_five))], df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]]
    peak_energy_y = [df['Energy'].iloc[MegaWatth_per_five.astype(float).idxmax(max(
        MegaWatth_per_five))], df['Energy'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]]
    energy_plot_peak_layer = go.Scattergl(x=peak_energy_x,
                                          y=peak_energy_y,
                                          mode='markers',
                                          marker_color='rgb(270,0,0)',
                                          marker={'size': 7},
                                          name='Max Consuption')

    df.columns = ['Carbon Emitted (lbs)', 'Time', 'Energy (MWh)']
    try:
        layout = dict(
            xaxis=dict(
                tickvals=df['Time'][::int(len(df['Time'])/4)],
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
        msg = 'check input time accuracy and format. If problem persists please contact support team.'
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
            msg = 'check input time accuracy and format. If problem persists please contact support team.'
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
                tdelta = dt.strptime(
                    df['Time'][len(df['Time'])-1], FMT) - dt.strptime(df['Time'][0], FMT)
            except:
                FMT = '%Y%m%d %H:%M'
                tdelta = df['Time'][len(df['Time'])-1] - df['Time'][0]
        except:
            try:
                FMT = '%Y-%m-%dT%H:%M:%SZ'
                tdelta = dt.strptime(
                    df['Time'][len(df['Time'])-1], FMT) - dt.strptime(df['Time'][0], FMT)
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

    # emissions_plot.add_trace(figl)

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
    # print(df)

    abbrev = request.args.get("ba", None)
    print(abbrev)
    moer_value = get_realtime_data(abbrev)
    percent_zeros = get_percent_zero(abbrev)

    page_data = {}

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

    vals = rsp.json()

    # To plot the daily, weekly and monthly carbon emission trends

    if vals[0]['frequency'] != 300:
        daydata = vals[:int(round((len(vals)/30), 0))]
        print(daydata[:3])
        print(len(daydata))

        MOER_day_time = []
        MOER_day = []
        for x in range(0, len(daydata), int(round((len(daydata)/24), 0))):
            val = daydata[x]['value']
            time = daydata[x]['point_time']
            MOER_day.append(val)
            MOER_day_time.append(time)
        Neat_day = pd.DataFrame([MOER_day_time, MOER_day]).T
        Neat_day.columns = ['Time (UTC)', 'Region Intensity']

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
        Neat_day = pd.DataFrame([MOER_day_time, MOER_day]).T
        Neat_day.columns = ['Time (UTC)', 'Region Intensity']

    # Percent times 0g carbon emission in a day
    count_moer_day = 0
    count_zero_day = 0
    for i in daydata:
        if int(i["value"]) == 0:
            count_zero_day += 1
        count_moer_day += 1

    day_zero = round((count_zero_day/count_moer_day)*100, 2)

    # For passing data to html
    page_data['day'] = day_zero
    page_data['num_day_0'] = count_zero_day
    page_data['avg_day'] = round(statistics.mean(MOER_day), 0)

    descend = Neat_day['Time (UTC)'].sort_index(ascending=False)
    descend = descend.reset_index()

    df['Time (UTC)'] = descend['Time (UTC)']
    df['Region Intensity'] = Neat_day['Region Intensity']

    # plots
    large_CI_plot = px.line(data_frame=Neat_day, x='Time (UTC)',
                            y='Region Intensity',
                            title='Region Intensity (<span><sup>lbs</sup>/<sub>MWh</sub></span>) by Time',
                            template='none')
    large_CI_plot_custome_layer = go.Scatter(x=Neat_day['Time (UTC)'],
                                             y=Neat_day['Region Intensity'],
                                             mode='lines',
                                             connectgaps=True,
                                             hoverinfo='skip',
                                             line_color='#077FFF',
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
    page_data['total_carbon'] = format(carbon_total, '.4g')
    page_data['energy'] = format(MegaWatth_total*1000, '.4g')
    page_data['peak_e_max'] = format(max(MegaWatth_per_five)*1000, '.4g')
    page_data['peak_e_time'] = df['Time'].iloc[MegaWatth_per_five.astype(
        float).idxmax(max(MegaWatth_per_five))]
    page_data['peak_c_max'] = format(max(resource_emissions), '.4g')
    page_data['peak_c_time'] = df['Time'].iloc[resource_emissions.astype(
        float).idxmax(max(resource_emissions))]
    page_data['realtime_data'] = realtime_data.values[0, 3]
    page_data['avg'] = avg
    page_data['length'] = tdelta
    page_data['AZ'] = request.args.get("AZ_Region", None)

    mini_C_plot = go.Scatter(x=df['Time (UTC)'][:len(df['Carbon Emitted (lbs)'])],
                             y=Carbon,
                             mode='lines',
                             connectgaps=True,
                             line_color='#077FFF',
                             name='Emissions')
    mini_peak_C_x = df['Time (UTC)'].iloc[pd.Series(resource_emissions.loc[resource_emissions > (
        max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)]
    mini_peak_C_y = Carbon.iloc[pd.Series(resource_emissions.loc[resource_emissions > (
        max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)]
    mini_C_peak_layer = go.Scattergl(x=mini_peak_C_x,
                                     y=mini_peak_C_y,
                                     mode='markers',
                                     marker_color='rgb(270,0,0)',
                                     marker={'size': 6},
                                     name='Highest 5%')
    mini_E_plot = go.Scattergl(x=df['Time (UTC)'],
                               y=df['Energy (MWh)'],
                               mode='lines',
                               connectgaps=True,
                               line_color='#077FFF',
                               name='Consumption')
    mini_peak_E_x = [df['Time (UTC)'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))],
                     df['Time (UTC)'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]]
    mini_peak_E_y = [df['Energy (MWh)'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))],
                     df['Energy (MWh)'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]]
    mini_E_peak_layer = go.Scattergl(x=mini_peak_E_x,
                                     y=mini_peak_E_y,
                                     mode='markers',
                                     marker_color='rgb(270,0,0)',
                                     marker={'size': 6},
                                     name='Max Consuption')
    CI_plot = go.Scatter(x=Neat_day['Time (UTC)'],
                         y=Neat_day['Region Intensity'],
                         mode='lines',
                         connectgaps=True,
                         line_color='#077FFF',
                         name='Intensity')
    CI_peak_layer = go.Scattergl(x=df['Time (UTC)'].iloc[pd.Series(resource_emissions.loc[resource_emissions > (max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)],
                                 y=Neat_day['Region Intensity'].iloc[pd.Series(resource_emissions.loc[resource_emissions > (
                                     max(resource_emissions) - max(resource_emissions)*peak_threshold)].index)],
                                 mode='markers',
                                 marker_color='rgb(270,0,0)',
                                 marker={'size': 6},
                                 name='Highest 5%')

    # Initialize figure with subplots
    three_mini_plots = make_subplots(
        rows=1, cols=3,
        column_titles=['Emissions (lbs) by Time', 'Energy Consumed (MWh) by Time',
                       "Region Intensity (<span><sup>lbs</sup>/<sub>MWh</sub></span>) by Time"],
        x_title='Time (UTC)'
    )
    three_mini_plots.append_trace(mini_C_plot, 1, 1)
    three_mini_plots.append_trace(mini_C_peak_layer, 1, 1)
    three_mini_plots.append_trace(mini_E_plot, 1, 2)
    three_mini_plots.append_trace(mini_E_peak_layer, 1, 2)
    three_mini_plots.update_layout(showlegend=False, template=None)
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

        areaDict = next(filter(lambda x: x.get(Key) ==
                        Region_Name, az_coords), None)
        if areaDict == None:
            msg = 'use a different region to get a carbon analysis. There was no pre-paired Azure Data center available.'
            return make_response(render_template('data_error.html', msg=msg), 404)

        # calling coords of AZ region
        data_center_latitude = areaDict['metadata']['latitude']
        data_center_longitude = areaDict['metadata']['longitude']

        data_url = 'https://api2.watttime.org/v2/data'
        headers = {'Authorization': 'Bearer {}'.format(token)}
        params = {'latitude': data_center_latitude, 'longitude': data_center_longitude,
                  'starttime': starttime,
                  'endtime': endtime}
        rsp = requests.get(data_url, headers=headers, params=params)
        data_check = str.strip(rsp.text[2:7])
        print(data_check)
        if data_check == 'error':
            msg = 'check query parameters. WattTime response contained an error'
            return make_response(render_template('data_error.html', msg=msg), 400)
        elif len(data_check) == 0:
            msg = 'check query parameters. No WattTime response returned.'
            return make_response(render_template('data_error.html', msg=msg), 404)
        rsp_data = json.loads(rsp.text)

        WT_data_counterfactual = pd.json_normalize(rsp_data)
        WT_data_counterfactual = WT_data_counterfactual.sort_index(
            ascending=False)

        # power per time delta
        MegaWatth_per_five_counterfactual = MWh_Az*2.77778e-10
        # pounds of carbon per time delta
        Carbon_counterfactual = MegaWatth_per_five_counterfactual * \
            WT_data_counterfactual['value']
        # print(Carbon_counterfactual)
        # total pounds of carbon in time window
        Carbon_counterfactual_total = sum(Carbon_counterfactual.dropna())
        print(len(WT_data_counterfactual['value']))
        print(
            f"New total is {Carbon_counterfactual_total} using {Region_Name} ")
        Carbon_counterfactual_total_region = [
            Carbon_counterfactual_total, Region_Name]
        all_region_counterfactual.append(Carbon_counterfactual_total_region)

    all_region_counterfactual_df = pd.DataFrame(all_region_counterfactual)
    all_region_counterfactual_df.columns = ['Sum', 'Name']
    # print(all_region_counterfactual_df)
    minimum_index = all_region_counterfactual_df.loc[all_region_counterfactual_df['Sum'] == min(
        all_region_counterfactual_df['Sum'])].index
    min_counterfactual = all_region_counterfactual_df.iloc[pd.Series(
        minimum_index)]
    min_counterfactual = min_counterfactual.reset_index()
    suggested_region_displayName = str(min_counterfactual['Name'])
    suggested_region_displayName = suggested_region_displayName.split(":")[0]
    suggested_region_displayName = suggested_region_displayName.split("Name")[
        0]
    suggested_region_displayName = suggested_region_displayName.split("0")[1]

    page_data['option'] = format(float(min_counterfactual['Sum'][0]), '.4g')
    page_data['pair'] = suggested_region_displayName

    delta_carbon_percent = ((float(page_data['total_carbon']) - float(
        page_data['option']))/float(page_data['total_carbon']))*100
    page_data['delta'] = format(float(delta_carbon_percent), '.4g')
    print(delta_carbon_percent)
    print(page_data['delta'])

    times_vals = [3, 6, 9, 12, 15]
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
            new_start = (format_starttime +
                         datetime.timedelta(hours=k)).isoformat()
            print(f"new_start = {new_start}")
            new_end = (format_endtime +
                       datetime.timedelta(hours=k)).isoformat()
            print(f"new_end = {new_end}")

            Key = "displayName"
            Region_Name = az_region
            #token = get_token()

        # finding coords for the passed AZ_region

            areaDict = next(filter(lambda x: x.get(Key) ==
                            Region_Name, az_coords), None)
            if areaDict == None:
                msg = 'use a different region to get a carbon analysis. There was no pre-paired Azure Data center available.'
                return make_response(render_template('data_error.html', msg=msg), 404)

            # calling coords of AZ region
            data_center_latitude = areaDict['metadata']['latitude']
            data_center_longitude = areaDict['metadata']['longitude']

            try:
                data_url = 'https://api2.watttime.org/v2/data'
                headers = {'Authorization': 'Bearer {}'.format(token)}
                params = {'latitude': data_center_latitude, 'longitude': data_center_longitude,
                          'starttime': new_start,
                          'endtime': new_end}
                rsp = requests.get(data_url, headers=headers, params=params)
            except:
                break
            data_check = str.strip(rsp.text[2:7])
            print(data_check)
            if data_check == 'error':
                msg = 'check query parameters. WattTime response contained an error'
                return make_response(render_template('data_error.html', msg=msg), 400)

            elif len(data_check) == 0:
                msg = 'check query parameters. No WattTime response returned.'
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

            # power per time delta
            MegaWatth_per_five3 = MWh_Az3*2.77778e-10
            # pounds of carbon per time delta
            MOER_Az3 = MegaWatth_per_five3*WT_data3['value']
            if len(MOER_Az3.dropna()) < len(az_file['Total']):
                break
            #print(f"MOER_Az3 = {MOER_Az3}")
            # total pounds of carbon in time window
            MOER_Az_day3 = sum(MOER_Az3.dropna())
            print(len(WT_data3['value']))
            print(
                f"New total is {time_carbon_counterfactual} using {Region_Name} ")
            MOER_Az_day3 = MOER_Az_day3

            time_carbon_counterfactual.append(MOER_Az_day3)

        time_carbon_counterfactual_total = pd.DataFrame(
            time_carbon_counterfactual)
        time_carbon_counterfactual_total.columns = ['Sum']

        min_time_carbon_counterfactual = time_carbon_counterfactual_total.iloc[pd.Series(
            time_carbon_counterfactual_total.loc[time_carbon_counterfactual_total['Sum'] == min(time_carbon_counterfactual_total['Sum'])].index)]

        shift_amount = pd.DataFrame(times_vals).iloc[pd.Series(
            min_time_carbon_counterfactual.loc[min_time_carbon_counterfactual['Sum'] == min(min_time_carbon_counterfactual['Sum'])].index)]
        shift_amount.columns = ['hours']
        page_data['time_carbon'] = min_time_carbon_counterfactual['Sum']

        time_carbon_percent = ((float(page_data['total_carbon']) - float(
            page_data['time_carbon']))/float(page_data['total_carbon']))*100
        page_data['delta_shift'] = format(float(time_carbon_percent), '.4g')
        page_data['hour_shift'] = format(float(shift_amount['hours']), '.4g')
    except:
        pass

    if gpuutil_flag == 1:
        return render_template('report_final_util.html', data=page_data, plot1=html_emissions_plot, plot2=html_energy_plot, plot3=html_large_CI_plot, plot4=html_three_mini_plots)
    else:
        return render_template('report_final.html', data=page_data, plot1=html_emissions_plot, plot2=html_energy_plot, plot3=html_large_CI_plot, plot4=html_three_mini_plots)


@app.route('/get_sum_data', methods=["GET", "POST"])
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

    # pull data from WattTime & transform into dataframe
    rsp = gather_watttime(ba, starttime, endtime)
    data = json.loads(rsp.text)
    WT_data = pd.json_normalize(data).dropna()
    WT_data = WT_data.sort_index(ascending=False)
    MWh_Az = AZ_data['Total'].dropna()

    # power per time delta
    MegaWatth_per_five = MWh_Az*2.77778e-10
    # total power in time window
    MegaWatth_total = sum(MegaWatth_per_five)
    # pounds of carbon per time delta
    resource_emissions = MegaWatth_per_five*WT_data['value'].dropna()
    # print(resource_emissions)
    # total pounds of carbon in time window
    resource_emissions_total = sum(resource_emissions.dropna())
    print(len(WT_data['value']))

    return {"Total Carbon Emission (lbs)": resource_emissions_total, "Total Energy Consumed (MWh)": MegaWatth_total}


@app.route('/get_peak_data', methods=["GET", "POST"])
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

    # power per time delta
    MegaWatth_per_five = MWh_Az*2.77778e-10

    # pounds of carbon per time delta
    resource_emissions = MegaWatth_per_five*WT_data['value'].dropna()
    print(resource_emissions)

    plot_data = {'resource_emissions': resource_emissions,
                 'Time': AZ_data['Time'], 'Energy': MegaWatth_per_five}
    df = pd.DataFrame(plot_data)
    # peak id
    peak_c = f"{round(max(resource_emissions), 3)} lbs/per 5 minutes at {df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))]}"
    peak_e = f"{round(max(MegaWatth_per_five), 6)} MWh/per 5 minutes at {df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))]}"
    peak_dict = {"Peak Carbon Emission Time": {"Time_stamp": df['Time'].iloc[resource_emissions.astype(float).idxmax(max(resource_emissions))], "Explaination": peak_c}, "Peak Energy Consumption Time": {
        "Time-stamp": df['Time'].iloc[MegaWatth_per_five.astype(float).idxmax(max(MegaWatth_per_five))], "Explaination": peak_e}}

    peak_data = {}
    peak_data["peak_carbon_timestamp"] = df['Time'].iloc[resource_emissions.astype(
        float).idxmax(max(resource_emissions))]
    peak_data["peak_carbon_time"] = df['Time'].iloc[resource_emissions.astype(
        float).idxmax(max(resource_emissions))]
    peak_data["peak_carbon_date"] = df['Time'].iloc[resource_emissions.astype(
        float).idxmax(max(resource_emissions))]
    peak_data["peak_carbon_val"] = round(max(resource_emissions), 3)
    peak_data["peak_energy_timestamp"] = df['Time'].iloc[MegaWatth_per_five.astype(
        float).idxmax(max(MegaWatth_per_five))]
    peak_data["peak_energy_time"] = df['Time'].iloc[MegaWatth_per_five.astype(
        float).idxmax(max(MegaWatth_per_five))]
    peak_data["peak_energy_date"] = df['Time'].iloc[MegaWatth_per_five.astype(
        float).idxmax(max(MegaWatth_per_five))]
    peak_data["peak_energy_val"] = round(max(MegaWatth_per_five), 6)

    return peak_dict


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


WattTime_abbrevs = {}
WattTime_abbrevs['PJM Roanoke'] = 'PJM_ROANOKE'
WattTime_abbrevs['PJM DC'] = 'PJM_DC'
WattTime_abbrevs['ERCOT San Antonio'] = 'ERCOT_SANANTONIO'
WattTime_abbrevs['PUD No 2 of Grant County'] = 'GCPD'
WattTime_abbrevs['National Electricity Market (Australia)'] = 'NEM'
WattTime_abbrevs['Ireland'] = 'IE'
WattTime_abbrevs['United Kingdom'] = 'UK'
WattTime_abbrevs['Netherlands'] = 'NL'
WattTime_abbrevs['MISO Madison City'] = 'MISO_MASON_CITY'
WattTime_abbrevs['PJM Chicago'] = 'PJM_CHICAGO'
WattTime_abbrevs['California ISO Northern'] = 'CAISO_NORTH'
WattTime_abbrevs['Independent Electricity System Operator (Ontario)'] = 'IESO'
WattTime_abbrevs['France'] = 'FR'
WattTime_abbrevs['Germany and Luxembourg'] = 'DE_LU'
WattTime_abbrevs['PacifiCorp East'] = 'PACE'
WattTime_abbrevs['Hydro Quebec'] = 'HQ'
WattTime_abbrevs['Arizona Public Service Co'] = 'AZPS'
WattTime_abbrevs['Norway'] = 'NO'


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


@app.route('/amulet_test', methods=["GET"])
def amulet_test():
    data_path = './local_files/data_for_table.json'
    if not os.path.exists(data_path):
        print("Cached copy does not exist. Creating first...")
        update_data_table()
    data_for_table = json.load(open(data_path,))
    print(data_for_table)
    return jsonify(data_for_table[-1])


@app.route('/all_index', methods=["GET", "POST"])
def all_index():
    mappy = get_mappy()
    print(f"mappy = {mappy}")
    #mappy.to_csv("Region_Info.csv", encoding='utf-8', index=False )
    # Scatter Map
    # Scatter Map
    fig5 = px.scatter_geo(mappy, lat=mappy['Latitude'], lon=mappy['Longitude'], hover_name=mappy['Azure Region'],
                          hover_data=[mappy['Emission Percent'], mappy['MOER Value']], color=mappy['MOER Value'], title='Global Azure Regions in WattTime Balancing Authorities', template='none')

    fig5 = plotly.io.to_html(fig5)

    # Data table
    # Using bokeh
    data_for_table = mappy[['Azure Region', 'MOER Value']]

    source = ColumnDataSource(data_for_table)

    columns = [
        TableColumn(field="Azure Region", title="Azure Region"),
        TableColumn(field="MOER Value", title="MOER Value"),
    ]

    data_table = DataTable(
        source=source, columns=columns, width=400, height=280)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(data_table)

    return render_template('footprint.html', plot1=fig5,
                           plot_script=script,
                           plot_div=div,
                           js_resources=js_resources,
                           css_resources=css_resources,)


# For /overview route

# 1. Real-time carbon info for BA - from the /get_index_api
# @app.route('/get_index_data', methods=["GET"])
def get_realtime_data(ba):
    token = get_token()
    index_url = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(index_url, headers=headers, params=params)
    return rsp.json()

# 2. % of time at 0g. this is the % of time that the BA has a MOER of 0 over the span of the past week.
# @app.route('/get_percent_zero', methods=["GET"])


def get_percent_zero(ba):
    token = get_token()
    endtime = datetime.datetime.now().isoformat()
    starttime = (datetime.datetime.now() -
                 datetime.timedelta(days=7)).isoformat()
    data_url = 'https://api2.watttime.org/v2/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba,
              'starttime': starttime,
              'endtime': endtime}
    rsp = requests.get(data_url, headers=headers, params=params)

    parsed_rsp = rsp.json()

    count_moer = 0
    count_zero = 0

    for i in parsed_rsp:
        if int(i["value"]) == 0:
            count_zero += 1
        count_moer += 1

    percent_zero = round((count_zero/count_moer)*100, 2)
    return percent_zero

# 3 Average MOER (value) for the last year
# @app.route('/get_average_emission', methods=["GET"])


def get_average_emission(ba):
    token = get_token()
    endtime = datetime.datetime.now().isoformat()
    starttime = (datetime.datetime.now() -
                 datetime.timedelta(days=365)).isoformat()
    data_url = 'https://api2.watttime.org/v2/avgemissions/'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba,
              'starttime': starttime,
              'endtime': endtime}
    rsp = requests.get(data_url, headers=headers, params=params)

    rsp_list = rsp.json()

    count_aoer = len(rsp_list)
    sum_aoer = 0
    if count_aoer == 0:
        avg_aoer = 0
    else:
        for i in rsp_list:
            sum_aoer = sum_aoer + int(i["value"])
        avg_aoer = (sum_aoer/count_aoer)

    return round(avg_aoer, 2)


# /overview api
@app.route('/overview', methods=["GET", "POST"])
def overview():

    try:
        BA_name = request.form.get('data', request.args.get('data'))
        print(f"try BA = {BA_name}")
    except:
        msg = 'check query string for errors in formatting'
        return make_response(render_template('data_error.html', msg), 400)
    try:
        print(f"try BA = {BA_name}")
        if BA_name == 'nada':
            return make_response(render_template('ba_error.html'), 400)
    except:
        msg = 'select a WattTime balancing authority to inspect.'
        return make_response(render_template('data_error.html', msg=msg), 404)
    abbrev = WattTime_abbrevs[BA_name]
    print(f"the BA Abbrev is {abbrev}")
    moer_value = get_realtime_data(abbrev)
    percent_zeros = get_percent_zero(abbrev)
    aoer_value = get_average_emission(abbrev)

    data = {}

    data['moer_value'] = moer_value["moer"]
    data['percent_zeros'] = percent_zeros
    data['aoer_value'] = aoer_value
    data['name'] = BA_name

    token = get_token()
    endtime = datetime.datetime.now().isoformat()
    starttime = (datetime.datetime.now() -
                 datetime.timedelta(days=30)).isoformat()
    data_url = 'https://api2.watttime.org/v2/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': abbrev,
              'starttime': starttime,
              'endtime': endtime}
    rsp = requests.get(data_url, headers=headers, params=params)

    vals = rsp.json()

    # To plot the daily, weekly and monthly carbon emission trends

    if vals[0]['frequency'] != 300:
        daydata = vals[:int(round((len(vals)/30), 0))]
        print(daydata[:3])
        print(len(daydata))
        weekdata = vals[:int(round((len(vals)/4), 0))]
        print(len(weekdata))
        monthdata = vals
        print(len(monthdata))

        MOER_day_time = []
        MOER_day = []
        for x in range(0, len(daydata), int(round((len(daydata)/24), 0))):
            val = daydata[x]['value']
            time = daydata[x]['point_time']
            MOER_day.append(val)
            MOER_day_time.append(time)
        Neat_day = pd.DataFrame([MOER_day_time, MOER_day]).T
        Neat_day.columns = ['Time (UTC)', 'Marginal Carbon Intensity']

        MOER_week_time = []
        MOER_week = []
        for x in range(0, len(weekdata), int(round((len(weekdata)/24), 0))):
            val = weekdata[x]['value']
            time = weekdata[x]['point_time']
            MOER_week.append(val)
            MOER_week_time.append(time)
        Neat_week = pd.DataFrame([MOER_week_time, MOER_week]).T
        Neat_week.columns = ['Time (UTC)', 'Marginal Carbon Intensity']

        MOER_month_time = []
        MOER_month = []
        for x in range(0, len(monthdata), int(round((len(vals)/24), 0))):
            val = monthdata[x]['value']
            time = monthdata[x]['point_time']
            MOER_month.append(val)
            MOER_month_time.append(time)
        Neat_month = pd.DataFrame([MOER_month_time, MOER_month]).T
        Neat_month.columns = ['Time (UTC)', 'Marginal Carbon Intensity']

    else:
        # When frequency == 300
        # 24 hrs in day * 60 mins in an hr / 5 min interval
        daydata = vals[:288]
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
        Neat_day = pd.DataFrame([MOER_day_time, MOER_day]).T
        Neat_day.columns = ['Time (UTC)', 'Marginal Carbon Intensity']

        # Aggregating Moer values over an hour (60/5 = 12)
        MOER_week = []
        MOER_week_time = []
        for x in range(0, len(weekdata), 12):
            aggregated_moer_60mins = 0
            for y in range(x, x+12):
                aggregated_moer_60mins += weekdata[y]['value']
                aggregated_moer_times = weekdata[y]['point_time']
            MOER_week.append(aggregated_moer_60mins//12)
            MOER_week_time.append(aggregated_moer_times)
        Neat_week = pd.DataFrame([MOER_week_time, MOER_week]).T
        Neat_week.columns = ['Time (UTC)', 'Marginal Carbon Intensity']

        try:
            # Aggregating Moer values over 6 hours (6*60/5 = 72)
            MOER_month = []
            MOER_month_time = []
            #print(f"monthdata = {monthdata}")
            print(f"len monthdata = {len(monthdata)}")
            if len(monthdata) == 8640:
                for x in range(0, len(monthdata), 72):
                    aggregated_moer_6hrs = 0
                    for y in range(x, x+72):
                        aggregated_moer_6hrs += monthdata[y]['value']
                        aggregated_moer_times = monthdata[y]['point_time']
                    MOER_month.append(aggregated_moer_6hrs//72)
                    MOER_month_time.append(aggregated_moer_times)
                Neat_month = pd.DataFrame([MOER_month_time, MOER_month]).T
                Neat_month.columns = [
                    'Time (UTC)', 'Marginal Carbon Intensity']
            else:
                msg2 = "Warning, WattTime data for this region is missing records.  Please be sure to inspect point times."
                counter = int(round((len(monthdata)/120 - 1), 0))
                print(counter)
                for x in range(0, len(monthdata), counter):
                    aggregated_moer_6hrs = 0
                    try:
                        for y in range(x, x+counter):
                            aggregated_moer_6hrs += monthdata[y]['value']
                            aggregated_moer_times = monthdata[y]['point_time']
                    except:
                        break
                    MOER_month.append(aggregated_moer_6hrs//counter)
                    MOER_month_time.append(aggregated_moer_times)
                Neat_month = pd.DataFrame([MOER_month_time, MOER_month]).T
                Neat_month.columns = [
                    'Time (UTC)', 'Marginal Carbon Intensity']
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
            count_zero_day += 1
        count_moer_day += 1

    day_zero = round((count_zero_day/count_moer_day)*100, 2)

    # Percent times 0g carbon emission in a week
    count_moer_week = 0
    count_zero_week = 0
    for i in weekdata:
        if int(i["value"]) == 0:
            count_zero_week += 1
        count_moer_week += 1

    week_zero = round((count_zero_week/count_moer_week)*100, 2)

    # Percent times 0g carbon emission in a month
    count_moer_month = 0
    count_zero_month = 0
    for i in monthdata:
        if int(i["value"]) == 0:
            count_zero_month += 1
        count_moer_month += 1

    month_zero = round((count_zero_month/count_moer_month)*100, 2)

    # For passing data to html
    data['day'] = day_zero
    data['week'] = week_zero
    data['month'] = month_zero
    data['num_day_0'] = count_zero_day
    data['num_week_0'] = count_zero_week
    data['num_month_0'] = count_zero_month
    data['avg_day'] = round(statistics.mean(MOER_day), 0)
    data['avg_week'] = round(statistics.mean(MOER_week), 0)
    data['avg_month'] = round(statistics.mean(MOER_month), 0)

    # Bar plots - day, week and month
    day_plot = px.line(data_frame=Neat_day, x='Time (UTC)',
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
    week_plot = px.line(data_frame=Neat_week, x='Time (UTC)',
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
        month_plot = px.line(data_frame=Neat_month, x='Time (UTC)',
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
                                   plot1=html_day_plot,
                                   plot2=html_week_plot,
                                   plot3=html_month_plot,
                                   data=data,
                                   msg=msg2)
    except:
        if len(monthdata) < 8000:
            msg = monthdata[0]['frequency']
            return render_template('region_bad_freq.html',
                                   plot1=html_day_plot,
                                   plot2=html_week_plot,
                                   data=data,
                                   msg=msg)
        else:
            return render_template('region.html',
                                   plot1=html_day_plot,
                                   plot2=html_week_plot,
                                   data=data,
                                   msg=msg2)


@app.route('/pred_shift_find', methods=["GET", "POST"])
def shift_predictions_ui():

    return render_template('pred_shift_find.html')

# get real-time data via lat/lon inputs


def get_realtime_data_loc(lat, lon):
    token = get_token()
    index_url = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'latitude': lat, 'longitude': lon}
    rsp = requests.get(index_url, headers=headers, params=params)
    return rsp.json()

# get a dict of forecast data via balancing authority abbrev


def get_region_forcast(ba):
    token = get_token()
    forecast_url = 'https://api2.watttime.org/v2/forecast'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(forecast_url, headers=headers, params=params)
    return rsp.json()


def find_forecast_min(some_dict, start_index, end_index):
    MOER_preds = pd.DataFrame([some_dict['forecast'][k]['value']
                              for k in range(len(some_dict['forecast']))])
    MOER_preds.columns = ['MOER']
    MOER_preds = MOER_preds['MOER'].iloc[start_index:end_index]
    print(f"MOER_preds now of len = {len(MOER_preds)}")
    MOER_preds = MOER_preds.iloc[:end_index]
    """
    print(f"MOER_preds now of len = {len(MOER_preds)}")
    print(f"MOER_preds is now - {MOER_preds}")
    print(f"the length before finding the min is {len(MOER_preds)}")
    print(f"MOER_preds.loc[MOER_preds == min(MOER_preds) = {int(MOER_preds.loc[MOER_preds == min(MOER_preds)].index.values)}")
    """
    index_loc = int(MOER_preds.loc[MOER_preds == min(MOER_preds)].index.values)
    print(f"index_loc = {index_loc}")
    min_occur = some_dict['forecast'][index_loc]
    return min_occur

# round to closest 5 min


def roundTime(dtt=None, roundTo=5*60):
    if dtt == None:
        dtt = datetime.datetime.now()
        seconds = (dtt.replace(tzinfo=None) - dtt.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        return dtt + datetime.timedelta(0, rounding-seconds, -dtt.microsecond)
    else:
        dtt = dt.fromisoformat(dtt)
        seconds = (dtt.replace(tzinfo=None) - dtt.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        return dtt + datetime.timedelta(0, rounding-seconds, -dtt.microsecond)


def get_mean_window_time(some_dict, start_time, window_size):
    """
    the start_time is appended to the end of the list, so we can calculate its datetime format
    at the same time as the other ranges. 
    """
    forecast_dict = some_dict['forecast']
    print("=========================")
    # print(forecast_dict)
    print("=========================")
    point_time_strings = [time['point_time'] for time in forecast_dict]
    point_time_strings.append(start_time)
    moers = [moer['value'] for moer in forecast_dict]
    point_times = []
    pattern = r'(\d{4}-\d{1,2}-\d{1,2}).*(\d{2}:\d{2}:\d{2})'
    for point_time in point_time_strings:
        match = re.search(pattern, point_time)
        #print(match.group(1), match.group(2))
        # break
        year, month, day = [int(ymd) for ymd in match.group(
            1).split("-")]  # ymd = year month date
        hour, minute, second = [int(hms) for hms in match.group(2).split(":")]
        point_times.append(datetime.datetime(
            year, month, day, hour, minute, second))

    delta_minutes = int(window_size)
    # Removes last element of the list which is the starting time to look out for and saves
    start_time = point_times.pop()
    end_time = start_time + datetime.timedelta(minutes=delta_minutes)
    print(f"No shift start time: {start_time}. Its end time: {end_time}")
    moer_vals = []  # Holds MOER values that fit within start_time and start_time + delta_minutes
    for index, moer in enumerate(moers):
        # If the current window of time being examined goes past the last point time, break.
        if end_time > point_times[-1]:
            break
        current_time = point_times[index]
        if current_time >= start_time and current_time <= end_time:
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
        year, month, day = [int(ymd) for ymd in match.group(
            1).split("-")]  # ymd = year month date
        hour, minute, second = [int(hms) for hms in match.group(2).split(":")]
        point_times.append(datetime.datetime(
            year, month, day, hour, minute, second))
    # print(point_times)
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
    min_moer_vals = []  # Confirmation.
    for index, moer in enumerate(moers):
        # Current moer total added up. num_moers = how many elements we've added to calculate the mean.

        # will hold the current time window's worth of moers.
        current_moer_vals = []

        # end_time is the upper datetime limit. If the current time we're examining is
        # greater than this, we've passed the window size.
        end_time = point_times[index] + datetime.timedelta(minutes=window_size)

        # If the current window of time being examined goes past the last point time, break.
        if end_time > point_times[-1]:
            break
        for moer, point_time in zip(moers[index:], point_times[index:]):
            if point_time > end_time:
                break  # past window_size if so
            current_moer_vals.append(moer)
        current_moer_mean = sum(current_moer_vals) / len(current_moer_vals)
        if current_moer_mean < min_moer_mean:
            min_index = index
            min_moer_mean = current_moer_mean
            min_moer_vals = current_moer_vals

    print(
        f"Current starting time with window size of {window_size} minutes is {point_times[min_index]} UTC")
    print(f"The average MOER value during this time window is {min_moer_mean}")
    print(f"Minimum index is {min_index}")
    print(
        f"Here is a list of the point_times in that window for confirmation:\n {min_moer_vals}")
    # Time format: 2021-07-23T21:30:00+00:00
    """
    print("NEW VALUES")
    print(point_time[:5])
    print(moers[:5])
    print(type(point_time[0]))
    print(type(moers[0]))
    """

    # forecast_dict = {'point_time': forecast_dict['forecast']['point_time'],
    #                    'value': forecast_dict['forecast']['value']}
    # print(forecast_dict)

    # print(some_dict)
    #MOER_preds = pd.DataFrame([some_dict['forecast'][k]['value'] for k in range(len(some_dict['forecast']))])
    #print("Moer preds is!!!", MOER_preds)
    print("=========================================")
    min_window_dict = {'point_time': forecast_dict[min_index]['point_time'],
                       'value': min_moer_mean,
                       'ba': forecast_dict[min_index]['ba']
                       }
    return min_window_dict
    # return forecast_dict[min_index]


@app.route('/shift_predictions', methods=["GET", "POST"])
def shift_predictions():
    print('step 1')
    WT_names = pd.DataFrame([json.loads(x) for x in WT_Regions])[
        ['name', 'abbrev']].dropna()
    # set the shift type and direct

    shift_type = request.args.get('data_shifter', None)
    print(f"GET shift_type = {shift_type}")

    if shift_type != None:
        print('shift_choice is not equal to none')
        print(shift_type)
        dc_location = request.args.get('data_az', None)
        dc_balancing_authority = request.args.get('data_ba', None)
        if dc_balancing_authority != None:
            dc_location = dc_balancing_authority
            print(
                f"now dc_location is the balancing authority {dc_balancing_authority}")
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
            print(shift_type)
            dc_location = request.form.get('data_az', None)
            print(f"dc_location is {dc_location}")
            dc_balancing_authority = request.form.get('data_ba', None)
            print(f"dc_balancing_authority is {dc_balancing_authority}")
            # id the drop down choice and make sure there is 1 and only 1 chosen
            if dc_location == 'nada':
                dc_location = dc_balancing_authority
                print(
                    f"now dc_location is the balancing authority {dc_balancing_authority}")
            else:
                print(f"dc_location didn't change and is {dc_location}")
                if dc_balancing_authority != 'nada':
                    msg = 'only select one Region type'
                    return make_response(render_template('pred_error.html', msg=msg), 400)

            WT_names = WT_names.reset_index()
            print(WT_names)
            print(f"tring to call from df {WT_names['name'][1]}")
            print(f"the shift type is {shift_type}")
            if shift_type == 'nada':
                msg = 'select a shift type.'
                return make_response(render_template('pred_error.html', msg=msg), 404)
        except:
            msg = 'begin a search first'
            return make_response(render_template('pred_error.html', msg=msg), 502)

    ######
    # BOTH GEOGRAPHIC AND TIME SHIFTING
    ######

    if shift_type == 'Geographic and Time Shift':
        print('step 2.geotime')
        # determine if AZ or BA was input
        # determine if AZ or BA was input

        WT_names = WT_names.reset_index()
        print(WT_names)
        print(f"tring to call from df {WT_names['name'][1]}")

        # find what name matches:abbrev pair
        for l in range(len(WT_names)):
            if WT_names['name'][l] == dc_location:
                region_ba = dc_location
                print(f"region_ba is {dc_location}")
                print(f"found match at {l}")
                print(f"input = {dc_location}")
                print(f"match = {WT_names['name'][l]}")

        # get helper data using balancing authority or
        try:
            data = from_ba_helper(region_ba)
            print(f"data clue of (region_ba) = {data}")

        except:
            try:
                data = getloc_helper(dc_location)
                print(f"data clue of (region_az) = {data}")
            except:
                msg = 'please try a different search.'
                return make_response(render_template('pred_error.html', msg=msg), 400)

        az_region = data['AZ_Region']
        print(az_region)
        az_coords = get_az()

        try:
            geo_time_shift_data = geotime_shift()
        except ZeroDivisionError:
            try:

                SKU_table = get_SKU_table()
                sensitive_check_box = request.form.get('sensitive', 'off')
                desired_GPU = request.form.get('gpu_type', None)
                filter_list = Law_filter(
                    SKU_table, sensitive_check_box, az_region)
                filtered_regions_list = Gpu_filter(filter_list, desired_GPU)

                data = get_current_min_region(filtered_regions_list, az_region)
                print(f"data package is {data}")
                return render_template('load_shift_eval_2.html', data=data)
            except:
                print(
                    "input region does not have desired resource. no data for comparison.")
                msg = 'begin with a region that has the desired resource to make a predictive comparison.'
                return make_response(render_template('pred_error.html', msg=msg), 400)

        # print(geo_time_shift_data)
        return render_template('load_shift_eval_geotime.html', data=geo_time_shift_data)


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
            for l in range(len(WT_names)):
                if WT_names['name'][l] == dc_location:
                    region_ba = dc_location
                    print(f"region_ba is {dc_location}")
                    print(f"found match at {l}")
                    print(f"input = {dc_location}")
                    print(f"match = {WT_names['name'][l]}")
                    print('using dc_location')
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
                return make_response(render_template('pred_error.html', msg=msg), 400)

        az_region = data['AZ_Region']
        print(az_region)
        az_coords = get_az()

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
        window_size_hours, window_size_minutes = (
            request.form['window_size_hours']), (request.form['window_size_minutes'])

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
        print(
            f"\n=======\nQuerying with window size of {window_size_hours} hours and {window_size_minutes} minutes\n========\n")
        print(
            f"Delta minutes (Window size in minutes) is {window_size} minutes")

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
        # finding coords for the Az Regions in the geography
        window_moer = []
        window_data_center = []
        for data_center in range(len(filtered_emissions_list)):
            emissions_avg = filtered_emissions_list[data_center]['average_moer_value']
            window_moer.append(emissions_avg)
            window_data_center.append(filtered_emissions_list[data_center])
        try:
            current_region_moer = region_data[DISPLAY_TO_NAME[az_region]
                                              ]['average_moer_value']
        except KeyError:
            data = get_current_min_region(filtered_regions_list, az_region)
            print(f"data package is {data}")
            return render_template('load_shift_eval_2.html', data=data)

        minimum_window_moer = min(window_moer)
        minimum_window_moer_index = window_moer.index(minimum_window_moer)
        minimum_region = window_data_center[minimum_window_moer_index]['data_center_name']
        percent_difference = 100 * \
            (current_region_moer - minimum_window_moer)/current_region_moer

        print(f"minimum_window_moer = {minimum_window_moer}")
        print(f"minumum_region = {minimum_region}")
        minimum_region_ba = getloc_helper(
            NAME_TO_DISPLAY[minimum_region])['name']

        page_data = {}
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
            response['shiftAZ'] = page_data['shiftAZ']

        except:
            response['shiftDateTime'] = dt.now().isoformat()
            response['shift_perc'] = page_data['shift_perc']
            response['shiftAZ'] = page_data['shiftAZ']

        if request.method == 'POST':
            # For output interface
            return render_template('load_shift_geo_eval.html', data=page_data)
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
        WT_names = WT_names
        print('step 2.time')

       # find what name matches:abbrev pair
        try:
            for l in range(len(WT_names)):
                if WT_names['name'][l] == dc_location:
                    region_ba = dc_location
                    print(f"region_ba is {dc_location}")
                    print(f"found match at {l}")
                    print(f"input = {dc_location}")
                    print(f"match = {WT_names['name'][l]}")
                    print('using dc_location')
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
                return make_response(render_template('pred_error.html', msg=msg), 400)

        print(f"data = {data}")
        az_region = data['AZ_Region']
        print(az_region)
        az_coords = get_az()

        # finding coords for the Az Regions in the geography
        geo = []

        Key = "displayName"
        Region_Name = az_region

    # finding coords for the passed AZ_region

        areaDict = next(filter(lambda x: x.get(Key) ==
                        Region_Name, az_coords), None)
        if areaDict == None:
            msg = 'use a different region to get a carbon analysis. There was no pre-paired Azure Data center available.'
            return make_response(render_template('pred_error.html', msg=msg), 404)

        # calling coords of AZ region
        data_center_latitude = areaDict['metadata']['latitude']
        data_center_longitude = areaDict['metadata']['longitude']

        # getting data to choose geogrpahy
        realT = get_realtime_data_loc(
            data_center_latitude, data_center_longitude)
        print(realT)

        try:
            geo.append(
                {'percent': realT['percent'], 'abbrev': realT['ba'], 'moer': realT['moer']})
        except:
            pass

        # making sure data was retrieved
        try:
            print(f"the MOER of {geo[0]['abbrev']} is {geo[0]['moer']}")
        except:
            print(f"No WattTime data was available for {az_region}")
            msg = 'use a Azure region supported by a WattTime balancing authority'
            return make_response(render_template('pred_error.html', msg=msg), 404)

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
            return make_response(render_template('pred_error.html', msg=msg), 404)
        end = request.form.get('endtime', None)
        if end != None:
            if len(end) == 0:
                end = str(datetime.datetime.now() +
                          datetime.timedelta(hours=24))
            end = end.upper()
        else:
            end = end = str(datetime.datetime.now() +
                            datetime.timedelta(hours=24))
        print('swagger starttime works')

        try:
            endtime = parser.parse(end, tzinfos=timezone_info).isoformat()
            print(f"input end {endtime}")
        except:
            msg = 'verify correct format of query times'
            return make_response(render_template('pred_error.html', msg=msg), 400)

        #window_size = request.form['window_size']
        window_size_hours, window_size_minutes = (
            request.form['window_size_hours']), (request.form['window_size_minutes'])

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
        print(
            f"\n=======\nQuerying with window size of {window_size_hours} hours and {window_size_minutes} minutes\n========\n")
        print(
            f"Delta minutes (Window size in minutes) is {window_size} minutes")
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
        # if no MOER forecast data available for the region submethod of only geog shift w/ no time shift
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
                return render_template('load_shift_eval_2.html', data=data)
            else:
                msg = 'use a Region which has marginal forecast data from WattTime.'
                return make_response(render_template('pred_error.html', msg=msg), 400)

        #print(f"pred_forecast = {pred_forecast}")

        # df to parse with input time window
        time_filter = pd.DataFrame(
            [pred_forecast['forecast'][k] for k in range(len(pred_forecast['forecast']))])

        for i in range(len(time_filter["point_time"])):
            time_filter["point_time"][i] = time_filter["point_time"][i].split(
                '+')[0]
            # print(time_filter["point_time"][i])

        print(f"in {rounded_starttime}")
        print(f"in {rounded_endtime}")

        # formatting start and end times to be able to find a match to create window
        starttime = pd.to_datetime([rounded_starttime], utc=True)
        starttime = str(starttime).split("'")[1]
        starttime = str(starttime).replace(" ", "T")
        endtime = pd.to_datetime([rounded_endtime], utc=True)
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
        # print(pred_forecast)

        pred_best_shift = find_forecast_window_min(
            pred_forecast, start_ind, end_ind, window_size)
        print(f"pred_best_shift = {pred_best_shift}")
        #print(f"the length of pred_best_shift is {len(pred_best_shift)}")
        # data checks
        print(
            f"pred_forecast min = {find_forecast_window_min(pred_forecast, start_ind, end_ind, window_size)}")
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
        page_data['shiftBA'] = list(WattTime_abbrevs.keys())[list(
            WattTime_abbrevs.values()).index(new_region['name'])]
        page_data['shiftTime'] = pred_best_shift['point_time']
        page_data['no_shiftTime'] = rt_in_reg['point_time']
        page_data['shiftMOER'] = pred_best_shift['value']

        def get_noshift_moer(rt_in_reg, window_size):
            pass
        # def get_mean_window_time(some_dict, start_time, window_size):
        page_data['no_shiftMOER'] = get_mean_window_time(
            pred_forecast, rt_in_reg['point_time'], window_size)  # rt_in_reg['moer']
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

        page_data['shift_delta'] = dt.strptime(
            shiftDateTime, FMT) - dt.strptime(no_shiftDateTime, FMT)
        shift_perc = ((float(page_data['no_shiftMOER']) - float(
            page_data['shiftMOER']))/float(page_data['no_shiftMOER']))*100
        page_data['shift_perc'] = round(shift_perc, 2)
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
            response['shiftAZ'] = page_data['shiftAZ']

        except:
            response['shiftDateTime'] = dt.now().isoformat()
            response['shift_perc'] = page_data['shift_perc']
            response['shiftAZ'] = page_data['shiftAZ']

        if request.method == 'POST':
            # For output interface
            return render_template('load_shift_eval.html', data=page_data)
        else:
            return response

    else:
        msg = 'select a shifting type.'
        return make_response(render_template('pred_error.html', msg=msg), 400)


@app.route('/get_timeseries_table_data', methods=["GET", "POST"])
def get_timeseries_table_data():
    token = get_token()
    filename = request.args.get("filename", None)
    checker = str(filename)
    if checker[-3:] == 'csv':
        az_file = pd.read_csv(checker).dropna()
        if len(az_file.columns) != 3:
            if len(az_file.columns) != 2:
                msg = 'use either a .xlsx, .csv, or .json file with the  proper column formatting.'
                return make_response(render_template('data_error.html', msg=msg), 411)
            else:
                az_file.columns = ['Time', 'Total']
        else:
            az_file.columns = ['Index', 'Time', 'Total']

        print(az_file['Time'].dtype)
        print(az_file['Total'].dtype)

        try:
            assert az_file['Time'].dtype == 'object'

        except:
            msg = 'use either a .xlsx, .csv, or .json file with the proper data type formats.'
            return make_response(render_template('data_error.html', msg=msg), 412)

    elif checker[-4:] == 'json':
        Monitor_data = json.load(open(checker))
        az_file = pd.DataFrame(
            Monitor_data['value'][0]['timeseries'][0]['data']).dropna()
        az_file.columns = ['Time', 'Total']
        print(az_file[:3])

    elif checker[-4:] == 'xlsx':
        az_file = pd.read_excel(checker)[10:].dropna()
        # print(az_file)
        if len(az_file.columns) != 3:
            if len(az_file.columns) != 2:
                msg = 'use either a .xlsx, .csv, or .json file with the proper column formatting.'
                return make_response(render_template('data_error.html', msg=msg), 411)
            else:
                az_file.columns = ['Time', 'Total']
                az_file = az_file.reset_index()
                print(az_file)
                print(az_file['Time'])
                pd.to_numeric(az_file['Total'])
        else:
            az_file.columns = ['Index', 'Time', 'Total']
        # print(az_file)
        print(az_file['Time'].dtype)
        print(az_file['Total'].dtype)

    else:
        msg = 'input a valid .xlsx, .csv, or .json file'
        return make_response(render_template('data_error.html', msg=msg), 413)

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
            set1 = '9:40:00'
            set2 = '9:45:00'
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
            set1 = '9:40'
            set2 = '9:45'
            FMT = '%H:%M'
            bench = dt.strptime(set2, FMT) - dt.strptime(set1, FMT)
            print(f"bench = {bench}")
            tdelta = dt.strptime(t2, FMT) - dt.strptime(t1, FMT)

            print(f"tdelta = {tdelta}")

        if tdelta != bench:
            msg = 'use either a .xlsx, .csv, or .json file with 5 min time aggregation.'
            return make_response(render_template('data_error.html', msg=msg), 415)
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
            msg = 'check query parameters. WattTime response contained an error'
            return make_response(render_template('data_error.html', msg=msg), 400)
        elif len(data_check) == 0:
            msg = 'check query parameters. No WattTime response returned.'
            return make_response(render_template('data_error.html', msg=msg), 404)
        data = json.loads(rsp.text)

        WT_data = pd.json_normalize(data).dropna()
        WT_data = WT_data.sort_index(ascending=False)
        MWh_Az = AZ_data['Total'].dropna()

        # power per time delta
        MegaWatth_per_five = MWh_Az*2.77778e-10
        # pounds of carbon per time delta
        resource_emissions = MegaWatth_per_five*WT_data['value'].dropna()
        # print(resource_emissions)

        plot_data = {'resource_emissions': resource_emissions,
                     'Time': AZ_data['Time'], 'Energy': MegaWatth_per_five}
        df = pd.DataFrame(plot_data)

        # peak id

        df.columns = ['Carbon Emitted (lbs)', 'Time', 'Energy (MWh)']
        print(f"the DataFrame v1 is {df[:10]}")

        time_series_data = df.to_dict()
        print(time_series_data)

    except:
        msg = 'check that query parameters match file values.'
        return make_response(render_template('data_error.html', msg=msg), 404)

    df.to_csv("./local_files/time_series_table_data.csv")
    return send_file('./local_files/time_series_table_data.csv',
                     mimetype='text/csv',
                     attachment_filename="time_series_table_data.csv",
                     as_attachment=True)

    #time_series_data = df.to_dict()

    # return time_series_data


"""
MSAI ENDPOINT
REQUIRED: current azure region, current timestamp (datetime.datetime.now()), desired SKU (string), sensitive data (logical response)
Filter down the regions to be parsed by 
SKU availability
data sensitivity 
law flags
Using the cached forecast data
- Find sum of MOER for each region left after filtering for the length of the run window
- Find %-diff of other region's cumulative MOER compared to the input region's sum
"""


@app.route('/msai', methods=["GET"])
def msai_endpoint():
    # update_all_regions_forecast_data() # FOR TESTING. Remove in production
    # If file doesn't exist, run the update function to generate the cached file first then open this same file.
    if not os.path.isfile("./local_files/all_regions_forecasts.json"):
        print("All Region forecast data exists... Using existing cache.")
        update_all_regions_forecast_data()
    with open("./local_files/all_regions_forecasts.json", "r") as file_in:
        # Read in as string json. doing a second json.loads deserializes into json/dict object.
        all_regions_forecasts = json.loads(json.load(file_in))

    """
    What datetime.datetime.now() does: Will grab the local machine time. Mine is in Pacific Time which is 7 hours behind UTC... 
    But the Watt-time api returns times in UTC. 
    So... We grab the local time as in UTC, however this sets the tzinfo abstract class within the datetime.datetime. 
    The datetime library does not let you compare naive objects (datetime objects without tzinfo set) and aware objects (datetime objects
    with tzinfo set). So... we grab the time in UTC, then essentially set the tzinfo to None to be able to compare later. 
    """
    current_time = datetime.datetime.now(
        tz=datetime.timezone.utc).replace(tzinfo=None)

    # Given as display name. Convert to region name
    current_region = request.args.get("data_center_name", 'East US')

    # print(DISPLAY_TO_NAME)
    try:
        current_region = DISPLAY_TO_NAME[current_region]
    except:
        pass

    # TODO: Change each to request.form.get(...) with HTML page
    SKU_table = get_SKU_table()
    # Change this to request.form.get with HTML page added on
    sensitive_check_box = request.args.get('sensitive', 'off')
    # Change this to request.form.get with HTML page added on
    desired_GPU = request.args.get("gpu_type", "nada")
    # sensitive_check_box == 'on':
    filter_list = Law_filter(SKU_table, sensitive_check_box, current_region)
    filtered_regions_list = Gpu_filter(filter_list, desired_GPU)
    # if current region does not have desired GPU, allows search to still happen.
    if NAME_TO_DISPLAY[current_region] not in filtered_regions_list:
        filtered_regions_list.append(NAME_TO_DISPLAY[current_region])

    print('/n =============================')
    print('made it past the error handle')

    print(
        f"Based on GPU and Law filtering, geo and time-shifting over these regions:\n{filtered_regions_list}")
    # Grabbing window size and converting to minutes.

    deltaminutes = int(request.args.get("window_size_minutes", 60))

    if deltaminutes < 30:
        deltaminutes = MINUTES_IN_HOUR

    all_region_moer_comparison = {}
    all_region_moer_comparison['current_region'] = current_region
    for az_region, time_moer in all_regions_forecasts.items():
        print("==========================================================")
        displayName = NAME_TO_DISPLAY[az_region]
        if displayName not in filtered_regions_list:
            print(
                f"Region: {displayName} not in filtered list for LAW and GPU. Skipping\n")
            continue
        all_region_moer_comparison[az_region] = {}
        point_times, moer_vals = time_moer['point_times'], time_moer['values']
        print(
            f"Region being searched: {az_region}, Current Region Selected: {current_region}")
        """
        if current_region == displayName: # find average window value for current region given the current time
            for moer, point_time in zip(moer_vals, point_times):
                point_time = datetime.datetime.fromisoformat(point_time)
                if point_time > current_time + datetime.timedelta(minutes=deltaminutes):
                    break
                if point_time >= current_time and point_time <= current_time + datetime.timedelta(minutes=deltaminutes):
                    current_region_moers.append(moer)
        """
        current_moer_sum = - \
            1  # If we see a -1, it just means there wasn't any forecast data available.
        end_time = current_time + datetime.timedelta(minutes=deltaminutes)
        for moer_val, point_time in zip(moer_vals, point_times):
            point_time = datetime.datetime.fromisoformat(point_time)
            # If the ending time is greater than the last point_time, we are not getting a full window size.
            if end_time > datetime.datetime.fromisoformat(point_times[-1]) or point_time > end_time:
                break
            if point_time < current_time:
                continue
            current_moer_sum += moer_val
            # for moer, point_time in zip(moer_vals[index:], point_times[index:]):
            #    point_time = datetime.datetime.fromisoformat(point_time) # string datetime --> datetime object
            #    current_moer_vals.append(moer)
        all_region_moer_comparison[az_region]['moer_avg'] = current_moer_sum/(
            deltaminutes/5)

    current_region_moer_sum = all_region_moer_comparison[current_region]['moer_avg']
    for region in all_region_moer_comparison.keys():
        if region == current_region or region == "current_region":
            continue  # A key dictating the current region selected is in there. Also skip doing a comparison for the current region. 0% increase/decrease
        # print(all_region_moer_comparison[region])
        # continue
        region_sum = all_region_moer_comparison[region]['moer_avg']
        perc_diff = ((region_sum - current_region_moer_sum) /
                     current_region_moer_sum) * 100
        print(region, perc_diff)
        all_region_moer_comparison[region]['perc_diff'] = round(perc_diff, 2)
    return all_region_moer_comparison


"""
COMBINATION SHIFTING
REFERENCE: 
INPUT: 
    - current azure region, current timestamp (datetime.datetime.now()), desired SKU (string), sensitive data (logical response), 
    - ADDED ON: ?window_hours and ?window_minutes to calculate window size. This will probably be simplified with a webpage later on.
PROCESS:
    - find %-diff between running now in current region and greenest time in new region
RETURN:
    - input region
    - suggested region
    - green start time
    - %-diff of windows
    - time until greenest start time
    - supporting balancing authority 
"""


@app.route('/geotime_shift', methods=["GET"])
def geotime_shift():
    # update_all_regions_forecast_data() # FOR TESTING. Remove in production
    # If file doesn't exist, run the update function to generate the cached file first then open this same file.
    if not os.path.isfile("./local_files/all_regions_forecasts.json"):
        print("All Region forecast data exists... Using existing cache.")
        update_all_regions_forecast_data()
    with open("./local_files/all_regions_forecasts.json", "r") as file_in:
        # Read in as string json. doing a second json.loads deserializes into json/dict object.
        all_regions_forecasts = json.loads(json.load(file_in))

    """
    What datetime.datetime.now() does: Will grab the local machine time. Mine is in Pacific Time which is 7 hours behind UTC... 
    But the Watt-time api returns times in UTC. 
    So... We grab the local time as in UTC, however this sets the tzinfo abstract class within the datetime.datetime. 
    The datetime library does not let you compare naive objects (datetime objects without tzinfo set) and aware objects (datetime objects
    with tzinfo set). So... we grab the time in UTC, then essentially set the tzinfo to None to be able to compare later. 
    """
    current_time = datetime.datetime.now(
        tz=datetime.timezone.utc).replace(tzinfo=None)

    current_region = request.form.get("data_az")
    SKU_table = get_SKU_table()
    # Change this to request.form.get with HTML page added on
    sensitive_check_box = request.form.get('sensitive', 'off')
    # Change this to request.form.get with HTML page added on
    desired_GPU = request.form.get("gpu_type", "nada")
    filter_list = Law_filter(SKU_table, sensitive_check_box, current_region)
    try:
        filtered_regions_list = Gpu_filter(filter_list, desired_GPU)
    except KeyError:
        msg = 'verify chosen resource GPU. This GPU is unavailable in current workspace location'
        return make_response(render_template('data_error.html', msg=msg), 404)

    print('/n =============================')
    print('made it past the error handle')

    print(
        f"Based on GPU and Law filtering, geo and time-shifting over these regions:\n{filtered_regions_list}")
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
    if deltaminutes < 30:
        deltaminutes = 30
    print(
        f"Querying with the following, CURRENT_AZ_REGION of {current_region}, CURRENT_TIME of {current_time}, WINDOW_SIZE of {deltaminutes} minutes")
    # These variables keep track of which region had the minimum average MOER value for the given window size as well as that given value.
    minimum_region, minimum_avg_moer, greenest_starttime = None, float(
        "inf"), datetime.datetime.now()
    # Variables to keep track of current region's average moer for the given window.
    current_region_moers = []
    for az_region, time_moer in all_regions_forecasts.items():
        print("==========================================================")
        displayName = all_regions_forecasts[az_region]['displayName']
        print(az_region, displayName)
        if displayName not in filtered_regions_list:
            print(
                f"Region: {displayName} not in filtered list for LAW and GPU. Skipping\n")
            continue
        print(f"Display name of current region: {displayName}")
        print(
            f"Region in filtered list?: {displayName in filtered_regions_list}")
        print()
        point_times, moer_vals = time_moer['point_times'], time_moer['values']
        print(
            f"Region being searched: {az_region}, Current Region Selected: {current_region}")
        if current_region == displayName:  # find average window value for current region given the current time
            for moer, point_time in zip(moer_vals, point_times):
                point_time = datetime.datetime.fromisoformat(point_time)
                if point_time > current_time + datetime.timedelta(minutes=deltaminutes):
                    break
                if point_time >= current_time and point_time <= current_time + datetime.timedelta(minutes=deltaminutes):
                    current_region_moers.append(moer)

        for index, time in enumerate(point_times):
            current_moer_vals = []  # keep track of the current window
            # convert datetime string format to datetime object for comparison
            start_time = datetime.datetime.fromisoformat(point_times[index])
            end_time = start_time + datetime.timedelta(minutes=deltaminutes)

            # If the ending time is greater than the last point_time, we are not getting a full window size.
            if end_time > datetime.datetime.fromisoformat(point_times[-1]):
                break

            for moer, point_time in zip(moer_vals[index:], point_times[index:]):
                point_time = datetime.datetime.fromisoformat(
                    point_time)  # string datetime --> datetime object
                if point_time > end_time:
                    break
                current_moer_vals.append(moer)

            average_moer = sum(current_moer_vals) / len(current_moer_vals)

            if average_moer < minimum_avg_moer:
                minimum_region, minimum_avg_moer = az_region, average_moer
                greenest_starttime = time

    current_region_avg = sum(current_region_moers) / len(current_region_moers)
    perc_diff = ((current_region_avg - minimum_avg_moer) /
                 current_region_avg) * 100
    ba = all_regions_forecasts[minimum_region]['ba']
    return_dict = {
        'current_region': current_region,
        'current_region_avg': current_region_avg,
        'current_starttime': current_time.isoformat(),
        'greenest_region': NAME_TO_DISPLAY[minimum_region], 'greenest_starttime': greenest_starttime,
        'greenest_region_BA': ba,
        'minimum_avg_moer': minimum_avg_moer, 'percentage_decrease': round(perc_diff, 2),
        'window_size_in_minutes': deltaminutes
    }
    # print(return_dict)
    # Need to return as normal dictionary. Don't use jsonify(). It'll return as a response object.
    return return_dict


def get_avg_moer(region_name, starting_time, deltaminutes=60):
    with open("./local_files/all_regions_forecasts.json", "r") as file_in:
        # Read in as string json. doing a second json.loads deserializes into json/dict object.
        all_regions_forecasts = json.loads(json.load(file_in))
    # Means there's no forecast data for this region.
    if region_name not in all_regions_forecasts.keys():
        return None

    point_times, moer_vals = all_regions_forecasts[region_name][
        'point_times'], all_regions_forecasts[region_name]['values']
    ending_time = starting_time + datetime.timedelta(minutes=deltaminutes)
    valid_moer_vals = []
    for point_time, moer_val in zip(point_times, moer_vals):
        point_time = dt.fromisoformat(point_time)
        if point_time >= starting_time and point_time <= ending_time:
            valid_moer_vals.append(moer_val)
    # Current time not found within the forecasted data. The all regions forecast json file may be outdated.
    if not valid_moer_vals:
        return -1
    return sum(valid_moer_vals) / len(valid_moer_vals)


@app.route('/amulet', methods=["GET"])
def amulet_endpoint():
    # region_name = request.args.get("data_center_name", 'westus2') #default to MSFT Washington DC

    # default to 60 minutes for window size
    deltaminutes = int(request.args.get("window_size_minutes", 60))
    # NameError

    # if not region_name:
    #    print("Invalid region name. TODO: Display error page")
    # If a valid region display name was chosen/given

    # If file doesn't exist, run the update function to generate the cached file first then open this same file.
    if not os.path.isfile("./local_files/all_regions_forecasts.json"):
        update_all_regions_forecast_data()
    else:
        print("All Region forecast data exists... Using existing cache.")

    # with open("./local_files/all_regions_forecasts.json", "r") as file_in:
    #    all_regions_forecasts = json.loads(json.load(file_in)) # Read in as string json. doing a second json.loads deserializes into json/dict object.
    current_time = datetime.datetime.now(
        tz=datetime.timezone.utc).replace(tzinfo=None)
    return_dict = {}
    for region_name in NAME_TO_DISPLAY.keys():  # keys are all the AZ region names.
        avg_moer_value = get_avg_moer(
            region_name=region_name, starting_time=current_time, deltaminutes=deltaminutes)
        if not avg_moer_value:
            #print(f"No forecast data available for the region: {region_name}")
            continue
        if avg_moer_value == -1:
            print("Current time not found within the forecasted data... check the forecast JSON file under local_files")
            continue
        return_dict[region_name] = {
            'data_center_name': region_name,
            'current_starttime': current_time.isoformat(),
            'window_size_minutes': deltaminutes,
            'average_moer_value': avg_moer_value
        }
    return return_dict

    """
    return_dict = {
        'data_center_name' : region_name,
        'current_starttime' : current_time.isoformat(),
        'window_size_minutes' : deltaminutes,
        'average_moer_value' : avg_moer_value
    }
    """


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


@app.route('/get_current_min_region', methods=["GET"])
def get_current_min_region(filtered_regions_list, current_region):
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

    region_average_dict = {}
    # taking average of last 3 MOER for each region
    for n in position_numbers:
        average_moer = (region_history_dict[0]["MOER Value"][n]
                        + region_history_dict[1]["MOER Value"][n]
                        + region_history_dict[2]["MOER Value"][n])/3
        region_average_dict[n] = {"average_moer": average_moer}
    # grabbing just the averaged moer values
    moer_val_list = []
    for entry in region_average_dict:
        moer_val_list.append(float(region_average_dict[entry]["average_moer"]))
    # find min moer
    moer_min = min(moer_val_list)
    # find region with min moer, will return multiple if equal moer values at multiple regions with desired GPU
    min_region_name = []
    for entry in region_average_dict:
        if float(region_average_dict[entry]["average_moer"]) == moer_min:
            min_region_name.append(
                region_history_dict[0]["Azure Region"][entry])

    #print(f"final moer_min is {moer_min}")
    print(f"final min_region_name is {min_region_name[0]}")

    min_region_data = getloc_helper(min_region_name[0])
    current_region_info = getloc_helper(current_region)
    current_region_data = get_realtime_data(current_region_info['abbrev'])
    print(current_region_data['moer'])

    print(f"current region moer is {current_region_data}")
    geo_shift_perc_diff = 100 * \
        (float(current_region_data['moer']) -
         float(moer_min))/float(current_region_data['moer'])

    data_package = {}
    data_package['min_moer_region'] = min_region_name[0]
    data_package['shiftBA'] = min_region_data['name']
    data_package['shift_perc'] = round(geo_shift_perc_diff, 2)
    data_package['inputRegion'] = current_region
    data_package['inputBA'] = current_region_info['name']

    return data_package


def geo_shifting(window_size):

    # if not region_name:
    #    print("Invalid region name. TODO: Display error page")
    # If a valid region display name was chosen/given

    # If file doesn't exist, run the update function to generate the cached file first then open this same file.
    if not os.path.isfile("./local_files/all_regions_forecasts.json"):
        update_all_regions_forecast_data()
    else:
        print("All Region forecast data exists... Using existing cache.")

    current_time = datetime.datetime.now(
        tz=datetime.timezone.utc).replace(tzinfo=None)
    return_dict = {}
    for region_name in NAME_TO_DISPLAY.keys():  # keys are all the AZ region names.
        avg_moer_value = get_avg_moer(
            region_name=region_name, starting_time=current_time, deltaminutes=window_size)
        if not avg_moer_value:
            #print(f"No forecast data available for the region: {region_name}")
            continue
        if avg_moer_value == -1:
            print("Current time not found within the forecasted data... check the forecast JSON file under local_files")
            continue
        return_dict[region_name] = {
            'data_center_name': region_name,
            'current_starttime': current_time.isoformat(),
            'window_size_minutes': window_size,
            'average_moer_value': avg_moer_value
        }
    return return_dict


@scheduler.task('cron', id="Old Amulet endpoint file.", month="*", day="*", hour="*", minute="*/15", misfire_grace_time=30)
def update_data_table():
    mappy = get_mappy()
    HISTORY_LIMIT = 3
    data_for_table = mappy[['Azure Region', 'MOER Value']].to_dict()
    # If this directory doesn't exist, the json file containing the history doesn't as well.
    if not os.path.isdir("./local_files"):
        os.mkdir("./local_files")
        data = [data_for_table]
    else:  # Directory + cached file exists
        data = json.load(open("./local_files/data_for_table.json",))
        if len(data) >= HISTORY_LIMIT:  # only hold up to HISTORY_LIMIT number of previous calls
            # Will only keep 1 less than the limit, then add the latest entry.
            data = data[-(HISTORY_LIMIT - 1):]
        data.append(data_for_table)
    with open("./local_files/data_for_table.json", "w") as cachedfile:
        json.dump(data, cachedfile)


"""
Will fire off every 15th minute. E.g. 3:00, 3:15, 3:30, 3:45, 4:00, and on. 
"""


# If it doesn't fire off within 30 seconds, it'll redo it.
@scheduler.task('cron', id="Updates forecast data for all AZ Regions", month="*", day="*", hour="*", minute="*/15", misfire_grace_time=30)
def update_all_regions_forecast_data():
    print("AMULET ENDPOINT: Updating All Regions Forecast Data")
    all_regions_forecasts = {}
    pattern = r'(\d{4}-\d{1,2}-\d{1,2}).*(\d{2}:\d{2}:\d{2})'
    for az_coords, ba in zip(az_coords_WT_joined[0], az_coords_WT_joined[1]):
        ba = json.loads(ba)
        # Using an iterator is much faster than converting the keys to a list, indexing, then comparing. Can compare directly.
        if next(iter(ba.keys())) == 'error':
            continue
        region_name = az_coords['name']  # Used as keys
        display_name = az_coords['displayName']
        #print(region_name, display_name)
        region_data = get_region_forcast(ba['abbrev'])
        try:
            forecast_data = region_data['forecast']
        except KeyError:
            continue
        """
        Any region that isn't a primary key within the JSON file means there is no forecast data for it. 
        """
        # if not forecast_data: # Empty list == no available data
        #    continue
        all_regions_forecasts[region_name] = {}
        all_regions_forecasts[region_name]['point_times'], all_regions_forecasts[region_name]['values'] = [
        ], []
        all_regions_forecasts[region_name]['ba'] = f"{ba['name']}, {ba['abbrev']}"
        all_regions_forecasts[region_name]['displayName'] = display_name
        for data in forecast_data:
            match = re.search(pattern, data['point_time'])
            year, month, day = [int(ymd) for ymd in match.group(
                1).split("-")]  # ymd = year month date
            hour, minute, second = [int(hms)
                                    for hms in match.group(2).split(":")]
            # Need to save in isoformat. Incompatible with json otherwise
            all_regions_forecasts[region_name]['point_times'].append(
                datetime.datetime(year, month, day, hour, minute, second).isoformat())
            all_regions_forecasts[region_name]['values'].append(data['value'])
    all_regions_forecasts_json = json.dumps(all_regions_forecasts)
    if not os.path.isdir("./local_files"):
        os.mkdir("./local_files")
    with open("./local_files/all_regions_forecasts.json", "w") as all_regions_forecasts:
        json.dump(all_regions_forecasts_json, all_regions_forecasts, indent=4)
    return all_regions_forecasts_json


def name_to_dname(region_name):
    print(az_coords)
    #region_name = next(filter(lambda x: x.get(Key).upper() == region_name.upper(), az_coords), None)['name']

    return region_name


def dname_to_name(display_name):
    pass


"""
For converting between displayname and region name. Believe it'll be a lot cleaner once we refactor.
Upon deploying the endpoint, we can have a function go through and generate all files that are needed.
This could be...
1. The initial forecasts file
2. These name to display name and vice versa files
3. etc. etc.
"""


def load_region_displayname_dict():
    name_to_display, display_to_name = {}, {}
    if not os.path.isfile("./static/name_to_display.json") and not os.path.isfile("./static/display_to_name.json"):
        for region_dict in az_coords:
            name, displayName = region_dict['name'], region_dict['displayName']
            name_to_display[name] = displayName
            display_to_name[displayName] = name
    with open("./static/name_to_display.json", "w") as ntd:
        json.dump(name_to_display, ntd, indent=4)
    with open("./static/display_to_name.json", "w") as dtn:
        json.dump(display_to_name, dtn, indent=4)


if __name__ == '__main__':
    # load_region_displayname_dict()
    app.run(debug=True)
