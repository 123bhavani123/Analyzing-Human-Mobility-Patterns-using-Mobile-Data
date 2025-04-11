# epidemic_analysis.py
import pandas as pd
from geopy.distance import geodesic

# Load and process mobility data to flag high-density transitions (used for epidemic alerts)
def detect_epidemic_risk_zones(df, cluster_col='cluster'):
    zone_counts = df[cluster_col].value_counts()
    risk_zones = zone_counts[zone_counts > zone_counts.mean() + zone_counts.std()].index.tolist()
    df['epidemic_risk_zone'] = df[cluster_col].apply(lambda x: 'High Risk' if x in risk_zones else 'Low Risk')
    return df

# public_transport_optimization.py
def suggest_transport_boosts(df, cluster_col='cluster'):
    rush_hours = df['hour'].between(7, 9) | df['hour'].between(17, 19)
    high_traffic_zones = df[rush_hours][cluster_col].value_counts().nlargest(5).index.tolist()
    suggestions = {zone: "Increase transport availability" for zone in high_traffic_zones}
    return suggestions

# urban_planning_analysis.py
def identify_urban_clusters(df, cluster_col='cluster'):
    cluster_stats = df.groupby(cluster_col).agg({
        'latitude': ['mean'],
        'longitude': ['mean'],
        'timestamp': ['count']
    })
    cluster_stats.columns = ['lat_mean', 'lon_mean', 'visit_count']
    cluster_stats['urban_zone'] = cluster_stats['visit_count'].apply(lambda x: 'Urban' if x > 50 else 'Rural')
    return cluster_stats.reset_index()

# tourism_location_prediction.py
def get_tourist_hotspots(df, cluster_col='cluster'):
    weekend_data = df[df['dayofweek'].isin([5, 6])]  # Saturday and Sunday
    hotspot_clusters = weekend_data[cluster_col].value_counts().nlargest(5).index.tolist()
    df['tourism_hotspot'] = df[cluster_col].apply(lambda x: 'Yes' if x in hotspot_clusters else 'No')
    return df

# health_monitoring.py
def track_epidemiological_mobility(df, infected_clusters):
    df['contact_with_infected'] = df['cluster'].apply(lambda x: 'Yes' if x in infected_clusters else 'No')
    return df
