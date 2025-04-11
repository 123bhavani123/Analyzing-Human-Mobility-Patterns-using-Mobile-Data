import pandas as pd
import generate_heatmap

df = pd.read_csv('synthetic_mobile_data.csv')
generate_heatmap(df, lat_col='latitude', lon_col='longitude')

