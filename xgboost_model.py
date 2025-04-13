# xgboost_model.py

import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

# Paths to save model and encoder
MODEL_PATH = "xgb_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

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

    # Save model and encoder
    joblib.dump(xgb_model, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)

    return xgb_model, le, features

def load_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        model = joblib.load(MODEL_PATH)
        le = joblib.load(ENCODER_PATH)
        features = ['latitude', 'longitude', 'hour', 'dayofweek', 'month']
        return model, le, features
    else:
        return None, None, None

def predict_future_clusters(model, df, features):
    df = preprocess_data(df)
    if df.empty or model is None:
        return pd.DataFrame()
    preds = model.predict(df[features])
    df['predicted_cluster'] = preds
    return df
