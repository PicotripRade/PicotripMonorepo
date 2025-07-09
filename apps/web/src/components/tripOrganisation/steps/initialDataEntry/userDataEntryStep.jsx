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
import {addCityInfo} from "@picotrip/shared/src/store/actions/cityInformationActions.jsx";
import {
    setAirportsList, setArrowBackPressed, setCalendarOpen, setIsValidSelection,
    setSelectedAirportsList, setTagsExpanded, setWhereFromExpanded
} from "@picotrip/shared/src/store/actions/tripOrganisationActions.jsx";
import CustomButton from "../../buttons/customButton.jsx";
import {
    fetchAirports,
    fetchUserLocation,
    formatDateToNumbersAndLetters, formatDisplayDate, handleCitySelect,
    getTagDescription
} from "@picotrip/shared";

import {
    setSearchResultsDisplayed,
    setSearchResultsReady
} from "@picotrip/shared/src/store/actions/searchResultsActions.jsx";
import {handleSearchClick} from "@picotrip/shared/src/utils/handleSearchClick.js";

function UserDataEntryStep() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const location = useLocation();

    const [autocompleteKey, setAutocompleteKey] = useState(0);

    const [inputFieldsCollapsed, setInputFieldsCollapsed] = useState(false);
    const startDate = useSelector((state) => state.tripOrganisation.startDate);
    const endDate = useSelector((state) => state.tripOrganisation.endDate);

    const isValidSelection = useSelector((state) => state.tripOrganisation.isValidSelection);
    const whereFromExpanded = useSelector((state) => state.tripOrganisation.isWhereFromExpanded);
    const calendarOpen = useSelector((state) => state.tripOrganisation.isCalendarOpen);

    const errorMessageAirportRef = useRef(null);
    const autocompleteRef = useRef(null);
    const calendarRef = useRef(null);
    const tagContainerRef = useRef(null);

    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingCityData, setIsLoadingCityData] = useState(false);
    const [originId, setOriginId] = useState('') || Cookies.get("geoname");
    const [startingPoint, setStartingPoint] = useState('');
    const [selectedTag, setSelectedTag] = useState('');

    const [responseData, setResponseData] = useState(null);
    const [responseCityData, setResponseCityData] = useState(null);
    const [errorResponse, setErrorResponse] = useState(false);

    const arrowBackPressed = useSelector((state) => state.tripOrganisation.arrowBackPressed);

    const airportsListRedux = useSelector((state) => state.tripOrganisation.airportList);
    const selectedAirportsListRedux = useSelector((state) => state.tripOrganisation.selectedAirportsList);

    const searchResultsReady = useSelector((state) => state.searchResults.setSearchResultsReady);
    const searchResultsDisplayed = useSelector((state) => state.searchResults.setSearchResultsDisplayed);

    const [allTypes, setAllTypes] = useState(1);

    const arrowBackPressedRef = useRef(arrowBackPressed);

    const dataPerCityRedux = useSelector((state) => state.cityInfoReducer.cities) || '';

    useEffect(() => {
        arrowBackPressedRef.current = arrowBackPressed;
    }, [arrowBackPressed]);

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const from = params.get("from");
        const begin = params.get("begin");
        const end = params.get("end");
        const tag = params.get("activityType");

        if (from && begin && end) {
            setOriginId(from);
            Cookies.set("geoname", from);

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
            dispatch(setIsValidSelection(true));
            setStartingPoint(response_formatted);


            fetchAirports({
                id,
                dispatch,
                setAutocompleteKey,
            });
        };

        fetchLocation();
    }, []);

    useEffect(() => {
        if (!originId || !isValidSelection) return;
        fetchAirports({
            originId,
            dispatch,
            setAutocompleteKey,
        });
    }, [originId, isValidSelection]);

    useEffect(() => {
        const handleClick = (event) => {
            if (autocompleteRef.current?.contains(event.target)) {
                dispatch(setWhereFromExpanded(true));
                dispatch(setCalendarOpen(false));
                dispatch(setTagsExpanded(false));

            } else if (calendarRef.current?.contains(event.target)) {
                dispatch(setWhereFromExpanded(false));
                dispatch(setCalendarOpen(true));
                dispatch(setTagsExpanded(false));

            } else if (tagContainerRef.current?.contains(event.target)) {
                dispatch(setWhereFromExpanded(false));
                dispatch(setCalendarOpen(false));
                dispatch(setTagsExpanded(true));
            }
        };

        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, [isValidSelection]);


    const onSearchClick = () => {
        handleSearchClick({
            overrideParams: null,
            skipUpdateURL: false,
            startDate,
            endDate,
            originId,
            selectedTag,
            selectedAirportsList: selectedAirportsListRedux,
            airportsList: airportsListRedux,
            startingPoint,
            dispatch,
            arrowBackPressedRef,
            navigate,
            setSearchResultsDisplayed,
            setSearchResultsReady,
            setErrorResponse,
            setInputFieldsCollapsed,
            setIsLoading,
            setResponseData,
            setTagsExpanded,
            setArrowBackPressedAction: setArrowBackPressed,
            setAirportsListAction: setAirportsList,
            setSelectedAirportsListAction: setSelectedAirportsList
        });
    };

    const onCitySelect = async (params) => {
        await handleCitySelect({
            ...params,
            from: originId,
            beginDate: formatDateToNumbersAndLetters(startDate),
            finalDate: formatDateToNumbersAndLetters(endDate),
            tag: selectedTag || '',
            selectedAirportsList: selectedAirportsListRedux,
            dataPerCity: dataPerCityRedux,
            dispatch,
            setIsLoadingCityData,
            setResponseCityData,
            addCityInfoAction: addCityInfo,
        });
    };

    const resetAutocompleteParameters = () => {
        const startingPoint = Cookies.get("startingPoint") || "";
        setStartingPoint(startingPoint);

        setAutocompleteKey(autocompleteKey + 1);
    };

    const resetToInitialState = () => {
        dispatch(setArrowBackPressed(true));
        dispatch(setIsValidSelection(true));
        dispatch(setWhereFromExpanded(true));
        dispatch(setCalendarOpen(false));
        dispatch(setTagsExpanded(false));
        dispatch(setSearchResultsReady(false));
        dispatch(setSearchResultsDisplayed(false));
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
                                            dispatch(setSearchResultsDisplayed(true))
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
                                            onNextClick={() => {
                                                dispatch(setCalendarOpen(true));
                                                dispatch(setWhereFromExpanded(false));
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
                                            onClose={() => {
                                                dispatch(setCalendarOpen(false));
                                                dispatch(setTagsExpanded(true));
                                            }}
                                            onMonthSelection={() => {
                                            }}
                                        />

                                    </div>
                                )}
                                {!whereFromExpanded && !calendarOpen && (
                                    <div id={"tag-selection"} ref={tagContainerRef}>
                                        <TagSelection
                                            onSearchClick={() => onSearchClick()
                                            }
                                            selectedTag={selectedTag}
                                            onTagChange={(tag) => {
                                                setSelectedTag(tag);
                                            }}
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
                                            dispatch(setWhereFromExpanded(true));
                                            dispatch(setCalendarOpen(false));
                                            dispatch(setTagsExpanded(false));
                                            dispatch(setSearchResultsDisplayed(false));
                                            resetAutocompleteParameters();
                                        }}
                                    >
                                        {(() => {
                                            const dateDisplay = formatDisplayDate(startDate, endDate);
                                            return (
                                                <>
                                                    <div className={"activity-name-collapsed"}>
                                                        {selectedTag && getTagDescription(selectedTag)}
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
                                    onCitySelect={onCitySelect}
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