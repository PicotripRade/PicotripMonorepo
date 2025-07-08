export const SET_SEARCH_RESULTS_READY = "SET_SEARCH_RESULTS_READY";
export const SET_SEARCH_RESULTS_DISPLAYED = "SET_SEARCH_RESULTS_DISPLAYED";


export const setSearchResultsReady = (results) => ({
  type: SET_SEARCH_RESULTS_READY,
  payload: results,
});

export const setSearchResultsDisplayed = (resultsDisplayed) => ({
  type: SET_SEARCH_RESULTS_DISPLAYED,
  payload: resultsDisplayed,
});