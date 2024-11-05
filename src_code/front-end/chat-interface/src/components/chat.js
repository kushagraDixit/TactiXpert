import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import PlayerCard from './PlayerCard';
import './chat.css';
import MarkdownToHtml from './MarkdownToHtml';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [userMessage, setUserMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);
  const agents = useRef([]); // Store the list of used agents here
  const current_agents = useRef([]); // Maintain the current agents list
  const current_team_store = useRef([]); // Maintain the team store
  const current_request_store = useRef([]); // Maintain the team store

  const get_request_type = (request) => {
    if (request.toLowerCase().includes('build') || request.toLowerCase().includes('create')) {
      return 'team_generation';
    }
    return 'other_request_type';
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const getAgentImage = (topAgents) => {
    for (let agent of topAgents) {
      if (agent === 'KAY/O') agent = 'KAYO'; // Handle KAY/O case
      if (!agents.current.includes(agent)) {
        agents.current.push(agent);
        return `Agents/${agent}.webp`;
      }
    }
    return ''; // Fallback if no agent found
  };

  const sendMessage = async () => {
    if (userMessage.trim()) {
      const newMessage = { sender: 'user', text: userMessage, id: new Date().getTime() }; // Unique ID for each user message
      setMessages([...messages, newMessage]);
  
      const requestType = get_request_type(userMessage);
  
      if (requestType === 'team_generation') {
        setLoading(true);
        try {
          const response = await axios.post(
            `http://127.0.0.1:5000/request_team`,
            {
              request: userMessage,
              request_type: requestType,
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
          );

          const responseData = response.data['Response'];
          const current_team = responseData['current_team'];
          const final_team_combined = responseData['final_team_combined'];
          const request_calls = responseData['request_calls'];
          const team_store = responseData['team_store'];

          agents.current = []; // Reset agents to avoid duplicates
          current_agents.current = current_team; // Update current_agents with the new current team
          current_team_store.current = team_store;
          current_request_store.current = request_calls
          
          
          //console.log("Current Team: ", current_team)
          
          // Add each player's data to messages with unique keys
          current_team.forEach((player, i) => {
            const agentImage = getAgentImage(player.top_5_agents); // Get the agent image
            
            const requestReasoning = request_calls[i]?.reasoning || 'No reasoning available';
            const playerReasoning = player?.reasoning || 'No reasoning available';

            setMessages((prevMessages) => [
              ...prevMessages,
              {
                sender: 'bot',
                player, // Player object
                agentImage, // Agent image to display
                requestReasoning, // Pass the reasoning
                playerReasoning, // Player's reasoning
                id: `${player.player_id}-${new Date().getTime()}`, // Unique key for each player message
              },
            ]);
          });


          if (final_team_combined?.team_strength) {
            const teamStrengthId = `team-strength-${new Date().getTime()}`;
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                sender: 'bot',
                text: `${final_team_combined.team_strength}`,
                type: 'team_strength', // Mark this message as team strength
                id: teamStrengthId, // Unique ID for the team strength message
              },
            ]);
          }
        } catch (error) {
          const errorMessage =
            error.response?.data?.message || error.message || 'Unknown error occurred.';
          setMessages((prevMessages) => [
            ...prevMessages,
            { sender: 'bot', text: `Error: ${errorMessage}`, id: `error-${new Date().getTime()}` }, // Unique ID for error messages
          ]);
        }

        setLoading(false);
      } else if (requestType === 'other_request_type') {
        setLoading(true);
        try {

          const response = await axios.post(
            `http://127.0.0.1:5000/request_team`,
            {
              request: userMessage,
              request_type: requestType,
              current_team: current_agents.current,
              team_store: current_team_store.current,
              request_calls: current_request_store.current
            },
            {
              headers: {
                'Content-Type': 'application/json',
              }
            }
          );

          const responseData = response.data['Response'];
          const queryResponse = responseData['query_response'];
          const player_replacements = responseData['player_replacements']

          console.log("Player Replacements: ", player_replacements)

          // Check if player_replacements is not empty
          if (player_replacements && player_replacements.length > 0) {
            agents.current = []; // Reset agents to avoid duplicates
            
            // Loop through player_replacements to add their cards
            player_replacements.forEach((player, i) => {
              const agentImage = getAgentImage(player.top_5_agents);

              setMessages((prevMessages) => [
                ...prevMessages,
                {
                  sender: 'bot',
                  player,
                  agentImage,
                  playerReasoning: player.reasoning || 'No reasoning available',
                  id: `${player.player_id}-${new Date().getTime()}`, // Unique key for each replacement player message
                },
              ]);
            });
          }

          // Add the query_response to the chat
          setMessages((prevMessages) => [
            ...prevMessages,
            {
              sender: 'bot',
              type: 'query_response',
              text: `${queryResponse}`,
              id: `query-response-${new Date().getTime()}`, // Unique ID for the query response
            },
          ]);
        } catch (error) {
          const errorMessage =
            error.response?.data?.message || error.message || 'Unknown error occurred.';
          setMessages((prevMessages) => [
            ...prevMessages,
            { sender: 'bot', text: `Error Encountered During your query. Please Enter your Query Again!`, id: `error-${new Date().getTime()}` }, // Unique ID for error messages
          ]);
        }

        setLoading(false);
      }
    }
    setUserMessage('');
  };

  return (
    <div className="chat-container">
      <div className="chat-header"></div>
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={msg.id || index} className={`message ${msg.sender}`}> {/* Use msg.id or fallback to index */}
            {msg.player ? (
              <PlayerCard
                player={msg.player}
                agentImage={msg.agentImage}
                requestReasoning={msg.requestReasoning}
                playerReasoning={msg.playerReasoning}
              />
            ) : msg.type === 'team_strength' || msg.type === 'query_response' ? (
              <div className="team-strength-box">
                  <MarkdownToHtml markdownText={msg.text} ></MarkdownToHtml>
              </div>
            ) : (
              <p>{msg.text}</p>
            )}
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="loading-spinner"></div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      <div className="input-box">
        <input
          type="text"
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          placeholder="Type your message..."
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;
