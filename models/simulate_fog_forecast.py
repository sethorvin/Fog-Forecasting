import joblib
import pandas as pd
import sys
import os

# Load the Random Forest estimator
model = joblib.load('best_random_forest_model.pkl')

# Retrieve data
# NOTE: Ideally, would use an API for live data. Did not find a convenient one from same source as EPA5.
# So, using already processed data -- the last 20% of which, which is not involved in model training/testing

# Get the path to the data directory, relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'processed_data_china_winter2024.csv')

# Attempt to load data into a DataFrame, exit otherwise
if os.path.exists(data_path):
    try:
        df = pd.read_csv(data_path, parse_dates=['time'], low_memory=False)
        df.sort_values(by=['station', 'time'], inplace=True)
    except Exception as e:
        print('Error loading processed data file: {e}')
        sys.exit(1)
else:
    print(f'File not found at {data_path}')
    sys.exit(1)

# Create binary fog label (1 if fog, 0 otherwise)
df['is_fog'] = df['coco'].isin([5, 6]).astype(int) # https://dev.meteostat.net/formats.html#weather-condition-codes

# Create target for forecasting: Was there fog 1 hour later? --> Use to test "forecasting"
df['is_fog_in_1h'] = df.groupby('station')['is_fog'].shift(-1)

# Drop rows with missing target
df = df.dropna(subset=['is_fog_in_1h'])
df['is_fog_in_1h'] = df['is_fog_in_1h'].astype(int)

# Only use last 20% of the data (unseen -- not previously used in training or testing model)
split_index = int(len(df) * 0.8)
df = df.iloc[split_index:]

# Select variables that were used as features in training
features = [
    'd2m', 't2m', 'sp', 'lcc', 'tcc', 'swvl1', 'blh',
    'latitude', 'longitude', 'wind_speed', 'relative_humidity'
]

# Select 10 random rows from DataFrame
sample = df.sample(n=10)

# Predict probability of fog in 1 hour, and add probabilities to sample
probs = model.predict_proba(sample[features])[:, 1]
sample['fog_probability_in_1h'] = probs

# Output results. Compare predictions to is_fog_in_1h
sample = sample[['time', 'station', 'fog_probability_in_1h', 'is_fog_in_1h'] + features]
print(sample.to_string(index=False, float_format="%.2f"))
