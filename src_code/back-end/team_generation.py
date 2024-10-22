from prompts import system_prompt_team_generator, get_prompt_player_selection, get_prompt_selection_state, get_final_prompt
from models import GeminiLLM, BedrockLLM
from config import Config
import traceback
from utils import extract_json_from_response_with_comment_removal
from extract_data import get_player_options
from utils import transform_document, get_object_by_player_id, replace_vct_game_changers, dynamodb_to_python_map
import json

def get_selected_player(input_map, player_request, task):
    
    system_prompt_player_selector = get_prompt_player_selection(task)
    player_selector = GeminiLLM(api_key=Config.GEMINI_KEY, system_instruction=system_prompt_player_selector)

    current_state_for_selection = get_prompt_selection_state(input_map['current_team'], player_request, input_map['player_options'])

    #print('SELECTION STATE PROPT : ', current_state_for_selection)

    selected_player = player_selector.call(current_state_for_selection)
    #print("Selected Player: ", selected_player)

    selected_player = extract_json_from_response_with_comment_removal(str(selected_player))

    return selected_player


def generate_team(request):
    try:
        # Initialize the model
        system_instruction = system_prompt_team_generator()
        # gemini_llm = GeminiLLM(api_key=Config.GEMINI_KEY, system_instruction=system_instruction)
        gemini_llm = BedrockLLM()
        request_calls = []
        current_team = []
        current_team_store = []

        request = replace_vct_game_changers(request)

        instruction = request

        request = "Instructions: " + '\n' + request

        print(f"Final Request : {request}")

        for i in range(5):
            retries = 3  # Number of retries per iteration
            success = False

            while not success and retries > 0:
                try:
                    # Call the model with the request
                    result = gemini_llm.call(request)
                    player_request = extract_json_from_response_with_comment_removal(str(result))
                    request_calls.append(player_request)

                    #print(f"Player Request {i+1}: \n{player_request}\n")

                    # Fetch player options
                    player_options = get_player_options(player_request)
                    player_options = [dynamodb_to_python_map(player) for player in player_options]

                    # Prepare player options input
                    player_options_input = {
                        'current_team': current_team,
                        'player_options': [transform_document(player) for player in player_options]
                    }

                    # Get selected player
                    player_selected = get_selected_player(player_options_input, player_request, instruction)
                    #print(f"Player {i+1} Selected: \n{player_selected}\n\n")
                    print(f"Player {i+1} Selected\n")

                    # Fetch and update selected player info
                    selected_player_info = get_object_by_player_id(player_options, player_selected['selected_player']['player_id'])
                    current_team_store.append(selected_player_info)
                    selected_player_info = transform_document(selected_player_info)
                    selected_player_info.pop('last_15_stats')
                    selected_player_info['assigned_part'] = player_selected['selected_player']['assigned_part']
                    selected_player_info['reasoning'] = player_selected['selected_player']['reasoning']

                    # Append selected player to the current team
                    current_team.append(selected_player_info)

                    # Update the request string
                    request += '\n' + result + '\n\n' + "Player Selected : " + json.dumps(selected_player_info) + '\n'

                    # Mark this iteration as successful
                    success = True

                except Exception as e:
                    # Handle the exception, retry, and revert the state changes
                    print(f"An error occurred in Team Generation iteration {i+1}, retrying... {retries} retries left. Error: {str(e)}")
                    traceback.print_exc()
                    if len(request)>0:
                        print("Exception occured at request : ", player_request )

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
                final_prompt = request + '\n' + get_final_prompt(instruction)
                result = gemini_llm.call(final_prompt)
                final_team_combined = extract_json_from_response_with_comment_removal(str(result))
                success = True
            except Exception as e:
                retries -= 1
                print(f"An error occurred in Final Prompt iteration {i+1}, retrying... {retries} retries left. Error: {str(e)}")

        
        #print("Current Team: ", current_team)
        print(str(result))

        # Return the final result after successful iterations
        return final_team_combined, current_team, current_team_store, request_calls

    except Exception as e:
        # Print the error message and the traceback for debugging
        error_message = f"An error occurred: {str(e)}"
        traceback.print_exc()  # This will print the full traceback for debugging
        return error_message



# def generate_team(request):
#     try:
#         # Initialize the model
#         system_instruction = system_prompt_team_generator()
#         gemini_llm = GeminiLLM(api_key=Config.GEMINI_KEY, system_instruction=system_instruction)
#         request_calls = []
#         current_team = []

#         request = replace_vct_game_changers(request)

#         instruction = request

#         request = "Instructions: " + '\n' + request

#         print(f"Final Request : {request}")

#         for i in range(5):
#             retries = 3  # Number of retries per iteration
#             success = False

#             while not success and retries > 0:
#                 try:
#                     # Call the model with the request
#                     result = gemini_llm.call(request)
#                     player_request = extract_json_from_response_with_comment_removal(str(result))
#                     request_calls.append(player_request)

#                     #print(f"Player Request {i+1}: \n{player_request}\n")

#                     # Fetch player options
#                     player_options = get_player_options(player_request)

#                     # Prepare player options input
#                     player_options_input = {
#                         'current_team': current_team,
#                         'player_options': [convert_dynamodb_map(transform_document(convert_to_json(player))) for player in player_options]
#                     }

#                     # Get selected player
#                     player_selected = get_selected_player(player_options_input, player_request)
#                     #print(f"Player {i+1} Selected: \n{player_selected}\n\n")
#                     print(f"Player {i+1} Selected\n")

#                     # Fetch and update selected player info
#                     selected_player_info = get_object_by_player_id(player_options, player_selected['selected_player']['player_id'])
#                     selected_player_info = convert_dynamodb_map(convert_to_json(selected_player_info))
#                     selected_player_info['assigned_part'] = player_selected['selected_player']['assigned_part']
#                     selected_player_info['reasoning'] = player_selected['selected_player']['reasoning']

#                     # Append selected player to the current team
#                     current_team.append(selected_player_info)

#                     # Update the request string
#                     request += '\n' + result + '\n\n' + "Player Selected : " + json.dumps(selected_player_info) + '\n'

#                     # Mark this iteration as successful
#                     success = True

#                 except Exception as e:
#                     # Handle the exception, retry, and revert the state changes
#                     print(f"An error occurred in iteration {i+1}, retrying... {retries} retries left. Error: {str(e)}")
#                     traceback.print_exc()

#                     # Revert any changes in the current iteration
#                     if request_calls:
#                         request_calls.pop()
#                     if current_team:
#                         current_team.pop()

#                     request += '\n' + 'Request for next player: \n'

#                     # Decrement the retries counter
#                     retries -= 1

#                     # If retries are exhausted, raise the error
#                     if retries == 0:
#                         raise Exception(f"Failed to complete iteration {i+1} after multiple retries.")
                    
#         final_prompt = request + '\n' + get_final_prompt(instruction)
#         result = gemini_llm.call(final_prompt)

#         print("Current Team: ", current_team)

#         print(extract_json_from_response_with_comment_removal(str(result)))


#         # Return the final result after successful iterations
#         return result

#     except Exception as e:
#         # Print the error message and the traceback for debugging
#         error_message = f"An error occurred: {str(e)}"
#         traceback.print_exc()  # This will print the full traceback for debugging
#         return error_message
