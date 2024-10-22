from flask import Flask, jsonify, request
from team_generation import generate_team
from flask_cors import CORS

app = Flask(__name__)
from config import DevelopmentConfig  # Load the config

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# # In-memory cache to store responses
# cache = {}

# Endpoint 1: Basic health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'App is running!'}), 200

# Endpoint 2: Add two numbers passed as query parameters
@app.route('/add', methods=['GET'])
def add_numbers():
    try:
        num1 = float(request.args.get('num1'))
        num2 = float(request.args.get('num2'))
        result = num1 + num2
        return jsonify({'result': result}), 200
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid input! Please provide two numbers.'}), 400

# Endpoint 2: Add two numbers passed as query parameters
@app.route('/request_team', methods=['GET'])
def request_team():
    try:
        print("=======================New Request Start==================================")
        request_str = str(request.args.get('request'))
        request_type = str(request.args.get('request_type'))

        # if request_str in cache:
        #     return jsonify(cache[request_str]), 200

        if request_type=='team_generation':
            final_team_combined, current_team, team_store, request_calls = generate_team(request_str)

        # cache[request_str] = {'Response': {'response_type' : request_type, 'final_team_combined' : final_team_combined, 'current_team' : current_team, 'team_store' : team_store, 'request_calls' : request_calls}}
        
        print("===============================Request End===================================")
        return jsonify({'Response': {'response_type' : request_type, 'final_team_combined' : final_team_combined, 'current_team' : current_team, 'team_store' : team_store, 'request_calls' : request_calls}}), 200
    except (TypeError, ValueError):
        print("===============================Request End===================================")
        return jsonify({'error': 'Invalid input! Please provide request'}), 400

if __name__ == '__main__':
    app.run(debug=True)
