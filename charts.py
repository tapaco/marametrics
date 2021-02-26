import numpy as np
import pandas as pd

import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn import preprocessing

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.offline as pyo
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from functions import pace, pace_plot, pace_to_dt, power, vo2_max, WEIGHT

def radar_chart(runs):
    """
    Plots a radar chart for the last three runs - rating each run out of five for 
    HR, Speed, Distance, Elevation and VO2 max
    """
    radar_data = runs.copy()
    radar_data = radar_data[:50]
    radar_data['vo2_max'] = radar_data.apply(vo2_max, axis=1)
    radar_data.set_index('name', inplace=True)
    radar_data = radar_data.drop(['upload_id', 'max_speed', 'average_cadence', 
                                'max_heartrate', 'start_date_local', 'start_time', 'pace_in_sec', 'moving_time'], axis=1)

    x = radar_data.values
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)

    normalized = pd.DataFrame(x_scaled, columns=['distance', 'average_speed', 'total_elevation_gain',
        'average_heartrate', 'vo2_max'])
    normalized.set_index(radar_data.index, inplace=True)
    normalized = normalized.apply(lambda x: x*5, axis=1)
    normalized = normalized[
        ['average_heartrate', 'average_speed', 'distance', 'total_elevation_gain', 'vo2_max']
        ]

    categories = ['HR', 'Speed', 'Distance', 'Elevation', 'VO2 max']
    categories = [*categories, categories[0]]

    run_1 = normalized.iloc[0]
    run_2 = normalized.iloc[1]
    run_3 = normalized.iloc[2]
    run_1 = [*run_1, run_1[0]]
    run_2 = [*run_2, run_2[0]]
    run_3 = [*run_3, run_3[0]]
    run_1_title = normalized.index[0]
    run_2_title = normalized.index[1]
    run_3_title = normalized.index[2]

    fig = go.Figure(
        data=[
            go.Scatterpolar(r=run_1, theta=categories, fill='toself', name=f'{run_1_title}'),
            go.Scatterpolar(r=run_2, theta=categories, fill='toself', name=f'{run_2_title}'),
            go.Scatterpolar(r=run_3, theta=categories, fill='toself', name=f'{run_3_title}')
        ],
        layout=go.Layout(
            title=go.layout.Title(text='Last 3 runs'),
            polar={'radialaxis': {'visible': True}},
            showlegend=True
        )
    )

    fig.update_layout(
        template='plotly_white'
    )

    return fig

def time_series(runs):
    """
    plots a time series to compare pace and heart rate values over time, 
    with an adjustable range for the last month, last six months, year-to-date and all time
    """
    ts = runs.copy()
    ts['pace_not_dt'] = ts['pace_in_sec'].apply(pace_plot)
    ts['pace'] = ts['pace_not_dt'].apply(pace_to_dt)
    ts.columns = ['Name', 'Upload ID', 'Distance', 'Moving Time', 'Avg speed', 'Max speed', 'Avg cadence', 'Total elevation gain', 'Avg HR', 'Max HR', 'Date', 'Start time', 'Pace in sec', 'Pace not dt', 'Pace']

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=ts['Date'], y=ts['Avg HR'], name="Avg HR"),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(x=ts['Date'], y=ts['Max HR'], name="Max HR"),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(x=ts['Date'], y=ts['Pace'], name="Pace"),
        secondary_y=False,
    )

    fig.update_xaxes(
        title_text="Date",
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    fig.update_yaxes(title_text="Heart Rate", secondary_y=True)
    fig.update_yaxes(title_text="Pace", secondary_y=False, autorange='reversed')

    fig.update_layout(
        title_text="Pace vs Heart rate trends",
        template='plotly_white',
        yaxis=dict(
            title='Pace',
            tickformat='%M:%S'
        )
    )

    return fig

def clustering(runs, start_date, end_date, slider_input):
    """
    performs k-means clustering given user inputs and returns the dataset which can be sorted by bucket
    """
    display = runs.copy()
    display['pace_not_dt'] = display['pace_in_sec'].apply(pace_plot)
    display['vo2_max'] = display.apply(vo2_max, axis=1)
    display['power'] = display.apply(power, axis=1)
    display = display.set_index('start_date_local')
    display['date'] = display.index
    display = display.loc[end_date : start_date]

    unscaled = display.drop(['name', 'upload_id', 'start_time', 'start_time', 'pace_in_sec', 'pace_not_dt', 'vo2_max', 'date', 'power'], axis = 1)

    X = StandardScaler().fit_transform(unscaled)
    scaled_runs = pd.DataFrame(X, columns=['distance', 'moving_time', 'average_speed', 'max_speed', 'average_cadence', 'total_elevation_gain', 'average_heartrate', 'max_heartrate'])

    model = KMeans(n_clusters=slider_input)
    model.fit(X)
    scaled_runs['cluster'] = model.labels_
    scaled_runs['cluster'].value_counts()

    clustered = display.copy()
    clustered = clustered.reset_index(drop=True)
    clustered['cluster'] = scaled_runs['cluster']

    cluster_counts = pd.DataFrame(clustered['cluster'].value_counts())
    cluster_counts.columns = ['Frequency']

    clustered = clustered.drop(['upload_id', 'moving_time', 'average_speed', 
                                'max_speed', 'average_cadence', 'average_heartrate',
                                'max_heartrate', 'start_time', 'pace_in_sec'], axis=1)
    clustered['distance'] = clustered['distance'].apply(lambda x: round(x))
    clustered = clustered.set_index('date')
    clustered.columns = ['Name', 'Distance', 'Elevation', 'Pace', 'VO2 max', 'Power', 'Cluster']

    return [cluster_counts, clustered]