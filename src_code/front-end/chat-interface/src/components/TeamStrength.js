import React from 'react';

const TeamStrength = ({ teamStrengthHTML }) => {
  return (
    <div className="team-strength" dangerouslySetInnerHTML={{ __html: teamStrengthHTML }} />
  );
};

export default TeamStrength;