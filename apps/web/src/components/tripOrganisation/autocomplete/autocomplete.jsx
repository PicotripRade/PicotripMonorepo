import React, {useState, useEffect, useRef, forwardRef} from 'react';
import './styles.css';
import LocationImage from "@picotrip/shared/assets/images/my-location-svgrepo-com.svg";
import CustomNextButton from "../buttons/customNextButton.jsx";
import {CloseIcon} from "../../utils/reactIcons/icons.jsx";
import LoadingSpinner from "../../utils/loadingSpinner/loadingSpinner.jsx";
import CheckMark from "@picotrip/shared/assets/images/check-mark-svgrepo-com.svg";
import {
    setIsValidSelection,
    setSelectedAirportsList,
} from "@picotrip/shared/src/store/actions/tripOrganisationActions.jsx";
import {useDispatch, useSelector} from "react-redux";
import {sendCoordinates} from "@picotrip/shared/src/utils/geolocation.js";

const Autocomplete = forwardRef(({
                                     startingPoint,
                                     setStartingPoint,
                                     onNextClick,
                                     onOriginChange,
                                     airportList,
                                     xButtonDisplayed
                                 }, ref) => {


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

    const isValidSelection = useSelector((state) => state.tripOrganisation.isValidSelection);
    const expanded = useSelector((state) => state.tripOrganisation.isWhereFromExpanded);
    const [inputValue, setInputValue] = useState(startingPoint || "");

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

    const clearInput = () => {
        setInputValue(''); // Clear the input value
        setStartingPoint?.('')
        setResults([]); // Clear the autocomplete results
        setDropdownVisible(false); // Hide the dropdown
        dispatch(setIsValidSelection(false));
    };

    const handleGetLocation = () => {
        setIsFetchingLocation(true);

        sendCoordinates(
            ({location, originId}) => {
                setInputValue(location);
                dispatch(setIsValidSelection(true));
                setStartingPoint?.(location);
                onOriginChange?.(originId);
            },
            (error) => {
                console.error("Failed to get or send geolocation", error);
            }
        ).finally(() => {
            setIsFetchingLocation(false);
        });
    };

    const onInputChange = (e) => {
        const {value} = e.target;
        setInputValue(value);
        setStartingPoint?.(value);
        dispatch(setIsValidSelection(false));
        setDropdownVisible(true); // Show the dropdown when typing
    };

    const onItemClick = (item) => {
        // Set input value in the format: City, Country, Admin Name
        const startingPointText = `${item.city}, ${item.country}, ${item.admin_name}`;
        setInputValue(startingPointText);
        setStartingPoint?.(startingPointText);
        // Update the parent component with the selected airport code
        // Mark the selection as valid and remove any previous error messages
        dispatch(setIsValidSelection(true));
        // Set originId based on the selected item and pass it upward
        if (onOriginChange) {
            onOriginChange(item.id);
        }

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
                                        onClick={handleGetLocation}
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
