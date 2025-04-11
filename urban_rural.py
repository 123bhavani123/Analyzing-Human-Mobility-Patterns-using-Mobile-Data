import pandas as pd
import geopandas as gpd

def classify_urban_rural(df, urban_shapefile = "urban_areas.shp"):

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
    urban_areas = gpd.read_file("urban_areas.geojson")

    
    df['is_urban'] = gdf.geometry.within(urban_areas.unary_union)
    urban_stats = df[df['is_urban']].groupby('user_id').size()
    rural_stats = df[~df['is_urban']].groupby('user_id').size()

    return pd.DataFrame({'urban_visits': urban_stats, 'rural_visits': rural_stats}).fillna(0)