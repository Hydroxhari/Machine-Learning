from flask import Flask, request, jsonify
from flask_cors import CORS
import util

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

@app.route('/get_location_names', methods=['GET'])
def get_location_names():
    response = jsonify({
        'locations': util.get_location_names()
    })
    return response

@app.route('/predict_home_price', methods=['POST'])
def predict_home_price():
    try:
        req_data = request.get_json()
        sqft = float(req_data['sqft'])
        location = req_data['location']
        bhk = int(req_data['bhk'])
    except (KeyError, ValueError) as e:
        return jsonify({'error': 'Invalid input', 'message': str(e)}), 400

    response = jsonify({
        'estimated_price': util.get_estimated_price(location, bhk, sqft)
    })
    return response

if __name__ == "__main__":
    print("Starting Python Flask Server For Home Price Prediction...")
    util.load_saved_artifacts()
    app.run()
