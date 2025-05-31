"""
This script downloads archive data through Meteostat.
Meteostat sources its weather and climate data from a variety of interfaces and organizations:
https://dev.meteostat.net/sources.html

This script downloads information on weather stations in China, such as their coordinates and recorded
climate conditions code (which may indicate fogginess).
The data spans all hours during the months of January, February, and December 2024 in China.
Seth Orvin
"""

from meteostat import Stations, Hourly
from datetime import datetime
import pandas as pd
import os

# Set up destination for downloaded data file
data_filename = 'fog_china_winter2024.csv'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(project_root, 'data', data_filename)

# Data ranges to align with ERA5 data -> Jan,Feb,Dec from 2024
start = datetime(2024, 1, 1)
end = datetime(2024, 12, 31)
valid_months = [1, 2, 12]

# Create DataFrame of weather stations in China that report hourly data
stations_df = Stations().region('CN').inventory('hourly').fetch()

# Prepare a list to store DataFrames, each containing hourly data from one station
stations_data = []

# Compile data from each weather station
for station_id, station in stations_df.iterrows():
    try:
        # Collect hourly weather observations for each station using a DataFrame
        data_df = Hourly(station_id, start, end).fetch()

        # Define criteria of a dataframe with useful data (i.e., has  at least one row with a fog-related coco value)
        #has_fog_coco = 'coco' in data_df.columns and data_df['coco'].isin([5, 6]).any()   # https://dev.meteostat.net/formats.html#weather-condition-codes

        # Limit rows to those within timeframe of Jan, Feb, Dec 2024 (to match ERA5 data)
        data_df = data_df[(data_df.index.month.isin(valid_months))]

        # Keep only the 'coco' column (variable corresponding to a code for weather conditions, including fog) # https://dev.meteostat.net/formats.html#weather-condition-codes
        # Note that relevant data is provided here that may be useful for predicting fog, but want to practice merging w/ ERA5 data
        if 'coco' in data_df.columns:
            data_df = data_df[['coco']]
        # Skip station if 'coco' column is missing
        else:
            continue

        # Reset the datetime index to a column, dtype = datetime64[ns]
        data_df = data_df.reset_index()

        # Add metadata about station to dataframe
        data_df = data_df.assign(
            station = station_id,
            latitude=station['latitude'],
            longitude=station['longitude'],
            name=station['name']
        )

        # Append to the list of data for all weather stations
        stations_data.append(data_df)

    except Exception as e:
        print(e)

# Turn list of data from all weather stations (list of DataFrames) into a combined DataFrame
if stations_data:
    stations_data_df = pd.concat(stations_data, ignore_index=True)
    stations_data_df.to_csv(data_path, index=False)
    print("Data saved to:", data_path)
else:
    print("List stations_data empty. No data was saved.")
