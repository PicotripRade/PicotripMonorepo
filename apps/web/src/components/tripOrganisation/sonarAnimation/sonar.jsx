import './styles.scss';
import React, { useState, useEffect } from "react";
import sonarPath from "../../../images/destinations/radar/mountain-svgrepo-com.svg";
import waterfallPath from "../../../images/destinations/radar/waterfall-svgrepo-com.svg";


const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
};

const RadarScan = () => {
    const [tag, setTag] = useState(null);

    useEffect(() => {
        const activityType = getCookie("activityType");
        setTag(activityType);
    }, []);


    return (

        <div className="app">

            <div className="sonar">

                <div className="sonar__container">
                    <div className="distance">
                        <div className="distance__circle"></div>
                        <div className="distance__circle"></div>
                        <div className="distance__circle"></div>
                        <div className="distance__circle"></div>
                        <div className="distance__circle"></div>
                    </div>

                    <div className="matrix"></div>

                    <div className="rotary"></div>

                    <div className="display">
                        <div className="ship-1"></div>
                        <div className="ship-2"></div>
                        <div className="ship-3"></div>
                        <div className="display">
                            {tag === "mountains" && (
                                <>
                                <div className="peak">
                                    <img src={sonarPath} alt="mountain" />

                                </div>
                                <div className="waterfall">
                                                                                   <img src={waterfallPath} alt="waterfall"/>
                                                                               </div>
                                                                               </>

                            )}


                        </div>


                    </div>

                </div>

            </div>

        </div>

    );
};

export default RadarScan;