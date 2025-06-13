import React, { useState } from "react";
import "./styles.css";

const CustomButton = ({ onClick, label }) => {
  const [isPressed, setIsPressed] = useState(false);

  const isReady = label==="Done";
  const handleClick = () => {
    setIsPressed(true);
    setTimeout(() => {
      setIsPressed(false);
    }, 300);
    onClick();
  };

  return (
    <div
      className={`button-done-outer nav-button-outer main-color rounded-button ${isReady ? "ready" : ""} ${isPressed ? "pressed" : ""}`}
      onClick={handleClick}
    >
        {label}
    </div>
  );
};

export default CustomButton;