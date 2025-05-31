"""
This script downloads archive data from the Climate Data Store (CDS) of
the European Centre for Medium-Range Weather Forecasts (ECMWF).
The dataset used is "ERA5 hourly data on single levels from 1940 to present".
This data is governed by the Creative Commons Attribution 4.0 International (CC BY 4.0).
https://creativecommons.org/licenses/by/4.0/

The variables requested from the dataset through this script may presumably be used to predict fog.
The data spans all hours during the months of January, February, and December 2024, mostly across China.
NOTE THAT THIS REQUEST HAS GENERATED A 3.75-4.03GB FILE IN 22:27 MINUTES.
Seth Orvin
"""

import cdsapi   # API to access CDS databases
import os

# Set up destination for downloaded data file
data_filename = 'era5_china_winter2024.nc'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(project_root, 'data', data_filename)

# Create API client and request data from server
c = cdsapi.Client()
c.retrieve(
    # Dataset name
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        # Weather observations
        'variable': [   #
            '10m_u_component_of_wind',
            '10m_v_component_of_wind',
            '2m_dewpoint_temperature',
            '2m_temperature',
            'surface_pressure',
            'low_cloud_cover',
            'total_cloud_cover',
            'volumetric_soil_water_layer_1',
            'boundary_layer_height',
        ],
        # Time: Winter months of 2024 (limited time due to file size constraints)
        'year': ['2024'],
        'month': ['01', '02', '12'],
        'day': [
            '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31',
        ],
        'time': [
            '0:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00', '21:00', '22:00', '23:00',
        ],
        'area': [54, -72, 18, 135], # Coordinates enclosing China
        'format': 'netcdf',
    },
    data_path)