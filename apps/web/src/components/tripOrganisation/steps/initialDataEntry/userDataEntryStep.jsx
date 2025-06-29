import React, {useState, useRef, useEffect} from "react";
import {useNavigate, useLocation} from "react-router-dom";
import Autocomplete from "../../autocomplete/autocomplete.jsx";
import "./styles.css";
import "../styles.css";
import "../../../../commonStyles.css";
import CustomCalendar from "../../datepicker/datepicker.jsx";
import Header from "../../../header/header.jsx";
import SearchResults from "../../searchResults/searchResults.jsx";
import TagSelection from "../setActivityTag/typeOfTravelStep.jsx";

import FilterResults from '../../../../images/destinations/filters-2-svgrepo-com.svg';
import ArrowBack from '../../../../images/destinations/left-navigation-back-svgrepo-com.svg';
import {CloseIcon} from "../../../utils/reactIcons/icons.jsx";
import Cookies from "js-cookie";

import {useDispatch, useSelector} from "react-redux";
import {addCityInfo} from "@picotrip/shared/src/store/actions/CityInformationActions.jsx";
import {
    setAirportsList, setArrowBackPressed,
    setSelectedAirportsList,
    setTag
} from "@picotrip/shared/src/store/actions/tripOrganisationActions.jsx";
import CustomButton from "../../buttons/customButton.jsx";
import {
    fetchUserLocation,
    formatDateToNumbersAndLetters, formatDisplayDate,
    getTagDescription,
    saveTripInfo
} from "@picotrip/shared";
import GetRequest from "@picotrip/shared/src/api/getRequest.js";
import getTripsInfo from "@picotrip/shared/src/api/getTripsInformation.js";

