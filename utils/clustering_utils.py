import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from collections import Counter, defaultdict

def apply_dbscan(df, eps_km=0.2, min_samples=10, lat_col='latitude', lon_col='longitude'):
    coords = df[[lat_col, lon_col]].dropna().to_numpy()
    kms_per_radian = 6371.0088
    epsilon = eps_km / kms_per_radian

    db = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
    cluster_labels = db.fit_predict(np.radians(coords))

    df['cluster'] = -1
    df.loc[~df[[lat_col, lon_col]].isnull().any(axis=1), 'cluster'] = cluster_labels
    return df

