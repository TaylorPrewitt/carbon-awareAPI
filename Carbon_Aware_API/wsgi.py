"""
File declaration for web server. This will act as the "main.py" / "app.py"
"""

from app import create_flask_app
from app.routes.static import static_bp
from app.routes.ci_data import ci_bp
from app.routes.shift import shift_bp
from app.utils import *
import datetime
from flask_apscheduler import APScheduler

app = create_flask_app()
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

################################################
#           CRON SCHEDULED JOBS
################################################

"""
Will fire off every 15th minute. E.g. 3:00, 3:15, 3:30, 3:45, 4:00, and on. 
"""
@scheduler.task('cron', id="Updates forecast data for all AZ Regions", month="*", day="*", hour="*", minute="*/15", misfire_grace_time=30) # If it doesn't fire off within 30 seconds, it'll redo it. 
def update_all_regions_forecast_data():
    print("AMULET ENDPOINT: Updating All Regions Forecast Data")
    all_regions_forecasts = {}
    pattern = r'(\d{4}-\d{1,2}-\d{1,2}).*(\d{2}:\d{2}:\d{2})'
    for az_coords, ba in zip(az_coords_WT_joined[0], az_coords_WT_joined[1]):
        ba = json.loads(ba)
        if next(iter(ba.keys())) == 'error': # Using an iterator is much faster than converting the keys to a list, indexing, then comparing. Can compare directly. 
            continue
        region_name = az_coords['name'] # Used as keys
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
        #if not forecast_data: # Empty list == no available data
        #    continue
        all_regions_forecasts[region_name] = {}
        all_regions_forecasts[region_name]['point_times'], all_regions_forecasts[region_name]['values'] = [], []
        all_regions_forecasts[region_name]['ba'] = f"{ba['name']}, {ba['abbrev']}"
        all_regions_forecasts[region_name]['displayName'] = display_name
        for data in forecast_data:
            match = re.search(pattern, data['point_time'])
            year, month, day = [int(ymd) for ymd in match.group(1).split("-")] #ymd = year month date
            hour, minute, second = [int(hms) for hms in match.group(2).split(":")]
            # Need to save in isoformat. Incompatible with json otherwise
            all_regions_forecasts[region_name]['point_times'].append(datetime.datetime(year, month, day, hour, minute, second).isoformat()) 
            all_regions_forecasts[region_name]['values'].append(data['value'])
    all_regions_forecasts_json = json.dumps(all_regions_forecasts)
    if not os.path.isdir("./local_files"):
        os.mkdir("./local_files")
    with open("./local_files/all_regions_forecasts.json", "w") as all_regions_forecasts:
        json.dump(all_regions_forecasts_json, all_regions_forecasts, indent=4)
    return all_regions_forecasts_json

if __name__ == '__main__':
    update_all_regions_forecast_data()
    app.register_blueprint(static_bp)
    app.register_blueprint(ci_bp)
    app.register_blueprint(shift_bp)
    app.run(debug=True)