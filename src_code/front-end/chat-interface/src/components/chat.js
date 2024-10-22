import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import PlayerCard from './PlayerCard';
import './chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [userMessage, setUserMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);
  const agents = useRef([]); // Store the list of used agents here

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
      const newMessage = { sender: 'user', text: userMessage };
      setMessages([...messages, newMessage]);
  
      const requestType = get_request_type(userMessage);
  
      setLoading(true);
      setMessages((prevMessages) => [
        ...prevMessages,
      ]);

      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/request_team?request=${encodeURIComponent(
            userMessage
          )}&request_type=${encodeURIComponent(requestType)}`,
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            cache: false,
          }
        );

        const responseData = response.data['Response'];
        const response_type = responseData['response_type'];
        const current_team = responseData['current_team'];
        const final_team_combined = responseData['final_team_combined'];
        const request_calls = responseData['request_calls'];

        console.log('final_combined:', current_team)
        console.log('request_calls:', request_calls)

        // console.log('Request Call reason:', request_calls[0].reasoning)
        // console.log('Player reason:', current_team[0].reasoning)
        
        agents.current = []
        if (response_type === 'team_generation') {
        current_team.forEach((player, i) => {
          const agentImage = getAgentImage(player.top_5_agents); // Get the agent image

          
        //   console.log('Request Call reason:', request_calls[i].reasoning)
        const requestReasoning = request_calls[i]?.reasoning || 'No reasoning available';
        const playerReasoning = player?.reasoning || 'No reasoning available';
      
        console.log('Passing requestReasoning:', requestReasoning); // Debug log
        console.log('Passing playerReasoning:', playerReasoning); // Debug log

          setMessages((prevMessages) => [
            ...prevMessages,
            {
              sender: 'bot',
              player, // Player object
              agentImage, // Agent image to display
              requestReasoning, // Pass the reasoning
              playerReasoning, // Player's reasoning
            },
          ]);
        });

        setMessages((prevMessages) => [
            ...prevMessages,
            {
              sender: 'bot',
              text: `${final_team_combined?.team_strength || "Did not recieved Team Strength"}`,
              type: 'team_strength', // Add a type to differentiate it from regular messages
            },
          ]);
        }
      } catch (error) {
        const errorMessage =
          error.response?.data?.message || error.message || 'Unknown error occurred.';
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'bot', text: `Error: ${errorMessage}` },
        ]);
      }

      setLoading(false);
    }
    setUserMessage('');
  };

  return (
    <div className="chat-container">
      <div className="chat-header"></div>
      <div className="chat-box">
      {messages.map((msg, index) => (
    <div key={index} className={`message ${msg.sender}`}>
      {msg.player ? (
        <PlayerCard
          player={msg.player}
          agentImage={msg.agentImage}
          requestReasoning={msg.requestReasoning}
          playerReasoning={msg.playerReasoning}
        />
      ) : msg.type === 'team_strength' ? ( // Check for team strength type
        <div className="team-strength-box">
          <h4>Team Strength</h4>
          <p>{msg.text}</p> {/* Display the team strength */}
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
