import React, {useState, useEffect} from "react";
import "./styles.css";
import RadarScan from "../sonarAnimation/sonar.jsx";
import PlaneIcon from '../../../images/destinations/plane.svg';
import CarIcon from '../../../images/destinations/car-taxi-front.svg';
import Paris from '../../../images/mock/paris.jpg';
import FlightSegment from "./flightSegment.jsx";
import Cookies from "js-cookie";
import {useDispatch} from "react-redux";
import {setSelectedCityRedux} from "../../../store/store/actions/CityInformationActions.jsx";
import {formatDateToMonthDayYear, getCountryName, removeTextInBrackets} from "@picotrip/shared";

const SearchResults = ({loading, ready, data, typeToDisplay, onCitySelect, cityInfo, isLoadingCityData}) => {
    const SENTENCE_TIME_MILLISECONDS = 3000;
    const DOTS_TIME_MILLISECONDS = 500;

    const dispatch = useDispatch();

    const loadingSentences = [
        "Analyzing 5000+ destinations",
        "Finding flights",
        "Calculating routes",
        "Optimizing offers"
    ];

    const [loadingIndex, setLoadingIndex] = useState(0);
    const [dotCount, setDotCount] = useState(0);
    const [selectedCity, setSelectedCity] = useState(null);

    const startDate = Cookies.get('beginDate') || '';
    const finalDate = Cookies.get('finalDate') || '';

    useEffect(() => {
        if (loading) {
            const sentenceInterval = setInterval(() => {
                setLoadingIndex((prevIndex) => (prevIndex + 1) % loadingSentences.length);
            }, SENTENCE_TIME_MILLISECONDS);
            return () => clearInterval(sentenceInterval);
        } else {
            setLoadingIndex(0);
        }
    }, [loading]);

    useEffect(() => {
        if (loading) {
            const dotInterval = setInterval(() => {
                setDotCount((prevCount) => (prevCount + 1) % 4);
            }, DOTS_TIME_MILLISECONDS);
            return () => clearInterval(dotInterval);
        } else {
            setDotCount(0);
        }
    }, [loading]);

    const getTransportIcon = (travelType) => {
        if (travelType === "car") return CarIcon;
        return PlaneIcon;
    };

    const typeMap = {
        1: 'top',
        2: 'flight',
        3: 'car'
    };

    let filteredData = [];

    if (data && data.results) {
        const selectedType = typeMap[typeToDisplay] || 'top';
        const rawData = data.results[selectedType];
        if (selectedType === 'flight') {
            filteredData = rawData.filter(city => city.transport === 'direct');
        } else {
            console.log("no direct flights");
        }
        filteredData = Array.isArray(rawData) ? rawData : [];
    }

    const handleTeaserClick = (city) => {
        setSelectedCity(city);
        dispatch(setSelectedCityRedux(city.geonameid));
        document.body.style.overflow = 'hidden'; // Prevent background scroll
        console.log("city data", city);
        onCitySelect({
            geonameid: city.geonameid,
            transportType: city.transport,
            cityName: city.name,
            countryName: getCountryName(city.country_code)
        });
    };

    const closeModal = () => {
        setSelectedCity(null);
        document.body.style.overflow = 'auto';
    };

    if (loading) {
        return (
            <div className="results-wrapper">
                <RadarScan/>
                <p className="loading-text">
                    {loadingSentences[loadingIndex]}
                    {".".repeat(dotCount)}
                </p>
            </div>
        );
    }


    if (ready) {
        return (
            <div className="results-wrapper">
                <div className={`scrollable-wrapper scroll`}>
                    {filteredData.length > 0 ? filteredData.map((city) => (
                        <div key={city.geonameid} className="city-teaser strong-shadow"
                             onClick={() => handleTeaserClick(city)}>
                            <div className={"city-image"}>
                                <img src={Paris}></img>
                            </div>
                            <div className={"description"}>
                                <div className={"main-desc"}>
                                    <div className="left-info">
                                        <div className="city-name-teaser">{city.name}</div>
                                        <div className="country-name-teaser">{getCountryName(city.country_code)}</div>
                                    </div>
                                    <div className="empty-space"></div>
                                    <div className="right-info">
                                        <div className={"transport-details"}>
                                            {city.transport === "direct" && (
                                                <>
                                                    <div className={"flight-teaser to-dest"}>
                                                        <span className={"teaser-flight-label"}>from</span>
                                                        <span
                                                            className="departure">{city.departures[0].departure}</span>
                                                        &nbsp;
                                                        <span className={"teaser-flight-label"}>via</span>
                                                        <span
                                                            className="departure">{removeTextInBrackets(city.departures[0]["airline:"])}</span>
                                                    </div>

                                                </>
                                            )}
                                        </div>
                                        <div className={"empty-space"}></div>
                                        <div className="transport-type">
                                            {city.transport === "direct" && (
                                                <span className="transport-label">Direct</span>
                                            )}
                                            <img src={getTransportIcon(city.transport)} alt={city.transport}
                                                 className="transport-icon"/>
                                        </div>
                                    </div>
                                </div>
                                <div className={"footer-desc"}>
                                    {/* Summer Vacation */}
                                    {city.BCH_no_h6_1 > 0 && (
                                        <div
                                            className={"beaches-count"}>{`BCH ${city.BCH_no_h6_1}`}
                                        </div>)}
                                    {city.BAY_no_h6_1 > 0 && (
                                        <div
                                            className={"bay-count"}>{`BAY ${city.BAY_no_h6_1}`}
                                        </div>)}
                                    {city.COVE_no_h6_1 > 0 && (
                                        <div
                                            className={"cove-count"}>{`COVE ${city.COVE_no_h6_1}`}
                                        </div>)}
                                    {city.LGN_no_h6_1 > 0 && (
                                        <div
                                            className={"lagoon-count"}>{`LAGOON ${city.LGN_no_h6_1}`}
                                        </div>)}
                                    {city.GULF_no_h6_1 > 0 && (
                                        <div
                                            className={"gulf-count"}>{`GULF ${city.GULF_no_h6_1}`}
                                        </div>)}
                                    {/* Mountains */}
                                    {city.PK_no_h5_1 > 0 && (
                                        <div
                                            className={"peaks-count"}>{`PEAKS ${city.PK_no_h5_1}`}
                                        </div>)}
                                    {city.MT_no_h5_1 > 0 && (
                                        <div
                                            className={"mountains-count"}>{`MOUNTAINS ${city.MT_no_h5_1}`}
                                        </div>)}
                                </div>
                            </div>
                        </div>
                    )) : ready && <p>No results found.</p>}
                </div>

                {/* Modal popup */}
                {selectedCity && (
                    <div className="modal-overlay" onClick={closeModal}>
                        <div
                            className={`modal-content`}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className={"modal-header"}>
                                <button className="close-button" onClick={closeModal}>×</button>
                                <h2>{selectedCity.name}</h2>
                                <div className={"country-name-modal"}>{getCountryName(selectedCity.country_code)}</div>
                            </div>
                            <div className={"modal-content-inner"}>
                                <div className="ai-city-info">
                                    {isLoadingCityData && (<div className={"radar-on-city-info"}><RadarScan/></div>)}
                                    {cityInfo?.what_attraction_to_visit_regarding_activity && !isLoadingCityData && (
                                        <>
                                            <h3>Must See</h3>
                                            <ul className="attractions-list">
                                                {cityInfo.what_attraction_to_visit_regarding_activity.map((attraction, idx) => (
                                                    <li key={idx} className="attraction-item">
                                                        - <strong>{attraction}</strong>
                                                    </li>
                                                ))}
                                            </ul>
                                        </>
                                    )}
                                    {cityInfo?.what_is_best_to_do_on_chosen_dates && !isLoadingCityData && (
                                        <>
                                            <h3>Recommendations</h3>
                                            <ul className="daily-plan-list">
                                                {Object.entries(cityInfo.what_is_best_to_do_on_chosen_dates).map(([date, activity]) => (
                                                    <li key={date}>
                                                        <b className={"date-font"}>{formatDateToMonthDayYear(date)}</b>
                                                        <div className={"activity-text"}>{activity}</div>
                                                    </li>
                                                ))}
                                            </ul>
                                        </>
                                    )}
                                </div>
                                {["direct", "non_direct"].includes(selectedCity.transport) && (
                                    <div className="modal-transport">

                                        <div className={"flight-info-wrapper"}>
                                            <div className={"title-section"}>
                                                <div className={"title-text"}>
                                                    Flights to
                                                    Destination
                                                </div>

                                                <div className={"flight-date"}>
                                                    {formatDateToMonthDayYear(startDate)}
                                                </div>
                                            </div>
                                            <div className={"flights-information"}>
                                                {Array.from({
                                                    length: Math.max(
                                                        selectedCity.departures?.length || 0,
                                                    )
                                                }).map((_, index) => (
                                                    <FlightSegment
                                                        key={index}
                                                        segment={selectedCity.departures?.[index]}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                        <div className={"flight-info-wrapper"}>
                                            <div className={"title-section"}>
                                                <div className={"title-text"}>
                                                    Return Flights
                                                </div>
                                                <div className={"flight-date"}>
                                                    {formatDateToMonthDayYear(finalDate)}
                                                </div>
                                            </div>
                                            <div className={"flights-information"}>
                                                {Array.from({
                                                    length: Math.max(
                                                        selectedCity.arrivals?.length || 0,
                                                    )
                                                }).map((_, index) => (
                                                    <FlightSegment
                                                        key={index}
                                                        segment={selectedCity.arrivals?.[index]}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    }
};

export default SearchResults;
