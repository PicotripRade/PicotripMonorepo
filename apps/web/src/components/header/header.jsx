import React, {useEffect, useRef} from 'react';
import './styles.css';
import './../../commonStyles.css';
import logoPath from "../../images/header/picotrip.svg";
import {useNavigate} from "react-router-dom";
import {setColor} from "@picotrip/shared";
import LanguageSwitcher from "../../functions/LanguageSwitcher.jsx";


const Header = ({title}) => {
    const navigate = useNavigate();
    const logoRef = useRef(null);

    const handleClickOnLogo = () => {
        navigate("/search");
    }

    useEffect(() => {
        const logoColor = getComputedStyle(document.documentElement).getPropertyValue('--element-background').trim();
        setColor('logo1', logoColor);
        setColor('logo2', logoColor);
    }, []);

    return (
        <header className="header">
            <div className="logo">
                <img src={logoPath} id="logo" ref={logoRef} onClick={handleClickOnLogo} alt="PicoTrip Logo"></img>
            </div>
            <div className="page-title"> {title} </div>
            <div className="header-right">
                <LanguageSwitcher />
            </div>
        </header>
    );
};

export default Header;