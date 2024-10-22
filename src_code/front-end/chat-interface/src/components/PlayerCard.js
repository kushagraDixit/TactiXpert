import React, { useState } from 'react';
import './PlayerCard.css';

const PlayerCard = (props) => {
    console.log('Props received by PlayerCard:', props); // Log props to check values
    const { player, agentImage, requestReasoning, playerReasoning } = props;
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const fullName = `${player.player_info.first_name} ${player.player_info.last_name}`;
  const mainRoles = player.main_roles.join(', ');
  const topAgents = player.top_5_agents.slice(0, 3).join(', ');

  const formatNumber = (num) => num.toFixed(2);


  console.log('requestReasoning inside PlayerCard:', requestReasoning);
  console.log('playerReasoning inside PlayerCard:', playerReasoning);
  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  return (
    <div className="player-card-container">
      <div className="player-card">
        {/* Left side (25%) - Display agent image */}
        <div className="left-section">
          <img src={agentImage} alt="Agent" className="agent-image" />
        </div>

        {/* Right side (75%) */}
        <div className="right-section">
          <h2 className="player-handle">{player.player_handle}</h2>
          <p className="player-tagline">{player.assigned_part}</p>

          <div className="divider"></div>

          <p><strong>Name:</strong> {fullName}</p>
          <p><strong>Main Roles:</strong> {mainRoles}</p>
          <p><strong>Competitive Level:</strong> {player.player_type}</p>
          <p><strong>Top Agents:</strong> {topAgents}</p>

          <div className="row">
            <div className="column left-align">
              <p><strong>Team:</strong> {player.team_name} ({player.team_acronym})</p>
            </div>
            <div className="column right-align">
              <p><strong>Region:</strong> {player.player_region}</p>
            </div>
          </div>

          <div className="row">
            <div className="column left-align">
              <p><strong>ACS:</strong> {formatNumber(player.acs)}</p>
            </div>
            <div className="column right-align">
              <p><strong>K/D:</strong> {formatNumber(player.kd)}</p>
            </div>
          </div>

          <div className="row">
            <div className="column left-align">
              <p><strong>Total Kills:</strong> {player.total_kills}</p>
            </div>
            <div className="column right-align">
              <p><strong>Player Score:</strong> {formatNumber(player.all_time_score)}</p>
            </div>
          </div>

          <div className="row">
            <div className="column left-align">
              <p><strong>Games Played:</strong> {player.total_games}</p>
            </div>
            <div className="column right-align">
              <p><strong>Win (%):</strong> {formatNumber(player.win_percentage)}%</p>
            </div>
          </div>

          {/* Dropdown button */}
          <button onClick={toggleDropdown} className="dropdown-btn">
            {isDropdownOpen ? 'Hide Details' : 'Show Details'}
          </button>
        </div>
      </div>

      {/* Dropdown content (spans full width) */}
      {isDropdownOpen && (
        <div className="dropdown-content">
          <h4>Selection Reasoning</h4>
          <p>{requestReasoning}</p>
          <h4>Player Reasoning</h4>
          <p>{playerReasoning}</p>
        </div>
      )}
    </div>
  );
};

export default PlayerCard;
