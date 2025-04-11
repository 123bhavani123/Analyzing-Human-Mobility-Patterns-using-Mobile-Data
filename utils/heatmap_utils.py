import folium
from folium.plugins import HeatMap
import pandas as pd

def generate_heatmap(df, lat_col='latitude', lon_col='longitude', output_file='heatmap.html'):
    # Filter out invalid values
    df = df[[lat_col, lon_col]].dropna()

    # Center map on the mean location
    map_center = [df[lat_col].mean(), df[lon_col].mean()]
    base_map = folium.Map(location=map_center, zoom_start=12)

    heat_data = [[row[lat_col], row[lon_col]] for index, row in df.iterrows()]
    HeatMap(heat_data).add_to(base_map)

    base_map.save(output_file)
    print(f"Heatmap saved to {output_file}")
