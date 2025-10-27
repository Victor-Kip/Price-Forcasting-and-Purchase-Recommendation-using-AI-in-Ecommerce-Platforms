
import joblib
import tensorflow as tf
import numpy as np
import os
import logging


TIME_STEP = 12

# Use relative paths based on this file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'lstm_model.keras')
scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')

model = None
scaler = None


def load_artifacts():
    global model, scaler
    try:
        # load LSTM model
           model = tf.keras.models.load_model(model_path)
           print("Successfully loaded LSTM model")
        # load scaler
           scaler = joblib.load(scaler_path)
           print("Successfully loaded scaler")
    except Exception as e:
           print(f"Error loading artifacts: {e}")

# Load model and scaler at import
load_artifacts()