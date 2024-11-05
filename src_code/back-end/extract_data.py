import boto3
from boto3.dynamodb.conditions import Key
from config import Config
from boto3.dynamodb.conditions import Attr
import traceback
from utils import dynamodb_to_python_map, parse_date

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', aws_access_key_id=Config.AWS_ACCESS_KEY,
                             aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                      region_name='us-west-2')

dynamodb_client = boto3.client('dynamodb', aws_access_key_id=Config.AWS_ACCESS_KEY,
                             aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                      region_name='us-west-2')


def is_replacement_player_required(relevant_player_map, request_calls):
    players_to_be_replaced = []
    replacement_request_calls = []
    replacement_required = False
    for player_map in relevant_player_map:
        if player_map['need_replacement']:
            players_to_be_replaced.append(player_map)
            replacement_required = True
            for call in request_calls:
                if player_map['player_id'] == call['selected_player']:
                    replacement_request_calls.append(call)
                    break
    
    return replacement_required, players_to_be_replaced, replacement_request_calls


def get_player_options(player_request):
    try:
        required_role = player_request['required_role']
        competitive_level = player_request['competitive_level']
        is_igl_required = player_request['is_igl_required']
        
        # Access the DynamoDB table
        table = dynamodb.Table('player_profiles')

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


def get_relevant_team_objects(relevant_players, current_team, current_team_store):
    # Create a set of player_ids from relevant_players for quick lookup
    relevant_player_ids = {player['player_id'] for player in relevant_players}

    # Create a dictionary from current_team mapping player_id to their reasoning
    player_reasoning_map = {player['player_id']: player.get('reasoning', '') for player in current_team}

    player_part_map = {player['player_id']: player.get('assigned_part', '') for player in current_team}

    # Filter current_team_store based on relevant_player_ids and add reasoning
    filtered_team_store = []
    for player in current_team_store:
        player_id = player['player_id']
        if player_id in relevant_player_ids:
            # Add reasoning from current_team if exists
            if player_id in player_reasoning_map:
                player['reasoning'] = player_reasoning_map[player_id]
                player['assigned_part'] = player_part_map[player_id]
            else:
                player['reasoning'] = 'No reasoning provided'  # Fallback if reasoning not found
            filtered_team_store.append(player)

    return filtered_team_store

def get_match_history_for_players(filtered_player_info):
    """Fetch and process match history documents for a list of players from DynamoDB."""
    player_ids = [player['player_id'] for player in filtered_player_info]
    keys = [{'player_id': {'S': player_id}} for player_id in player_ids]
    table_name = 'player_matches_updated'

    try:
        response = dynamodb_client.batch_get_item(
            RequestItems={table_name: {'Keys': keys}}
        )
        
        match_history = response.get('Responses', {}).get(table_name, [])
        match_history = [dynamodb_to_python_map(item) for item in match_history]
        
        # Initialize match history map
        match_history_map = {}

        for player_data in match_history:
            player_id = player_data.get('player_id')
            match_stats = player_data.get('match_stats', [])

            # Sort match_stats by date and pick the most recent 10 matches
            sorted_matches = sorted(match_stats, key=lambda x: parse_date(x['date']), reverse=True)[:10]
            
            # Filter each match to only include required keys
            filtered_matches = [
                {
                    'acs': match.get('acs'),
                    'kd': match.get('kd'),
                    'kills': match.get('kills'),
                    'deaths': match.get('deaths'),
                    'assists': match.get('assists'),
                    'agent': match.get('agent'),
                    'map': match.get('map'),
                    'team_name': match.get('team_name'),
                    'opponent_team_name': match.get('opponent_team_name'),
                    'win': match.get('win'),
                    'league': match.get('league'),
                    'date' : match.get('date')
                }
                for match in sorted_matches
            ]

            # Add to match history map with player_id as key
            match_history_map[player_id] = filtered_matches

        # Update filtered_player_info with recent_match_performance
        for player in filtered_player_info:
            player_id = player.get('player_id')
            # Add recent_match_performance key if there is a match history for the player_id
            if player_id in match_history_map:
                player['recent_match_performance'] = match_history_map[player_id]
        
        return filtered_player_info

    except Exception as e:
        print(f"Error fetching match history: {e}")
        return {}