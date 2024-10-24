from flask import Flask, jsonify, request
from team_generation import generate_team, get_question_response
from flask_cors import CORS
import json

app = Flask(__name__)
from config import DevelopmentConfig  # Load the config

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# # In-memory cache to store responses
cache = {}

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
@app.route('/request_team', methods=['POST'])
def request_team():
    try:
        print("=======================New Request Start==================================")
        
        data = request.get_data()  # Get raw data
        data_str = data.decode('utf-8')

        body = json.loads(data_str)

        request_str =       body.get('request')
        request_type =      body.get('request_type')
        team_info =         body.get('current_team', None)
        team_full_info =    body.get('team_store', None)

        # if request_str in cache:
        #     return jsonify(cache[request_str]), 200

        if request_type=='team_generation':
            final_team_combined, current_team, team_store, request_calls = generate_team(request_str)
            # cache[request_str] = {'Response': {'response_type' : request_type, 'final_team_combined' : final_team_combined, 'current_team' : current_team, 'team_store' : team_store, 'request_calls' : request_calls}}
            print("===============================Request End===================================")
            return jsonify({'Response': {'response_type' : request_type, 'final_team_combined' : final_team_combined, 'current_team' : current_team, 'team_store' : team_store, 'request_calls' : request_calls}}), 200
        if request_type=='other_request_type':
            final_response = get_question_response(request_str, team_info, team_full_info)
            print("===============================Request End===================================")
            return jsonify({'Response': {'response_type' : request_type, 'query_response' : final_response}}), 200


        
        
        
    except (TypeError, ValueError):
        print("===============================Request End===================================")
        return jsonify({'error': 'Invalid input! Please provide request'}), 400

if __name__ == '__main__':
    app.run(debug=True)
