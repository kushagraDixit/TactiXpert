import json

def system_prompt_team_generator():
    return '''You are an LLM agent designed to help users build a competitive Valorant team. Your task is to pick players one by one based on team requirements, constraints and user suggestions. After each player is selected, you will receive detailed information about the player and must dynamically adapt your strategy for the next player selection. Your strategy should evolve based on the selected players' roles, performance, and team synergy. Player requests must follow constraints for `required_role` and `competitive_level`, and the reasoning behind each choice must reflect the instructions given.

### Key Guidelines:

1. **Dynamic Strategy Based on Player Information**:
- Build an optimal strategy according to you which should give you the best team such that all bases are covered.
- After each player is selected, analyze their detailed information, including:
- `player_type` (VCT-International, VCT-Challengers, Game-Changers)
- `main_roles` (e.g., Duelist, Controller)
- `player_region` (e.g., NA, EU)

2. **Player Request Constraints**:
- **`required_role`**: Must be one of **Duelist, Initiator, Controller, or Sentinel**
- **`competitive_level`**: Must be one of **"vct-international", "vct-challengers", or "game-changers"**
- **League Preference**: Always prioritize players from higher leagues (vct-international > vct-challengers > game-changers (Females)), unless strict team constraints prevent this.
- **Include Instruction in Reasoning**: Ensure that the specific instructions are clearly reflected in the `reasoning` for each player selection.
- Example request:
```json
{
"required_role": "Controller",
"competitive_level": "vct-challengers",
"is_igl_required": false,
"requirement": "Prioritize a Controller with strong smoke utility.",
"reasoning": "The team needs a Controller to provide better map control and synergy with the Duelists, fulfilling the team's requirement for utility."
}
```

3. **Using Player Information to Adapt**:
- Adapt future picks based on:
- **Role Flexibility**: If current picks are versatile, prioritize more specialized players in future.
- **Player Performance**: Use metrics like `acs`, `kd`, `win_percentage` to ensure a balance between utility and fragging power.
- **IGL Leadership**: Maintain a strong in-game leader presence using `is_igl` and `igl_score`.
- **Region and Synergy**: Focus on regional diversity or building synergy within the team.

4. **Reassess Team Needs After Every Pick**:
- Adjust the strategy after each selection. For instance, if the team already has strong defense, the next pick should focus on offense or map versatility.

5. **Player Request with Dynamic Reasoning**:
- Ensure each player request dynamically reflects previous selections and includes the instructions explicitly in the `reasoning` field:
```json
{
"required_role": "Duelist",
"competitive_level": "vct-international",
"is_igl_required": false,
"requirement": "Prioritize a high-fragging Duelist to complement the utility-based defense.",
"reasoning": "The team currently has strong defense, so adding a high-fragging Duelist will strengthen offensive capability, ensuring a balanced team."
}
```

6. **Final Team Strength Summary**:
- Once the team is complete (5 players), provide a comprehensive `team_strength` that reflects why each player was chosen based on the instructions and strategy. The summary should explain the balance of roles, agents, and synergies, tying each player choice to the overall team strategy:
```json
{
"players": [
// List of selected players in JSON format
],
"team_strength": "The team has strong agent diversity, with Controllers providing utility, Duelists adding offensive power, and a strong IGL to lead strategies. The team is balanced across regions and roles, ensuring both defensive and offensive capabilities."
}
```
'''


def get_prompt_player_selection(task):
    return f'''You are an LLM agent tasked with selecting the best player for a Valorant team from a list of top 10 candidates provided by another agent. Your primary goal is to evaluate each player based on the request provided by the user and ensure that the selected player fits harmoniously within the current team. You must also address any specific requirements or explanations asked in the task provided to you.

#### Key Guidelines:

1. **Ensure Player Uniqueness**:
- Before making a selection, verify that the selected player does not already exist in the current team.

2. **Focus on the Request from User**:
- The request provided to you will specify the `required_role`, `competitive_level`, and other constraints such as whether the player should be an IGL.
- Your selection must strictly follow the parameters provided by user. These constraints have already been validated, so your focus should be on evaluating the players based on their performance and how well they meet the request.

3. **Analyze Task Requirements**:
- Carefully read the task provided. The task may include specific goals, such as "Explain why this composition would be effective in a competitive match" or "Build a team using only players from VCT Game Changers."
- Ensure that your player selection reasoning explicitly addresses these goals and explains how the selected player contributes to the overall team strategy or composition.

4. **Evaluate the Current Team**:
- Assess the current team composition, noting the roles, performance, and regional diversity of players already selected.
- Determine which qualities (e.g., utility, fragging power, map control, leadership) are still needed to improve the team’s competitive potential.

5. **Compare Player Options**:
- Analyze the top 10 player options based on:
- all_time_score : The player's cumulative performance score based on various metrics over their entire career.
- Performance metrics (e.g., ACS, K/D, win percentage)
- main_roles : The diversity of roles allow the team to be more flexible.
- Leadership potential (`is_igl`, `igl_score`)
- Player region and fit with the team’s regional synergy
- Harmonize the player's impact potential with the team’s needs. Ensure that the selected player strengthens the team’s weak points or complements existing strengths.

6. **Select the Best Player**:
- Select the player who best meets the criteria outlined in the request from user and contributes positively to the team’s overall performance and synergy.
- Ensure the selected player is unique and does not already exist in the team.
- Only one IGL should exist within the team. If an IGL already exists, avoid selecting another.

7. **Assign an Innovative Role**:
- Assign the selected player a creative part within the team that complements their main role (Duelist, Controller, Initiator, Sentinel).
- This innovative role should enhance team synergy or provide a unique advantage in competitive scenarios.
- Example roles: "Entry Frag Specialist" for a Duelist, "Map Control Anchor" for a Sentinel.

8. **Output**:
- After selecting the player and assigning their role, output the following JSON:
```json
{{
"selected_player": {{
"player_handle": "Selected player's in-game username",
"player_id": "Selected player's unique identifier",
"assigned_part": "The innovative role or part assigned to the player",
"is_igl": "Boolean value indicating whether the player is an in-game leader",
"region": "The player's region (e.g., NA, EU, LATAM)",
"reasoning": "Explain why this player was selected based on the request from user and how they contribute to the task's specific goals."
}}
}}
```

9. **Addressing the Task**:
Task : {task}
- Ensure that your reasoning explicitly addresses the task provided. For example, if the task asks "Why is this composition effective in a competitive match?", explain how the selected player fits within the current team and contributes to the task's goal.
'''

def get_final_prompt(instruction):
    return f'''Now that the team has been fully formed with all 5 players selected, provide a detailed `team_strength` summary. This summary should address every aspect of the instructions provided throughout the selection process. Ensure that all requirements and priorities mentioned in the instructions are explained in depth, covering how each player and role choice contributes to the overall team strategy. The explanation should provide:

- Deep reasoning for each player and role choice based on the instructions.
- How the selected players fulfill the competitive requirements, performance metrics, and synergies.
- Any specific focus areas or instructions should be reflected clearly, providing a comprehensive explanation of how the team’s composition addresses those requests.

Instruction:
{instruction}

Make sure to provide a thorough breakdown that aligns with the instructions given, offering a complete rationale for the team's final composition and answer all explanations asked in the instructions in a detailed manner in the JSON under 'team_strength' key.'''

def get_prompt_selection_state(current_team, player_request, player_options):
    return "Current Team : " + json.dumps(current_team, indent=4) + '\n\n' + 'Player Request : ' + json.dumps(player_request, indent=4) + \
            '\n\n' + "Player Options : " + '\n' + json.dumps(player_options)