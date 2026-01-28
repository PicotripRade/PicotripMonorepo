import './styles.scss';
import React, { useState, useEffect } from "react";
import mountainPath from "../../../images/destinations/radar/mountain-svgrepo-com.svg";
import waterfallPath from "../../../images/destinations/radar/waterfall-svgrepo-com.svg";
import skiingPath from "../../../images/destinations/radar/skiing.svg";
import snowingPath from "../../../images/destinations/radar/snowing-svgrepo-com.svg";
import summerPath from "../../../images/destinations/radar/summer-cocktail-svgrepo-com.svg";
import forestPath from "../../../images/destinations/radar/circle-forest-svgrepo-com.svg";
import umbrellaPath from "../../../images/destinations/radar/summer-svgrepo-com.svg";
import icePath from "../../../images/destinations/radar/ice-cream-sweet-dairy-ice-cream-svgrepo-com.svg";
import swimmerPath from "../../../images/destinations/radar/swimmer-in-water-waves-under-the-sun-svgrepo-com.svg";
import parkPath from "../../../images/destinations/radar/park-svgrepo-com.svg";
import familyPath from  "../../../images/destinations/radar/family-svgrepo-com.svg";
import babyPath from "../../../images/destinations/radar/baby-stroller-stroller-svgrepo-com.svg";
import hikingPath from "../../../images/destinations/radar/hiking-svgrepo-com.svg";
import bootPath from "../../../images/destinations/radar/hiking-boot-svgrepo-com.svg";
import personPath from "../../../images/destinations/radar/hiking-person-silhouette-with-a-stick-svgrepo-com.svg";
import surfacePath from "../../../images/destinations/radar/surface-water-source-svgrepo-com.svg";
import cavePath from "../../../images/destinations/radar/caving-cave-svgrepo-com.svg";
import undergroundPath from "../../../images/destinations/radar/underground-cave-svgrepo-com.svg";

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

                               <div className="ice">
                                   <img src={icePath} alt="ice cream" />
                               </div>

                               <div className="swimmer">
                                   <img src={swimmerPath} alt="swimmer" />
                               </div>
                           </>
                       )}
                   {tag === "family_trip" && (
                     <>
                       <div className="park">
                         <img src={parkPath} alt="park" />
                       </div>

                       <div className="family">
                         <img src={familyPath} alt="family" />
                       </div>

                       <div className="baby">
                         <img src={babyPath} alt="baby" />
                       </div>
                     </>
                   )}

               {tag === "hiking" && (
                   <>
                       <div className="hiking">
                           <img src={hikingPath} alt="hiking" />
                       </div>

                       <div className="boot">
                           <img src={bootPath} alt="hiking boot" />
                       </div>

                       <div className="person">
                           <img src={personPath} alt="hiking person" />
                       </div>
                   </>
               )}
           {tag === "lakes" && (
               <div className="surface">
                   <img src={surfacePath} alt="surface" />
               </div>
           )}
       {tag === "caving" && (
         <>
           <div className="peak-caving">
             <img src={mountainPath} alt="mountain" />
           </div>

           <div className="cave">
             <img src={cavePath} alt="cave" />
           </div>

           <div className="underground">
             <img src={undergroundPath} alt="underground cave" />
           </div>

           <div className="forest-caving">
             <img src={forestPath} alt="forest" />
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
