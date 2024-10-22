# import google.generativeai as genai

# def gemini_response(prompt, model):
#     response = model.generate_content(prompt)
#     return response.text

# def getModel(system_prompt, key):
#     genai.configure(api_key=key)
#     return genai.GenerativeModel(
#             model_name="gemini-1.5-flash",
#             system_instruction=system_prompt)

import re
import json
from decimal import Decimal
from boto3.dynamodb.types import TypeSerializer

import re

def replace_vct_game_changers(text):
    # Create a regex pattern to match "VCT Game Changers" in any case
    pattern = re.compile(r"VCT[\s\-]*Game[\s\-]*Changers", re.IGNORECASE)
    
    # Replace all matches with "game changers"
    result = pattern.sub("game changers", text)
    return result

def get_object_by_player_id(json_list, player_id):
    # Iterate through each JSON object in the list
    for obj in json_list:
        # Check if 'player_id' exists and matches the provided value
        if obj.get('player_id') == player_id:
            return obj
    # Return None if no object with the given player_id is found
    return None

def extract_json_from_response_with_comment_removal(response: str):
    # Regular expression to match JSON inside triple backticks
    json_pattern = r'```json\s*(\{.*?\})\s*```'
    
    # Find the JSON substring using the pattern
    match = re.search(json_pattern, response, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        
        # Remove comments (anything after //)
        json_str = re.sub(r'//.*', '', json_str)
        
        try:
            # Parse the cleaned JSON string
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    else:
        print("No JSON found in the response.")
        return None
    

def decimal_default(obj):
    if isinstance(obj, Decimal):
        # Convert Decimals to float or int
        return float(obj) if obj % 1 != 0 else int(obj)
    raise TypeError

def convert_to_json(dynamodb_data):
    serializer = TypeSerializer()
    return {k: serializer.serialize(v)['M'] if isinstance(v, dict) else serializer.serialize(v) 
                       for k, v in dynamodb_data.items()}

def convert_dynamodb_map(dynamodb_map):
    # Recursively convert the DynamoDB JSON format to a general Python dictionary
    if isinstance(dynamodb_map, dict):
        result = {}
        for key, value in dynamodb_map.items():
            if isinstance(value, dict):
                # Check for specific DynamoDB types and convert accordingly
                if 'S' in value:
                    result[key] = value['S']
                elif 'N' in value:
                    result[key] = float(value['N']) if '.' in value['N'] else int(value['N'])
                elif 'BOOL' in value:
                    result[key] = value['BOOL']
                elif 'M' in value:
                    # Recursively handle nested maps
                    result[key] = convert_dynamodb_map(value['M'])
                elif 'L' in value:
                    # Recursively handle lists, converting list items
                    result[key] = [convert_dynamodb_map(item) if isinstance(item, dict) else item for item in value['L']]
            else:
                result[key] = value  # Directly assign if value is not a dictionary
        return result
    return dynamodb_map

import json
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from decimal import Decimal

# Initialize the deserializer
deserializer = TypeDeserializer()

# Function to convert DynamoDB item to JSON serializable format
def dynamodb_to_json_serializable(dynamodb_item):
    def deserialize(value):
        """Recursively deserializes DynamoDB items."""
        if isinstance(value, dict):
            # Deserialize each item in the dictionary
            return {k: deserialize(deserializer.deserialize(v)) for k, v in value.items()}
        elif isinstance(value, list):
            # If it's a list, deserialize each item in the list (including lists of maps)
            return [deserialize(item) for item in value]
        elif isinstance(value, Decimal):
            # Convert Decimal to float or int to make it JSON serializable
            return float(value) if value % 1 else int(value)
        else:
            return value

    return deserialize(dynamodb_item)


def dynamodb_to_python_map(dynamodb_doc):
    deserializer = TypeDeserializer()
    
    def convert_value(value):
        # Convert Decimal to float, process dicts and lists recursively
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert_value(v) for v in value]
        else:
            return value
    
    # Process the DynamoDB document
    def process_document(dynamodb_value):
        if isinstance(dynamodb_value, dict):
            # Check for DynamoDB type specifiers (e.g., 'N', 'S', 'M', 'L', etc.)
            # Use TypeDeserializer to handle these automatically
            if all(isinstance(v, dict) and len(v) == 1 and list(v.keys())[0] in ['S', 'N', 'BOOL', 'M', 'L'] for v in dynamodb_value.values()):
                # If the document contains type specifiers, deserialize each field
                return {k: deserializer.deserialize(v) for k, v in dynamodb_value.items()}
            else:
                # Otherwise, recursively process nested dictionaries
                return {k: convert_value(v) for k, v in dynamodb_value.items()}
        elif isinstance(dynamodb_value, list):
            # Recursively process lists
            return [process_document(item) for item in dynamodb_value]
        else:
            # Base case: return the value as is
            return convert_value(dynamodb_value)
    
    return process_document(dynamodb_doc)

def transform_document(initial_doc):
    # Extract necessary fields for the final document
    final_doc = {
        "player_handle": initial_doc.get("player_handle"),
        "player_id": initial_doc.get("player_id"),
        "player_type": initial_doc.get("player_type"),
        "main_roles": initial_doc.get("main_roles"),
        "player_region": initial_doc.get("player_region"),
        # Nested player_info map
        "player_info": {
            "first_name": initial_doc["player_info"].get("first_name"),
            "last_name": initial_doc["player_info"].get("last_name"),
            "status": initial_doc["player_info"].get("status")
        },
        "team_name": initial_doc.get("team_name"),
        "team_acronym": initial_doc.get("team_acronym"),
        "all_time_score": initial_doc.get("all_time_score"),
        "kd": initial_doc.get("kd"),
        "top_5_agents": initial_doc.get("top_5_agents"),
        "total_kills": initial_doc.get("total_kills"),
        "total_wins": initial_doc.get("total_wins"),
        "last_15_stats": initial_doc.get("last_15_stats"),
        "win_percentage": initial_doc.get("win_percentage"),
        "is_igl": initial_doc.get("is_igl"),
        "total_games": initial_doc.get("total_games"),
        "acs": initial_doc.get("acs"),
        "igl_score": initial_doc.get("igl_score"),
        "team_players": initial_doc.get("all_time_stats", {}).get("team_players"),
    }

    return final_doc