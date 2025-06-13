import React, { useState } from "react";
import "./styles.css";
import "../../../commonStyles.css";

const PreviousButton = ({ onClick, isReady=true }) => {
  const [isPressed, setIsPressed] = useState(false);

  const handleClick = () => {
    setIsPressed(true);
    setTimeout(() => {
      setIsPressed(false);
    }, 300);
    onClick();
  };

  return (
    <div
      className={`button-previous-outer nav-button-outer rounded-left-button ${isReady ? "ready" : ""} ${isPressed ? "pressed" : ""}`}
      onClick={handleClick}
    >
      <div className={`button-previous-inner nav-button-inner rounded-left-button ${isReady ? "ready" : ""} ${isPressed ? "translate" : ""}`}>
        Previous
      </div>
    </div>
  );
};

export default PreviousButton;
