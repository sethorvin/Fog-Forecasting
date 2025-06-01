"""
This script assumes that download_era5_data.py has generated era5_china_winter2024.nc
This script assumes that download_fog_data.py has generated fog_china_winter2024.nc

This script combines the data from the aforementioned files such that features from ERA5 may be merged with
a ground truth label for fog from Meteostat.

Seth Orvin
"""

import xarray as xr #version 2023.1.0, with package h5netcdf version 1.1.0
import pandas as pd
from scipy.spatial import cKDTree
import numpy as np
import os
import sys

# Get the path to the data directory, relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..', 'data')

# Define file paths
era5_path = os.path.join(data_dir, 'era5_china_winter2024.nc')
fog_path = os.path.join(data_dir, 'fog_china_winter2024.csv')

# Load ERA5 dataset if the file exists
if os.path.exists(era5_path):
    try:
        era5 = xr.open_dataset(era5_path, engine="h5netcdf")
    except Exception as e:
        print('Error loading ERA5 NetCDF file: {e}')
        sys.exit(1)
else:
    print(f'ERA5 file not found at {era5_path}')
    sys.exit(1)

#Flatten ERA5 grid
lats = era5.latitude.values
lons = era5.longitude.values
long_grid, lat_grid = np.meshgrid(lons, lats)

# Build a KD-tree of points to allow fast nearest-neighbor searches
points = np.vstack([lat_grid.ravel(), long_grid.ravel()]).T
tree = cKDTree(points)

# Load fog/weather station data, if it exists
if os.path.exists(fog_path):
    try:
        stations_data_df = pd.read_csv(fog_path, low_memory=False)
        # Ensures times are datetime64[ns] dtype
        stations_data_df['time'] = pd.to_datetime(stations_data_df['time'])
    except Exception as e:
        print('Error loading or parsing fog CSV file: {e}')
        sys.exit(1)
else:
    print(f"Fog data CSV not found at {fog_path}")
    sys.exit(1)

# Extract station coordinates for nearest grid point matching
station_coords = stations_data_df[['latitude', 'longitude']].values

# Find nearest ERA5 grid point index for each station observation
_, indices = tree.query(station_coords)
indices_lat, indices_lon = np.unravel_index(indices, (len(lats), len(lons)))

# Get ERA5 time value as numpy datetime64 for fast indexing
era5_times = era5.valid_time.values

# Prepare a list to collect merged rows
merged_rows = []

for i, row in stations_data_df.iterrows():
    # Find closest time index in ERA5 for the station's time
    #time_idx = np.argmin(np.abs(era5_times - np.datetime64(row['time'])))
    time_idx = np.where(era5_times == np.datetime64(row['time']))[0]
    if len(time_idx) == 0:
        continue # skip if no exact match
    time_idx = time_idx[0]

    # Get lat/lon indices for this station
    lat_idx = indices_lat[i]
    lon_idx = indices_lon[i]

    # Extract ERA5 variables at this spatial-temporal point
    era5_point = {var: era5[var].values[time_idx, lat_idx, lon_idx] for var in era5.data_vars}

    # Combine ERA5 data with fog station data
    combined_dict = {
        'time': row['time'],
        'station': row['station'],
        'latitude': row['latitude'],
        'longitude': row['longitude'],
        'name': row['name'],
        'coco': row['coco']
    }
    combined_dict.update(era5_point)

    merged_rows.append(combined_dict)

# Create combined DataFrame
combined_df = pd.DataFrame(merged_rows)

# Save combined data to CSV
combined_data_path = os.path.join(data_dir, 'combined_data_china_winter2024.csv')
combined_df.to_csv(combined_data_path, index=False)
print("Combined data saved to:", combined_data_path)