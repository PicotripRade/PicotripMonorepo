import {saveTripInfo} from "../functions.js";
import getTripsInfo from "../api/getTripsInformation.js";


export const handleSearchClick = async ({
  overrideParams = null,
  skipUpdateURL = false,
  startDate,
  endDate,
  originId,
  selectedTag,
  selectedAirportsList,
  airportsList,
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
  setArrowBackPressedAction,
  setAirportsListAction,
  setSelectedAirportsListAction
}) => {
  try {
    setErrorResponse(false); // Reset error state
    setTagsExpanded(false);
    dispatch(setArrowBackPressedAction(false));

    const beginDate = overrideParams?.begin || formatDateToNumbersAndLetters(startDate);
    const finalDate = overrideParams?.end || formatDateToNumbersAndLetters(endDate);
    const from = overrideParams?.from || originId;
    const tag = overrideParams?.tag || selectedTag;

    // Save to Redux and cookies
    dispatch(setSelectedAirportsListAction(selectedAirportsList));
    dispatch(setAirportsListAction(airportsList));
    saveTripInfo({ startingPoint, beginDate, finalDate });

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
      selectedAirports: selectedAirportsList
    });

    if (!arrowBackPressedRef.current) {
      dispatch(setSearchResultsReady(true));
      dispatch(setSearchResultsDisplayed(true));
      setInputFieldsCollapsed(true);
      setResponseData(data);
    }

    if (data.error === "Internal server error") {
      console.log("there was a 500 error");
      setErrorResponse(true);
    }

    return data;
  } catch (error) {
    console.error("Search failed:", error);
    setErrorResponse(true);
    return null;
  } finally {
    setIsLoading(false);
  }
};

function formatDateToNumbersAndLetters(date) {
  if (!date) return '';
  return new Date(date).toISOString().split('T')[0]; // Basic ISO fallback
}
