import React, {useState, useEffect, useRef, forwardRef} from 'react';
import './styles.css';
import Cookies from "js-cookie";
import LocationImage from '../../../images/destinations/my-location-svgrepo-com.svg';
import PostRequest from "../../api/postRequest.jsx";
import CustomNextButton from "../buttons/customNextButton.jsx";
import {CloseIcon} from "../../utils/reactIcons/icons.jsx";
import LoadingSpinner from "../../utils/loadingSpinner/loadingSpinner.jsx";
import CheckMark from '../../../images/destinations/check-mark-svgrepo-com.svg';
import {setSelectedAirportsList} from "@picotrip/shared/src/store/actions/tripOrganisationActions.jsx";
import {useDispatch, useSelector} from "react-redux";

const Autocomplete = forwardRef(({
                                     setIsValidSelection,
                                     isValidSelection,
                                     startingPoint,
                                     setStartingPoint,
                                     expanded,
                                     onNextClick,
                                     onOriginChange,
                                     airportList,
                                     xButtonDisplayed
                                 }, ref) => {

    const [inputValue, setInputValue] = useState(startingPoint);
    const [results, setResults] = useState([]);
    const [dropdownVisible, setDropdownVisible] = useState(false);

    const [isFocused, setIsFocused] = useState(false);
    const debounceTimeout = useRef(null);
    const autocompleteRef = useRef(null);

    const [isFetchingLocation, setIsFetchingLocation] = useState(false);

    const preFilledPlaceholder = "Starting Point";
    const MAX_NUMBER_OF_RESULTS = 10;

    const dispatch = useDispatch();

    const selectedAirports = useSelector((state) => state.tripOrganisation.selectedAirportsList);

    useEffect(() => {
        if (inputValue.length >= 2 && dropdownVisible) {
            if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
            debounceTimeout.current = setTimeout(() => {
                let path;
                if (import.meta.env.VITE_WORKMODE === 'dev') {
                    path = `http://${import.meta.env.VITE_URL}:${import.meta.env.VITE_DJANGO_PORT}/api/autocomplete_airports/?input=${inputValue}`;
                } else {
                    path = `/api/autocomplete_airports/?input=${inputValue}`;
                }
                fetch(path)
                    .then(response => response.json())
                    .then(data => {
                        const formattedResults = data.message.map(item => ({
                            city: item.city,      // Access city correctly
                            country: item.country, // Access country correctly
                            admin_name: item.admin_name,
                            id: item.id
                        }));
                        setResults(formattedResults.slice(0, MAX_NUMBER_OF_RESULTS));
                        setDropdownVisible(true); // Show the dropdown after fetching results
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }, 50);
        } else {
            setResults([]);
            setDropdownVisible(false); // Hide the dropdown if input is less than 2 characters
        }
    }, [inputValue, dropdownVisible]);

    useEffect(() => {
        setInputValue(startingPoint || ''); // Update input when startingPoint changes
    }, [startingPoint]);

    useEffect(() => {
        console.log("selectedAirports", selectedAirports);
    }, [selectedAirports]);

    const clearInput = () => {
        setInputValue(''); // Clear the input value
        setStartingPoint?.('');
        setResults([]); // Clear the autocomplete results
        setDropdownVisible(false); // Hide the dropdown
        setIsValidSelection(false); // Mark the selection as invalid
    };

    const sendCoordinates = () => {
        if (!navigator.geolocation) {
            console.log('Geolocation is not supported by this browser.');
            return;
        }
        setIsFetchingLocation(true); // Start spinner
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const locationData = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    timestamp: new Date().toISOString() // Optional: add timestamp
                };
                // Build string to send
                const readyToSend = `(${locationData.latitude},${locationData.longitude})`;
                const path = 'api/set_geolocation/';

                PostRequest(readyToSend, path, 'json')
                    .then(response => {
                        if (response) {
                            console.log("geolocation set successfully", response);
                            // Assume response.city contains id, city, and country info
                            const cityLocation = `${response.city.city}, ${response.city.country}`;
                            setIsValidSelection(true);
                            setInputValue(cityLocation);
                            setStartingPoint?.(cityLocation);

                            if (onOriginChange) {
                                onOriginChange(response.city.id);
                            }
                        } else {
                            console.error("Unexpected response:", response);
                        }
                    })
                    .catch(error => {
                        console.error("Error sending location:", error);
                    })
                    .finally(() => {
                        setIsFetchingLocation(false); // Stop spinner
                    });
            },
            (err) => {
                console.log("error when getting location: ", err.message);
                setIsFetchingLocation(false);
            }
        );
    };

    const onInputChange = (e) => {
        const {value} = e.target;
        setInputValue(value);
        setStartingPoint?.(value);
        setIsValidSelection(false);
        setDropdownVisible(true); // Show the dropdown when typing
    };

    const onItemClick = (item) => {
        // Set input value in the format: City, Country, Admin Name
        const startingPointText = `${item.city}, ${item.country}, ${item.admin_name}`;
        setInputValue(startingPointText);
        setStartingPoint?.(startingPointText);
        // Update the parent component with the selected airport code
        // Mark the selection as valid and remove any previous error messages
        setIsValidSelection(true);
        // Set originId based on the selected item and pass it upward
        if (onOriginChange) {
            onOriginChange(item.id);
        }
        Cookies.set('startingPoint', startingPointText, {
            sameSite: window.location.protocol === 'https:' ? 'None' : 'Lax',
            secure: window.location.protocol === 'https:',
            path: '/'
        });
        // Clear the autocomplete results and hide the dropdown
        setResults([]);
        setDropdownVisible(false);
    };

    const handleNextClick = () => {
        setDropdownVisible(false); // Hide the dropdown
        if (onNextClick) onNextClick();
    };

    // Determine if the location block should be hidden
    const shouldRemoveLocationBlock = inputValue.length >= 2;

    return (
        <div className={`autocomplete rounded-button bottom-shadow ${expanded ? "expanded" : ""}`}
             ref={autocompleteRef}>
            <div className={`${expanded ? "expanded" : ""}`}>
                <div
                    className={`inner-block ${expanded ? "expanded" : ""} ${xButtonDisplayed ? "decreased-height" : ""}`}>
                    {expanded && (<p className={"input-box-title"}>Where from?</p>)}
                    <div className={`destination-input-field rounded-button ${expanded ? "" : "collapsed"}`}>
                        {!isFocused && !inputValue && (
                            <div className={`placeholder-text ${expanded ? "" : "placeholder-collapsed"}`}>
                                {preFilledPlaceholder}
                            </div>
                        )}
                        {!expanded && <div className={"disabled-text"}>From</div>}
                        <input
                            type="text"
                            value={inputValue}
                            onChange={onInputChange}
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                            required
                            className={` ${inputValue ? '' : 'placeholder-active'} ${expanded ? "rounded-left-button" : "input-collapsed rounded-button"}`}
                            ref={ref}
                        />
                        {/* Conditionally render the location block */}
                        {!shouldRemoveLocationBlock && expanded && (
                            <div className={"location-block rounded-right-button"}>
                                {isFetchingLocation ? (
                                    <LoadingSpinner/>
                                ) : (
                                    <img
                                        src={LocationImage}
                                        alt="Location"
                                        onClick={sendCoordinates}
                                        style={{cursor: 'pointer'}}
                                    />
                                )}
                            </div>
                        )}
                        {shouldRemoveLocationBlock && expanded && (
                            <div onClick={clearInput} className={"location-block rounded-right-button"}
                                 style={{color: "white"}}>
                                <CloseIcon/>
                            </div>
                        )}
                    </div>
                    {dropdownVisible && results.length > 0 && (
                        <ul className="autocomplete-results">
                            {results.map((result, index) => (
                                <li
                                    key={index}
                                    className={`autocomplete-item ${index === results.length - 1 ? 'last' : ''} ${index === 0 ? 'first' : ''}`}
                                    onClick={() => onItemClick(result)}
                                >
                                    <span className="name">
                                        {result.city}, {result.country}, {result.admin_name}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    )}
                    {expanded && isValidSelection && airportList.length > 0 && (
                        <div className={"airports-selection-wrapper"}>
                            <div className={"section-title"}>
                                Flying out? Choose your nearby airports and we will show where you can go direct.
                            </div>
                            <div className="airport-checkbox-list">
                                {airportList.map((airport) => {
                                    const isSelected = selectedAirports.includes(airport.iata_code);
                                    return (
                                        <div
                                            key={airport.iata_code}
                                            className={`airport-button ${isSelected ? 'selected bottom-shadow' : ''}`}
                                            onClick={() => {
                                                const isSelected = selectedAirports.includes(airport.iata_code);
                                                const updatedList = isSelected
                                                    ? selectedAirports.filter(code => code !== airport.iata_code)
                                                    : [...selectedAirports, airport.iata_code];

                                                dispatch(setSelectedAirportsList(updatedList));
                                            }}
                                        >
                                            <div className={"airport-text-wrapper"}>
                                                <div className="iata-code">{airport.iata_code}</div>
                                                <div className={"city-and-country"}>
                                                    <div className="city-name">{airport.name},&nbsp;</div>
                                                    <div className="country-name">{airport.iso_country}</div>
                                                </div>
                                            </div>
                                            <div className={"empty-space"}></div>
                                            <div className={`checkbox ${isSelected ? '' : 'hidden'}`}>
                                                {isSelected && <img
                                                    src={CheckMark}
                                                    alt="checkmark"
                                                    style={{cursor: 'pointer'}}
                                                />
                                                }
                                            </div>


                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                    {expanded && (<div className={"empty-space"}></div>)}
                    {expanded && (
                        <div className={"input-navigation"}>
                            <CustomNextButton onClick={handleNextClick} isReady={isValidSelection}/>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
});

export default Autocomplete;
