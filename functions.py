import requests
import json
import urllib3
import base64

import numpy as np
import pandas as pd
from pandas.io.json import json_normalize

from pathlib import Path
from datetime import datetime
import streamlit as st

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WEIGHT = 82

@st.cache
def load_data():
    """
    Obtain running data from the Strava API and perform some basic cleaning
    """
    # Get access tokens
    auth_url = 'https://www.strava.com/oauth/token'
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'
    payload = {
        'client_id': '61192',
        'client_secret': '2c4d071cbe331679dba8dd98ca5737807c649bd5',
        'refresh_token': '064486d45898df2990c369aa127472fce092912e',
        'grant_type': 'refresh_token',
        'f': 'json'
    }
    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()['access_token']
    header = {'Authorization': 'Bearer ' + f'{access_token}'}

    # get first half
    param = {'per_page': 200, 'page': 1}
    dataset_1 = requests.get(activities_url, headers=header, params=param).json()
    activities_1 = pd.json_normalize(dataset_1)

    # fetch second half
    param2 = {'per_page': 200, 'page': 2}
    dataset_2 = requests.get(activities_url, headers=header, params=param2).json()
    activities_2 = pd.json_normalize(dataset_2)

    # combine both halves and select required columns
    activities = pd.concat([activities_1, activities_2])
    cols = ['name', 'upload_id', 'type', 'distance', 'moving_time',   
            'average_speed', 'max_speed', 'average_cadence',
            'total_elevation_gain','average_heartrate', 'max_heartrate', 
            'start_date_local',
       ]
    activities = activities[cols]

    # separate date and time and filter only runs, removing NaN too
    activities['start_date_local'] = pd.to_datetime(activities['start_date_local'])
    activities['start_time'] = activities['start_date_local'].dt.time
    activities['start_date_local'] = activities['start_date_local'].dt.date
    runs = activities.loc[activities['type'] == 'Run']
    runs = runs.drop(['type'], axis = 1)
    runs = runs.dropna()

    # obtain pace for each run
    runs['pace_in_sec'] = runs.apply(pace, axis=1)

    return runs

def summary_stats(df):
    """
    return summary statistics for the respective dataframe
    """
    s_stats = df.copy()
    s_stats = s_stats.drop(['upload_id'], axis=1)
    return s_stats.describe(include = ['float', 'int'])

def pace(row):
    """
    converts speed in m/s to pace in s/km
    """
    pace = 1000 / row['average_speed']
    return pace

def pace_plot(x):
    """
    plots pace in seconds as pace in min:sec on charts
    """
    m = int(x / 60)
    s = int(x - (60 * m))
    return '%(m)01d:%(s)02d' % {'m': m, 's': s}

def pace_to_dt(x):
    """
    plots pace in min:sec for plotly
    """
    return datetime.strptime(x, '%M:%S')

def power(row):
    ecor = 1.04 # energy cost of running given air resistance
    power = row['average_speed'] * ecor * WEIGHT
    return round(power)

def vo2_max(row):
    """
    calculates vo2max based on the formula by The Secret of Running
    """
    velocity = (row['distance'] / 1000) / (row['moving_time'] / 3600) # km / hour
    vo2max = 3.77 * velocity
    return round(vo2max)

def filedownload(df):
    """
    download clustered data as csv
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="runs.csv">Download output as CSV</a>'
    return href

@st.cache
def read_markdown_file(markdown_file):
    """
    create intro text from markdown file
    """
    return Path(markdown_file).read_text()
