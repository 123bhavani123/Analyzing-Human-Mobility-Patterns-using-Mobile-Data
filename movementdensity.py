from folium.plugins import HeatMap

def generate_heatmap(df):
    heat_df = df[['latitude', 'longitude']].dropna()
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12)
    HeatMap(data=heat_df.values.tolist()).add_to(m)
    m.save('output/heatmaps/movement_heatmap.html')
