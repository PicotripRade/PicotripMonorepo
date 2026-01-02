import './styles.scss';
import React from "react";
import sonarPath from "../../../images/destinations/radar/mountain-svgrepo-com.svg";




const RadarScan = () => {

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

                    {/*<div className="degree">*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*    <div className="degree__line"></div>*/}
                    {/*</div>*/}

                    <div className="matrix"></div>

                    <div className="rotary"></div>

                    <div className="display">
                        <div className="ship-1"></div>
                        <div className="ship-2"></div>
                        <div className="ship-3"></div>
                        <div className="peak">
                            <svg viewBox="0 0 800 800" width="25" height="25"> src={sonarPath} </svg>
                        </div>

                    </div>

                </div>

            </div>

        </div>

);
};

export default RadarScan;