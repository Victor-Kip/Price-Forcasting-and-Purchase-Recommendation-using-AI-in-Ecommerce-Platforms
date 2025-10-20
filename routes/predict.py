from flask import Blueprint,request,jsonify
from model.inference import model,scaler,TIME_STEP
import numpy as np
import logging

predict_bp = Blueprint('predict',__name__)

@predict_bp.route('/predict',method = ['POST','GET'])
def predict():
    if not model or not scaler:
        return jsonify({'error':'Model or scaler not loaded'}),500
    try:
        #get input
        data_str = request.form['price_sequence']
        input_prices = np.array([float(x.strip()) for x in data_str.split(',')])
        if len(input_prices) != TIME_STEP:
            return jsonify({
                'error':f'Input sequence missing all {TIME_STEP} prices',
                'received':len(input_prices)
                }), 400
        #reshape and scale input
        input_scaled = input_prices.reshape(-1,1)
        input_scaled = scaler.fit_transform(input_scaled)
        #reshape to expected LSTM 3D format
        input_lstm = input_scaled.reshape(1,TIME_STEP,1)
        #make prediction
        scaled_prediction = model.predict(input_lstm)
        #inverse transform results
        final_prediction = scaler.inverse_transform(scaled_prediction)
        #return result
        return jsonify({
            'success':True,
            'predicted price':round(final_prediction,2)

        })
    except ValueError:
            return jsonify({'error': 'Invalid input. Please ensure all inputs are numerical values separated by commas.'}), 400
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({'error': f'An internal error occurred during prediction: {str(e)}'}), 500