function UserDataEntryStep() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const location = useLocation();

    const [autocompleteKey, setAutocompleteKey] = useState(0);
    const [isValidSelection, setIsValidSelection] = useState(false);
    const [whereFromExpanded, setWhereFromExpanded] = useState(true);
    const [calendarOpen, setCalendarOpen] = useState(false);
    const [tagsExpanded, setTagsExpanded] = useState(false);
    const [searchResultsReady, setSearchResultsReady] = useState(false);
    const [searchResultsDisplayed, setSearchResultsDisplayed] = useState(false);
    const [inputFieldsCollapsed, setInputFieldsCollapsed] = useState(false);
    const startDate = useSelector((state) => state.tripOrganisation.startDate);
    const endDate = useSelector((state) => state.tripOrganisation.endDate);

    const errorMessageAirportRef = useRef(null);
    const autocompleteRef = useRef(null);
    const calendarRef = useRef(null);
    const tagContainerRef = useRef(null);

    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingCityData, setIsLoadingCityData] = useState(false);
    const [originId, setOriginId] = useState('') || Cookies.get("geoname");
    const [startingPoint, setStartingPoint] = useState('');

    const [responseData, setResponseData] = useState(null);
    const [responseCityData, setResponseCityData] = useState(null);
    const [errorResponse, setErrorResponse] = useState(false);

    const arrowBackPressed = useSelector((state) => state.tripOrganisation.arrowBackPressed);
    const selectedTag = useSelector((state) => state.tripOrganisation.tag);
    const airportsListRedux = useSelector((state) => state.tripOrganisation.airportList);
    const selectedAirportsListRedux = useSelector((state) => state.tripOrganisation.selectedAirportsList);

    const [allTypes, setAllTypes] = useState(1);

    const arrowBackPressedRef = useRef(arrowBackPressed);

    const dataPerCityRedux = useSelector((state) => state.cityInfoReducer.cities) || '';

    useEffect(() => {
        arrowBackPressedRef.current = arrowBackPressed;
    }, [arrowBackPressed]);

    // useEffect(() => {
    //     setStartingPoint(startingPoint)
    // }, [startingPoint]);


    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const from = params.get("from");
        const begin = params.get("begin");
        const end = params.get("end");
        const tag = params.get("activityType");

        if (from && begin && end) {
            setOriginId(from);
            Cookies.set("geoname", from);
            if (tag) dispatch(setTag(tag));

            handleSearchClick({
                overrideParams: {
                    from,
                    begin,
                    end,
                    tag
                },
                skipUpdateURL: true,
            });
        }
    }, []);

    useEffect(() => {
        const fetchLocation = async () => {
            const {city, country, id} = await fetchUserLocation();
            const response_formatted = `${city}, ${country}`;

            console.log("response_formatted", JSON.stringify(response_formatted));
            setOriginId(id);
            setIsValidSelection(true);
            setStartingPoint(response_formatted);
            fetchAirports(id);
        };

        fetchLocation();
    }, []);

    useEffect(() => {
        if (!originId || !isValidSelection) return;
        fetchAirports(originId);
    }, [originId, isValidSelection]);

    useEffect(() => {
        const handleClick = (event) => {
            if (autocompleteRef.current?.contains(event.target)) {
                setWhereFromExpanded(true);
                setCalendarOpen(false);
                setTagsExpanded(false);
            } else if (calendarRef.current?.contains(event.target)) {
                setWhereFromExpanded(false);
                setCalendarOpen(true);
                setTagsExpanded(false);
            } else if (tagContainerRef.current?.contains(event.target)) {
                setWhereFromExpanded(false);
                setCalendarOpen(false);
                setTagsExpanded(true);
            }
        };

        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, [isValidSelection]);


    const fetchAirports = async (originId) => {
        console.log("fetch airports function")
        try {
            const airports_list = await GetRequest(`/api/get_airports_list/?city_id=${originId}`);
            dispatch(setAirportsList(airports_list));
            dispatch(setSelectedAirportsList(airports_list.map(a => a.iata_code)));

            setAutocompleteKey(prev => prev + 1); // Force re-render
        } catch (error) {
            console.error('Failed to fetch airports list:', error);
        }
    };

    const handleSearchClick = async ({overrideParams = null, skipUpdateURL = false} = {}) => {
        try {
            setErrorResponse(false); // Reset error state on new search
            setTagsExpanded(false);
            dispatch(setArrowBackPressed(false));

            const beginDate = overrideParams?.begin || formatDateToNumbersAndLetters(startDate);
            const finalDate = overrideParams?.end || formatDateToNumbersAndLetters(endDate);
            const from = overrideParams?.from || originId;
            const tag = overrideParams?.tag || selectedTag || '';

            // Save to cookies
            dispatch(setSelectedAirportsList(selectedAirportsListRedux));
            dispatch(setAirportsList(airportsListRedux));
            saveTripInfo({startingPoint, beginDate, finalDate});

            if (!skipUpdateURL) {
                navigate(`?from=${from}&begin=${beginDate}&end=${finalDate}&activityType=${tag}`, {
                    replace: true
                });
            }

            setIsLoading(true);

            const data = await getTripsInfo({
                from,
                beginDate,
                finalDate,
                tag,
                selectedAirports: selectedAirportsListRedux
            });

            if (!arrowBackPressedRef.current) {
                setSearchResultsReady(true);
                setSearchResultsDisplayed(true);
                setInputFieldsCollapsed(true);
                setResponseData(data);
            }
            if (data.error === "Internal server error") {
                console.log("there was a 500 error");
                setErrorResponse(true);
            }

            return data;
        } catch (error) {
            console.error('Search failed:', error);
            setErrorResponse(true);
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const handleCitySelect = async ({geonameid, transportType, cityName, countryName}) => {

        const beginDate = formatDateToNumbersAndLetters(startDate);
        const finalDate = formatDateToNumbersAndLetters(endDate);
        const from = originId;
        const tag = selectedTag || '';

        if (!geonameid) {
            console.log("No city id set!!!");
            return;
        }

        // Check if data for this geonameid is already in Redux
        if (Object.prototype.hasOwnProperty.call(dataPerCityRedux, geonameid)) {
            console.log("Using cached city data from Redux for geonameid:", geonameid);
            setResponseCityData(dataPerCityRedux[geonameid].info);
            return;
        }

        // Fetch from API if not found in Redux
        try {
            setIsLoadingCityData(true);
            const city_response = await GetRequest(
                `/api/get_city_info?from=${from}&begin=${beginDate}&end=${finalDate}&activityType=${tag}` +
                `&selectedAirports=${selectedAirportsListRedux.join(',')}&geoname=${geonameid}&transportType=${transportType}` +
                `&cityName=${encodeURIComponent(cityName)}&countryName=${encodeURIComponent(countryName)}`
            );

            console.log("Fetched city data from API:", city_response);
            setIsLoadingCityData(false);
            setResponseCityData(city_response);

            dispatch(addCityInfo(geonameid, {
                cityName: cityName,
                transportType: transportType,
                info: city_response,
            }));
        } catch (error) {
            console.error("Failed to fetch city data:", error);
        }
    };

    const resetAutocompleteParameters = () => {
        const startingPoint = Cookies.get("startingPoint") || "";
        setStartingPoint(startingPoint);

        setAutocompleteKey(autocompleteKey + 1);
    };

    const resetToInitialState = () => {
        dispatch(setArrowBackPressed(true));
        setIsValidSelection(true);
        setWhereFromExpanded(true);
        setCalendarOpen(false);
        setTagsExpanded(false);
        setSearchResultsReady(false);
        setSearchResultsDisplayed(false);
        setInputFieldsCollapsed(false);
        setIsLoading(false);
        setResponseData(null);
        setAllTypes(1);
        setErrorResponse(false);
        setAutocompleteKey(autocompleteKey + 1)
        window.history.replaceState(null, '', location.pathname);
        resetAutocompleteParameters();
    };

    return (
        <div className={"full-content-wrapper"}>
            <div id={"container"} className="form-inline-wrapper user-entry-length">
                {errorResponse ? (
                    <div className="error-message-container">
                        <h2>Something went wrong</h2>
                        <p>We couldn't complete your search. Please try again.</p>
                        <CustomButton
                            onClick={() => {
                                resetToInitialState();
                            }}
                            label={"Search Again"}></CustomButton>
                    </div>
                ) : (
                    <>
                        {(!inputFieldsCollapsed && !isLoading) && (
                            <div className={"user-entry-container"}>
                                {!searchResultsDisplayed && searchResultsReady && (
                                    <div
                                        className={"x-button-results"}
                                        style={{color: "black"}}
                                        onClick={() => {
                                            setSearchResultsDisplayed(true);
                                            setInputFieldsCollapsed(true);
                                            resetAutocompleteParameters();
                                        }}
                                    >
                                        <CloseIcon/>
                                    </div>
                                )}

                                <div id={"autocomplete"} className={"autocomplete-wrapper"} ref={autocompleteRef}>
                                    {originId && (
                                        <Autocomplete
                                            startingPoint={startingPoint}
                                            setStartingPoint={setStartingPoint}
                                            key={autocompleteKey}
                                            ref={errorMessageAirportRef}
                                            setIsValidSelection={setIsValidSelection}
                                            isValidSelection={isValidSelection}
                                            expanded={whereFromExpanded}
                                            onNextClick={() => {
                                                setCalendarOpen(true);
                                                setWhereFromExpanded(false);
                                            }}
                                            onOriginChange={(newDestId) => setOriginId(newDestId)}
                                            airportList={airportsListRedux}
                                            xButtonDisplayed={!searchResultsDisplayed && searchResultsReady}
                                        />
                                    )}
                                </div>

                                {!whereFromExpanded && (
                                    <div id={"datepicker"} className={"datepicker-wrapper"} ref={calendarRef}>
                                        <CustomCalendar
                                            isOpen={calendarOpen}
                                            onClose={() => {
                                                setCalendarOpen(false);
                                                setTagsExpanded(true);
                                            }}
                                            onMonthSelection={() => {
                                            }}
                                        />

                                    </div>
                                )}
                                {!whereFromExpanded && !calendarOpen && (
                                    <div id={"tag-selection"} ref={tagContainerRef}>
                                        <TagSelection
                                            tagsExpanded={tagsExpanded}
                                            onSearchClick={() => handleSearchClick()}
                                        />
                                    </div>
                                )}
                            </div>
                        )}
                        {(inputFieldsCollapsed || isLoading) && (
                            <div className={"user-entry-container"}>
                                <div className={"collapsed-input-wrapper"}>
                                    <div className={"back-arrow-results"} onClick={resetToInitialState}>
                                        <img src={ArrowBack} alt="Back to Search"/>
                                    </div>
                                    <div
                                        className={"collapsed-input strong-shadow"}
                                        onClick={() => {
                                            setInputFieldsCollapsed(false);
                                            setWhereFromExpanded(true);
                                            setCalendarOpen(false);
                                            setTagsExpanded(false);
                                            setSearchResultsDisplayed(false);
                                            resetAutocompleteParameters();
                                        }}
                                    >
                                        {(() => {
                                            const dateDisplay = formatDisplayDate(startDate, endDate);
                                            return (
                                                <>
                                                    <div className={"activity-name-collapsed"}>
                                                        {getTagDescription(selectedTag)}
                                                    </div>
                                                    <div className={"time-range-collapsed"}>
                                                        {dateDisplay.start} {dateDisplay.end ? '-' : ''} {dateDisplay.end}
                                                    </div>
                                                </>
                                            );
                                        })()}
                                    </div>
                                    <div className={"filter-results"}>
                                        <img src={FilterResults} alt="Filter Results"/>
                                    </div>
                                </div>
                            </div>
                        )}
                        <>
                            {searchResultsReady && searchResultsDisplayed && (
                                <div className={"travel-type-selection"}>
                                    <div
                                        className={`all-types ${allTypes === 1 ? "selected" : ""}`}
                                        onClick={() => {
                                            setAllTypes(1);
                                        }}
                                    >
                                        <div>Top</div>
                                    </div>
                                    {responseData?.results?.flight !== "no results" && (
                                        <div
                                            className={`by-plane ${allTypes === 2 ? "selected" : ""}`}
                                            onClick={() => {
                                                setAllTypes(2);
                                            }}
                                        >
                                            <div>Flights</div>
                                        </div>
                                    )}
                                    <div
                                        className={`by-car ${allTypes === 3 ? "selected" : ""}`}
                                        onClick={() => {
                                            setAllTypes(3);
                                        }}
                                    >
                                        <div>Car</div>
                                    </div>
                                </div>
                            )}
                            <div className={"results-container"}>
                                <SearchResults
                                    loading={isLoading}
                                    ready={searchResultsReady && searchResultsDisplayed}
                                    data={responseData}
                                    typeToDisplay={allTypes}
                                    onCitySelect={handleCitySelect}
                                    cityInfo={responseCityData}
                                    isLoadingCityData={isLoadingCityData}
                                />
                            </div>
                        </>
                    </>
                )}
            </div>
        </div>
    );
}

export default UserDataEntryStep;