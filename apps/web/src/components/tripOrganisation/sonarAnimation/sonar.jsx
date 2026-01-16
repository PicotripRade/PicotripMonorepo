import './styles.scss';
import React, { useState, useEffect } from "react";
import mountainPath from "../../../images/destinations/radar/mountain-svgrepo-com.svg";
import waterfallPath from "../../../images/destinations/radar/waterfall-svgrepo-com.svg";
import skiingPath from "../../../images/destinations/radar/skiing.svg";
import snowingPath from "../../../images/destinations/radar/snowing-svgrepo-com.svg";
import summerPath from "../../../images/destinations/radar/summer-cocktail-svgrepo-com.svg";
import forestPath from "../../../images/destinations/radar/circle-forest-svgrepo-com.svg";
import umbrellaPath from "../../../images/destinations/radar/summer-svgrepo-com.svg";

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


                        {/* MOUNTAINS */}
                        {tag === "mountains" && (
                            <>
                                <div className="peak">
                                    <img src={mountainPath} alt="mountain" />
                                </div>

                                <div className="waterfall">
                                    <img src={waterfallPath} alt="waterfall" />
                                </div>

                                <div className="forest">
                                    <img src={forestPath} alt="forest" />
                                </div>
                            </>
                        )}



                        {/* SKIING */}
                        {tag === "skiing" && (
                            <>
                                <div className="peak">
                                    <img src={mountainPath} alt="mountain" />
                                </div>
                                <div className="skiing">
                                    <img src={skiingPath} alt="skiing" />
                                </div>
                                <div className="snowing">
                                    <img src={snowingPath} alt="snowing" />
                                </div>
                            </>
                        )}

                       {tag === "summer_vacation" && (
                           <>
                               <div className="summer">
                                   <img src={summerPath} alt="summer" />
                               </div>

                               <div className="umbrella">
                                   <img src={umbrellaPath} alt="umbrella" />
                               </div>
                           </>
                       )}








                    </div>

                </div>
            </div>
        </div>
    );
};

export default RadarScan;
