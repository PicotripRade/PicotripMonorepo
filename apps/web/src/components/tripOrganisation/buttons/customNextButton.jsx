import React, {useState} from "react";
import "./styles.css";
import "./../../../commonStyles.css";

const CustomNextButton = ({onClick, text = "Next", isReady = true, color = "main"}) => {
    const [isPressed, setIsPressed] = useState(false);

    const handleClick = () => {
        setIsPressed(true);
        setTimeout(() => {
            setIsPressed(false);
        }, 300);
        if (isReady) {
            onClick();
        }
    };

    return (
        <div
            className={`button-next rounded-button nav-button-outer ${color === "main" ? "main-color" : ""} ${isReady ? "ready" : ""} ${isPressed ? "pressed" : ""}`}
            onClick={handleClick}
        >
            {text}
        </div>
    );
};

export default CustomNextButton;
