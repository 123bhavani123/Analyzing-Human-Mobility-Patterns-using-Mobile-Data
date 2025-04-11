import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, TimestampedGeoJson ,MarkerCluster
from streamlit_folium import st_folium
from utils.clustering_utils import apply_dbscan
from mobility_analysis import *
from utils.geospatial_utils import *
from utils.clustering_utils import *
from utils.clustering_utils import apply_dbscan
from utils.heatmap_utils import generate_heatmap
from frequentlocation import detect_frequent_locations
from transitiongraph import build_transition_graph
from urban_rural import classify_urban_rural
from xgboost_model import train_xgb_model, predict_future_clusters
from epidemic_analysis import (
    detect_epidemic_risk_zones,
    suggest_transport_boosts,
    identify_urban_clusters,
    get_tourist_hotspots,
    track_epidemiological_mobility
)
st.set_page_config(layout="wide")
st.title(" Human Mobility Analysis Dashboard")

uploaded_file = st.file_uploader("Upload CSV with latitude, longitude, timestamp", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Column selection
    lat_col = st.selectbox("Select Latitude Column", df.columns)
    lon_col = st.selectbox("Select Longitude Column", df.columns)
    time_col = st.selectbox("Select Timestamp Column", df.columns)

    # Clean and preprocess
    df = df[[lat_col, lon_col, time_col, 'user_id']].dropna()
    df['datetime'] = pd.to_datetime(df[time_col])
    df.sort_values(by=['user_id', 'datetime'], inplace=True)
    df.rename(columns={time_col: 'timestamp'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])


    st.subheader("🗺️ Heatmap")
    center = [df[lat_col].mean(), df[lon_col].mean()]
    base_map = folium.Map(location=center, zoom_start=12)
    heat_data = df[[lat_col, lon_col]].values.tolist()
    HeatMap(heat_data).add_to(base_map)
    st_folium(base_map, width=1000, height=500)

    # Apply clustering
    st.subheader("🧠 Clustering (DBSCAN)")
    eps_km = st.slider("DBSCAN Epsilon (km)", 0.05, 1.0, 0.3, step=0.05)
    min_samples = st.slider("Minimum Samples", 2, 20, 5)


    df = apply_dbscan(df, eps_km, min_samples, lat_col, lon_col)
    cluster_map = folium.Map(location=center, zoom_start=12)

    for _, row in df.iterrows():
        color = 'blue' if row['cluster'] == -1 else 'red'
        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=3,
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(cluster_map)

    st_folium(cluster_map, width=1000, height=500)

    # CSV Download
    st.subheader(" Download Processed Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="processed_mobility_data.csv",
        mime="text/csv"
    )

    # Apply DBSCAN
    df = apply_dbscan(df, eps_km=eps_km, min_samples=min_samples, lat_col=lat_col, lon_col=lon_col)
    # Animation
    st.subheader("🎞️ Animated Movement Playback")

    features = []
    for _, row in df.iterrows():
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row[lon_col], row[lat_col]],
            },
            'properties': {
                'time': row['datetime'].strftime('%Y-%m-%dT%H:%M:%S'),
                'style': {'color': 'blue'},
                'icon': 'circle',
                'iconstyle': {'fillColor': 'blue', 'fillOpacity': 0.6, 'stroke': 'true', 'radius': 4}
            }
        })

    animated_map = folium.Map(location=center, zoom_start=12)
    TimestampedGeoJson({
        'type': 'FeatureCollection',
        'features': features,
    }, period='PT1H', add_last_point=True, auto_play=False, loop=False, max_speed=1).add_to(animated_map)

    st_folium(animated_map, width=1000, height=500)
    df = df.sort_values(['user_id','timestamp'])

    generate_heatmap(df)
    df = apply_dbscan(df)
    frequent = detect_frequent_locations(df)
    st.write("Home/Work Locations:", frequent)
   
    G = build_transition_graph(df)
    st.subheader("📝 Transition Graph")
    G = build_transition_graph(df)
    st.write(f"Graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
    mobility_stats = classify_urban_rural(df)
    st.write(mobility_stats.head())

    # XGBoost Prediction of Future Clusters
    st.subheader("🔮 Predicted Future Clusters (XGBoost)")
    model, le, features = train_xgb_model(df)
    pred_df = predict_future_clusters(model, df, features)

    if not pred_df.empty:
        map_future = folium.Map(location=center, zoom_start=12)
        for _, row in pred_df.iterrows():
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=5,
                color=f'#{hex(100 + row["predicted_cluster"] * 100)[2:]}',
                fill=True,
                fill_opacity=0.6,
                popup=f"Predicted Cluster: {row['predicted_cluster']}"
            ).add_to(map_future)

        st_folium(map_future, width=1000, height=500)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['dayofweek'] = df['timestamp'].dt.dayofweek

# Sidebar Task Selection
        task = st.selectbox(
        "Select Use Case",
        [
        "Epidemic Outbreak Detection",
        "Public Transport Optimization",
        "Urban Planning",
        "Tourism & Location Marketing",
        "Health Tech - Epidemiological Monitoring"
        ]
        )

# Epidemic Detection
        if task == "Epidemic Outbreak Detection":
            alerts = detect_epidemic_risk_zones(df)
            st.subheader("🌧️ Epidemic Alerts")
            st.write(alerts)

# Public Transport Optimization
        elif task == "Public Transport Optimization":
            st.subheader("🚌 Optimized Transport Zones")
            transport_suggestions = suggest_transport_boosts(df)
            for cluster, suggestion in transport_suggestions.items():
                st.markdown(f"**Cluster {cluster}**: {suggestion}")

# Urban Planning
        elif task == "Urban Planning":
            st.subheader("🏙️ Urban Cluster Zones")
            cluster_df = identify_urban_clusters(df)
            st.write(cluster_df)

    # Optional visualization
            map_center = [df['latitude'].mean(), df['longitude'].mean()]
            city_map = folium.Map(location=map_center, zoom_start=12)
            marker_cluster = MarkerCluster().add_to(city_map)
            for _, row in df.iterrows():
                folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup="Urban Activity",
                icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(marker_cluster)
                st_folium(city_map, width=1000, height=500)

# Tourism & Location Marketing
        elif task == "Tourism & Location Marketing":
            updated_df = get_tourist_hotspots(df)
            st.subheader("🎯 Tourist Hotspots")
            st.write(updated_df[['cluster', 'tourism_hotspot']].drop_duplicates())
            map_center = [df['latitude'].mean(), df['longitude'].mean()]
            tour_map = folium.Map(location=map_center, zoom_start=12)
            for _, row in df.iterrows():
                if row['tourism_hotspot'] == 'Yes':
                    folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=6,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.6
                ).add_to(tour_map)
            st_folium(tour_map, width=1000, height=500)

# Health Monitoring
        elif task == "Health Tech - Epidemiological Monitoring":
            infected_clusters = df[df['epidemic_risk_zone'] == 'High Risk']['cluster'].unique().tolist() if 'epidemic_risk_zone' in df.columns else []
            status_df = track_epidemiological_mobility(df, infected_clusters)
            st.subheader("🌡️ Health Monitoring Dashboard")
            st.write(status_df[['cluster', 'contact_with_infected']].drop_duplicates())
        else:
             st.warning("No predicted clusters found.")
else:
    st.warning("No predicted clusters found.")