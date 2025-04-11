import pandas as pd
import folium
import matplotlib.pyplot as plt
from utils.geospatial_utils import haversine_distance
from datetime import datetime

# Load data
df = pd.read_csv('synthetic_mobile_data.csv', parse_dates=['timestamp'])
df.sort_values(by=['user_id', 'timestamp'], inplace=True)

# Calculate mobility metrics per user
def analyze_user_mobility(user_df):
    distances = []  
    times = []

    for i in range(1, len(user_df)):
        lat1, lon1 = user_df.iloc[i-1][['latitude', 'longitude']]
        lat2, lon2 = user_df.iloc[i][['latitude', 'longitude']]
        time_diff = (user_df.iloc[i]['timestamp'] - user_df.iloc[i-1]['timestamp']).seconds / 3600
        dist = haversine_distance(lat1, lon1, lat2, lon2)
        distances.append(dist)
        times.append(time_diff)

    return {
        'total_distance_km': sum(distances),
        'average_speed_kmph': sum(distances)/sum(times) if sum(times) > 0 else 0,
        'num_movements': len(distances)
    }

# Analyze all users
user_stats = df.groupby('user_id').apply(analyze_user_mobility).apply(pd.Series)
print(user_stats)

# Plot path for a sample user
sample_user = 'U1'
user_df = df[df['user_id'] == sample_user]

m = folium.Map(location=[user_df.iloc[0]['latitude'], user_df.iloc[0]['longitude']], zoom_start=12)
for i in range(len(user_df)-1):
    folium.PolyLine(
        [(user_df.iloc[i]['latitude'], user_df.iloc[i]['longitude']),
         (user_df.iloc[i+1]['latitude'], user_df.iloc[i+1]['longitude'])],
        color="blue", weight=2.5, opacity=1
    ).add_to(m)

m.save('C:\\Users\\Bhavani\Desktop\Mobility\output.html')
