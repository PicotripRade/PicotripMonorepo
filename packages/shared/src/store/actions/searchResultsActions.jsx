export const SET_SEARCH_RESULTS_READY = "SET_SEARCH_RESULTS_READY";


export const setSearchResultsReady = (results) => ({
  type: SET_SEARCH_RESULTS_READY,
  payload: results,
});