import boto3
from boto3.dynamodb.conditions import Key
from config import Config
from boto3.dynamodb.conditions import Attr
import traceback

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', aws_access_key_id=Config.AWS_ACCESS_KEY,
                             aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                      region_name='us-west-2')



def get_player_options(player_request):
    try:
        required_role = player_request['required_role']
        competitive_level = player_request['competitive_level']
        is_igl_required = player_request['is_igl_required']
        
        # Access the DynamoDB table
        table = dynamodb.Table('final_player_profiles')

        limit_per_query = 20  # Fetch smaller batches
        filtered_players = []  # Store players who match the role filter

        # Query the appropriate GSI based on whether IGL is required or not
        index_name = 'igl_score-index' if is_igl_required else 'all_time_score-index'
        
        # Initial query
        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=Key('player_type').eq(competitive_level),
            ScanIndexForward=False,
            Limit=limit_per_query
        )
        
        # Apply role filtering in Python
        filtered_players.extend([player for player in response['Items'] if required_role in player['main_roles']])

        # Keep querying if we haven't found 10 players yet and there are more items
        while len(filtered_players) < 10 and 'LastEvaluatedKey' in response:
            response = table.query(
                IndexName=index_name,
                KeyConditionExpression=Key('player_type').eq(competitive_level),
                ExclusiveStartKey=response['LastEvaluatedKey'],
                ScanIndexForward=False,
                Limit=limit_per_query
            )
            # Continue filtering players in Python
            filtered_players.extend([player for player in response['Items'] if required_role in player['main_roles']])

        # Return the first 10 filtered players (or fewer if less than 10 found)
        return filtered_players[:10]
    
    except KeyError as e:
        print(f"KeyError: Missing key in player_request: {e}")
    
    except Exception as e:
        print(f"An error occurred: {e}")