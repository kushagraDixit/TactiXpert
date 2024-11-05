from prompts import create_system_prompt_team_generator, create_prompt_player_selection, create_prompt_selection_state, create_final_prompt, \
    create_system_prompt_find_relevant_players, create_relevant_players_prompt, create_system_prompt_query_responder, create_prompt_query_responder, \
    create_system_prompt_replacement_selector, create_prompt_replacement_selector
from models import GeminiLLM, BedrockLLM
from config import Config
import traceback
from extract_data import get_player_options, get_relevant_team_objects, get_match_history_for_players, is_replacement_player_required
from utils import transform_document, get_object_by_player_id, replace_vct_game_changers, dynamodb_to_python_map, extract_json_from_response_with_comment_removal, extract_json_for_final_response
import json

def get_selected_player(input_map, player_request, task):
    
    system_prompt_player_selector = create_prompt_player_selection(task)
    player_selector = BedrockLLM(system_instruction=system_prompt_player_selector)

    current_state_for_selection = create_prompt_selection_state(input_map['current_team'], player_request, input_map['player_options'])

    #print('SELECTION STATE PROPT : ', current_state_for_selection)

    selected_player = player_selector.call(current_state_for_selection)
    #print("Selected Player: ", selected_player)

    selected_player = extract_json_from_response_with_comment_removal(str(selected_player))

    return selected_player


def generate_team(request):
    try:
        # Initialize the model
        system_instruction = create_system_prompt_team_generator()
        team_planner = BedrockLLM(system_instruction=system_instruction)
        request_calls = []
        current_team = []
        current_team_store = []

        request = replace_vct_game_changers(request)

        instruction = request

        request = "Instructions: " + '\n' + request

        #print(f"Final Request : {request}")

        for i in range(5):
            retries = 3  # Number of retries per iteration
            success = False

            while not success and retries > 0:
                try:
                    # Call the model with the request
                    print(f"******At iteration {i+1} : Current Team has {len(current_team)} players")
                    result = team_planner.call(request)
                    #print(f"Player Request {i+1} String: \n{result}\n")
                    player_request = None
                    player_request = extract_json_from_response_with_comment_removal(str(result))
                    request_calls.append(player_request)

                    print(f"Player Request {i+1}: \n{player_request}\n")

                    # Fetch player options
                    player_options = get_player_options(player_request)
                    player_options = [dynamodb_to_python_map(player) for player in player_options]

                    # Prepare player options input
                    player_options_input = {
                        'current_team': current_team,
                        'player_options': [transform_document(player) for player in player_options]
                    }

                    # print("-------------------------------------------------------------------------------------------")
                    # print(json.dumps(player_options[0], indent = 4))
                    # print("-------------------------------------------------------------------------------------------")

                    # Get selected player
                    player_selected = get_selected_player(player_options_input, player_request, instruction)
                    #print(f"Player {i+1} Selected: \n{player_selected}\n\n")
                    print(f"Player {i+1} Selected\n : {player_selected['selected_player']['player_handle']}")

                    # Fetch and update selected player info
                    selected_player_info = get_object_by_player_id(player_options, player_selected['selected_player']['player_id'])
                    current_team_store.append(selected_player_info)
                    if not player_request['is_igl_required']:
                        selected_player_info['is_igl'] = False
                    selected_player_info = transform_document(selected_player_info)
                    selected_player_info.pop('last_15_stats')
                    selected_player_info['assigned_part'] = player_selected['selected_player']['assigned_part']
                    selected_player_info['reasoning'] = player_selected['selected_player']['reasoning']

                    # Append selected player to the current team
                    current_team.append(selected_player_info)

                    # Update the request string
                    if i<4:
                        request += '\n' + result + '\n\n' + "Player Selected : " + json.dumps(selected_player_info) + '\n\n' + f"{i+1} Players Selected!" + '\n' + 'Request for next player: \n'
                    else:
                        request += '\n' + result + '\n\n' + "Player Selected : " + json.dumps(selected_player_info) + '\n\n' + f"{i+1} Players Selected!" + '\n' + 'Team is now Complete!! \n'
                        
                    # Mark this iteration as successful
                    success = True

                except Exception as e:
                    # Handle the exception, retry, and revert the state changes
                    print(f"An error occurred in Team Generation iteration {i+1}, retrying... {retries} retries left. Error: {str(e)}")
                    traceback.print_exc()
                    if len(request)>0:
                        if player_request:
                            print("Exception occured at request : ", request)

                            print("Exception occured at player_request : ", player_request)
                        else:
                            print("Exception occured at result: ", result)

                    # Revert any changes in the current iteration
                    if request_calls:
                        request_calls.pop()

                    request += '\n' + 'Request for next player: \n'

                    # Decrement the retries counter
                    retries -= 1

                    # If retries are exhausted, raise the error
                    if retries == 0:
                        raise Exception(f"Failed to complete iteration {i+1} after multiple retries.")

        retries = 3
        success = False
        while not success and retries > 0:
            try:            
                final_prompt = request + '\n' + create_final_prompt(instruction)
                # print("***********************FINAL PROMPT INPUT***************************")
                # print(final_prompt)
                # print('********************************************************************')
                result = team_planner.call(final_prompt)
                # final_team_combined = extract_json_from_response_with_comment_removal(str(result))
                final_strength_summary = str(result)
                # print(final_strength_summary)
                final_team_combined = {'team_strength' : final_strength_summary}
                success = True
            except Exception as e:
                retries -= 1
                print("Exception at final Response: ", result)
                print(f"An error occurred in Final Prompt iteration {i+1}, retrying... {retries} retries left. Error: {str(e)}")

        for i, call in enumerate(request_calls):
            call['selected_player'] = current_team[i]['player_id']
        #print("Current Team: ", current_team)
        # print(str(result))

        # Return the final result after successful iterations
        return final_team_combined, current_team, current_team_store, request_calls

    except Exception as e:
        # Print the error message and the traceback for debugging
        error_message = f"An error occurred: {str(e)}"
        traceback.print_exc()  # This will print the full traceback for debugging
        return "Error Encountered During your query. Please Enter your Query Again!"

