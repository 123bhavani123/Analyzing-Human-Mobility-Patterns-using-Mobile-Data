# xgboost_model.py
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def preprocess_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df.dropna(inplace=True)
    return df

def train_xgb_model(df):
    df = preprocess_data(df)

    le = LabelEncoder()
    df['cluster'] = le.fit_transform(df['cluster'])

    features = ['latitude', 'longitude', 'hour', 'dayofweek', 'month']
    X = df[features]
    y = df['cluster']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
    xgb_model.fit(X_train, y_train)

    return xgb_model, le, features

def predict_future_clusters(model, df, features):
    df = preprocess_data(df)
    future_data = df[features]
    if future_data.empty:
        return pd.DataFrame()
    preds = model.predict(future_data)
    df['predicted_cluster'] = preds
    return df
