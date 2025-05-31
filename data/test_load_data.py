import pandas as pd
import os

# Load fog/weather station data, ensuring times are datetime64[ns] dtype
combined_data_df = pd.read_csv('combined_data_china_winter2024.csv', low_memory=False)

print(combined_data_df) #112799 x 15
print(combined_data_df.columns) #['time', 'station', 'latitude', 'longitude', 'name', 'coco', 'u10', 'v10', 'd2m', 't2m', 'sp', 'lcc', 'tcc', 'swvl1', 'blh']
