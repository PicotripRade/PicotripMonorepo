import React, {useState} from "react";
import "./styles.css";

const NextButton = ({onClick, text="Next", isReady=true}) => {
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
            className={`button-next-outer nav-button-outer rounded-right-button ${isReady ? "ready" : ""} ${isPressed ? "pressed" : ""}`}
            onClick={handleClick}
        >
            <div className={`button-next-inner nav-button-inner rounded-right-button ${isReady ? "ready" : ""} ${isPressed ? "translate" : ""}`}>
                {text}
            </div>
        </div>
    );
};

export default NextButton;