def replace_player_in_current_team(current_team, selected_player_info, player_to_be_replaced):
    for i, player in enumerate(current_team):
        if player['player_id']==player_to_be_replaced['player_id']:
            current_team[i] = selected_player_info
            return current_team

def get_replacement_players(players_to_be_replaced, replacement_request_calls, query, current_team):
    
    replacement_players = []

    for player, player_request in zip(players_to_be_replaced, replacement_request_calls):
        retries = 3  # Number of retries per iteration
        success = False
        while not success and retries > 0:
            try:
                system_prompt_replacement_selector = create_system_prompt_replacement_selector(query)
                replacement_selector = BedrockLLM(system_instruction=system_prompt_replacement_selector)

                player_options = get_player_options(player_request)

                player_options = [dynamodb_to_python_map(player) for player in player_options]

                # Prepare player options input
                player_options_input = {
                    'current_team': current_team,
                    'player_options': [transform_document(player) for player in player_options]
                }

                prompt_replacement_selector = create_prompt_replacement_selector(player_options_input, player_request, player)

                selected_replacement = replacement_selector.call(prompt_replacement_selector)

                # print("Response for replacement : \n", selected_replacement)

                selected_replacement = extract_json_from_response_with_comment_removal(str(selected_replacement))

                selected_replacement_info = get_object_by_player_id(player_options, selected_replacement['replacement_player']['player_id'])

                if not player_request['is_igl_required']:
                    selected_replacement_info['is_igl'] = False
                selected_replacement_info = transform_document(selected_replacement_info)
                selected_replacement_info.pop('last_15_stats')
                selected_replacement_info['assigned_part'] = selected_replacement['replacement_player']['assigned_part']
                selected_replacement_info['reasoning'] = selected_replacement['replacement_player']['reasoning']

                replacement_players.append(selected_replacement_info)

                current_team = replace_player_in_current_team(current_team, selected_replacement_info, player)
                success = True

            except Exception as e:
                # Handle the exception, retry, and revert the state changes
                print(f"An error occurred in Player Replacement, retrying... {retries} retries left. Error: {str(e)}")
                traceback.print_exc()
                # Decrement the retries counter
                retries -= 1
                # If retries are exhausted, raise the error
                if retries == 0:
                    raise Exception(f"Failed to complete after multiple retries.")
                
    return replacement_players

def get_question_response(request, current_team, current_team_store, request_calls):

    retries = 3  # Number of retries per iteration
    success = False
    while not success and retries > 0:
        try:
            query = request
            replacement_required = False
            players_to_be_replaced = []
            replacement_request_calls = []
            replacement_players = []
            relevant_players_info = []
            
            system_prompt_relevant_players = create_system_prompt_find_relevant_players()
            
            relevent_players_finder = BedrockLLM(system_instruction=system_prompt_relevant_players)

            relevent_players_prompt = create_relevant_players_prompt(json.dumps(current_team, indent=4), query)

            relevant_players_response = relevent_players_finder.call(prompt=relevent_players_prompt)
            print("relevant_players_response: ", relevant_players_response)

            relevant_players = extract_json_from_response_with_comment_removal(str(relevant_players_response))
            match_history_required = relevant_players['match_history_required']

            #print("Relevant players: ",relevant_players['relevant_players'])
            print("Match history required: ",match_history_required)

            if len(relevant_players['relevant_players'])>0:
                relevant_players_info = get_relevant_team_objects(relevant_players['relevant_players'], current_team, current_team_store)

                print(f"Query : {query}")

                if match_history_required:
                    relevant_players_info = get_match_history_for_players(relevant_players_info)

                #print(f"relevant_players_info  : {relevant_players_info}")
                #print("Request Calls : ", request_calls)
                replacement_required, players_to_be_replaced, replacement_request_calls = is_replacement_player_required(relevant_players['relevant_players'], request_calls)

                if replacement_required:
                    replacement_players = get_replacement_players(players_to_be_replaced, replacement_request_calls, query, current_team)

            # print("Replacement Players : ", replacement_players)
            
            system_prompt_query_responder = create_system_prompt_query_responder(replacement_required)

            # print(f"system_prompt_query_responder : \n{system_prompt_query_responder}")
            
            query_responder = BedrockLLM(system_instruction=system_prompt_query_responder)

            prompt_query_responder = create_prompt_query_responder(json.dumps(relevant_players_info, indent=4), query, replacement_required, players_to_be_replaced, replacement_players)

            # print(f"prompt_query_responder : \n{prompt_query_responder}")

            final_response = query_responder.call(prompt=prompt_query_responder)

            #print("final_response : ", final_response)

            return final_response, replacement_players

        except Exception as e:
            # Print the error message and the traceback for debugging
            error_message = f"An error occurred: {str(e)}"
            traceback.print_exc()  # This will print the full traceback for debugging
            retries -= 1
            # If retries are exhausted, raise the error
            if retries == 0:
                 return "Error Encountered During your query. Please Enter your Query Again!"
            
