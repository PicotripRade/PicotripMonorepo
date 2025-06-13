import React, {useEffect, useRef} from 'react';

import './styles.css';
import './../../commonStyles.css';

import logoPath from "../../images/header/picotrip.svg";

import {useNavigate} from "react-router-dom";

const Header = ({title}) => {

    const navigate = useNavigate();

    const handleClickOnLogo = () => {
        navigate("/search");
    }

    const logoRef = useRef(null); // Create a ref

    useEffect(() => {
        // This code runs AFTER the component has rendered

        function setColor(id, newColor) {
            const element = document.getElementById(id); // Get element by ID
            if (element) {  // Important check!
                element.style.fill = newColor;
            }
        }

        // Use document.documentElement to access the root element
        const logoColor = getComputedStyle(document.documentElement).getPropertyValue('--element-background').trim();


        setColor('logo1', logoColor);
        setColor('logo2', logoColor);

    }, []); // Empty dependency array ensures this runs only once after mount

    return (
        <header className="header">
            <div className="logo">
                <img src={logoPath} id="logo" ref={logoRef} onClick={handleClickOnLogo}></img>
            </div>
            <div className="page-title"> {title} </div>
        </header>
    );
};

export default Header;
