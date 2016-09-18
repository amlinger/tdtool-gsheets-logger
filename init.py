# This script syncs sensor readings from a connected  Tellstickk or similar
# Telldus device to a selected Google Spreadsheet.
#
# This requires tdtool to be installed.
#
# The necessary Python dependencies are oauth2client and gspread, which
# could be found in requirements.txt

import subprocess, gspread, time, os
from oauth2client.service_account import ServiceAccountCredentials

# Dictionary of supported metrics, thats saved to the Google Spreadsheet.
# Keys are the supported metrics, values is a list of values to save to the
# tab in the tab in the Spreadsheet.
metrics = {
    'temperature': ['id', 'time', 'temperature'],
    'humidity':    ['id', 'time', 'humidity'],
}

SCRIPT_PATH=os.path.dirname(__file__)
CRED_PATH=os.path.join(SCRIPT_PATH, 'credentials.json')

ENV_SHEET_KEY='GOOGLE_SPREADSHEET_KEY'
POLLING_INTERVAL=20

# Sets up the initial credentials, using the credentials file in the
# folder. This reads the file, and sets up and returns a spreadsheet that has
# been authorized.
def setup_credentials():
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CRED_PATH, scope)
    return gspread.authorize(credentials)

# Fetches the ssensors using tdtool
def get_sensors():
    sensor_string = subprocess.Popen(
        "tdtool --list-sensors",
        shell=True,
        stdout=subprocess.PIPE
    ).stdout.read()

    return [
        dict(
            [pair.split('=') for pair in line.split('\t')]
        ) for line in sensor_string.split('/n')]

# Fetches a worksheet from the Spreadsheet. This can be done in one of three
# ways:
#
# 1. The worksheet is cached, so it is fetched from there.
# 2. The worksheet has not been cached, so its fetched from the spreadsheet
#    and saved to the cache. Headers are being reset again.
# 3 The worksheet does not exist, so it's created and added to the cache.
#
# If the name of the worksheet does not match the listed metrics a
# ValueError is thrown. Add more to metrics to be able to track these as well.
worksheet_cache = {}
def get_worksheet(spreadsheet, name):
    if name not in metrics:
        raise ValueError("\"{}\" is not a valid metric (use [{}])".format(
            name, ", ".join(metrics.keys())))

    headers = metrics[name]

    if name in worksheet_cache:
        return worksheet_cache[name]

    try:
        sheet = spreadsheet.worksheet(name)
    except gspread.exceptions.WorksheetNotFound as e:
        sheet = spreadsheet.add_worksheet(
                title=name, rows=1 ,cols=len(headers))

    for idx, header in enumerate(headers):
        sheet.update_cell(1, idx + 1, header)

    worksheet_cache[name] = sheet
    return sheet

# Logs a sensor information about given metric to the given spreadsheet.
# This assumes that a sensor has a time field, which must be greater tha
# the existing cached last timestamp to be inserted. Values are inserted in
# the top of the worksheet, below the header row. This is done since it
# simplifies using values with charts (which won't update it's range if
# rows instead are appended to the worksheet).
last_timestamps = {}
def log_sensor_and_metric(sensor, metric, spreadsheet):
    if metric in last_timestamps and last_timestamps[metric] == sensor["time"]:
        return

    last_timestamps[metric] = sensor["time"]
    get_worksheet(spreadsheet, metric).insert_row(
            [sensor[key] for key in metrics[metric]], index=2)

gc = setup_credentials()
spreadsheet = gc.open_by_key(os.environ[ENV_SHEET_KEY])

# Forever running main loop.
while True:
    for sensor in get_sensors():
        for metric in metrics:
            log_sensor_and_metric(sensor, metric, spreadsheet)
    time.sleep(POLLING_INTERVAL)

