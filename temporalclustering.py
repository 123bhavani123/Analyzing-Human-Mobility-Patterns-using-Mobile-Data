from sklearn.cluster import DBSCAN
import numpy as np

def dbscan_temporal_clustering(df, eps_km=0.5, min_samples=3):
    coords = df[['latitude', 'longitude']].to_numpy()
    db = DBSCAN(eps=eps_km / 6371.0, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
    radians = np.radians(coords)
    df['cluster'] = db.fit_predict(radians)
    return df
