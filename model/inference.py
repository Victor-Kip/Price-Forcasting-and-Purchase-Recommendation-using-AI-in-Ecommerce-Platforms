
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

def get_prediction(prices_list, description="Unknown Product"):
    if not model or not scaler:
        return None, "Model artifacts not loaded."
        
    try:
        if not prices_list or len(prices_list) != TIME_STEP:
            return None, f'Incorrect price data length for "{description}".'
            
        arr = np.array(prices_list, dtype=float).reshape(-1, 1)
        scaled = scaler.transform(arr)
        pred = model.predict(scaled.reshape(1, TIME_STEP, 1), verbose=0)
        final = pred.reshape(-1, 1)
        prediction = [round(float(val), 2) for val in final.flatten()]
        return prediction, None
    except Exception as e:
        logging.error(f"Prediction error for {description}: {e}")
        return None, "Prediction failed."