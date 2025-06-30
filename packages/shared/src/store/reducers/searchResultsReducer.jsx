import {SET_SEARCH_RESULTS_READY, setSearchResultsReady} from "../actions/searchResultsActions.jsx";

const initialState = {

    results: false,  //
};

const searchResultsReducer = (state = initialState, action) => {
    switch (action.type) {
        case SET_SEARCH_RESULTS_READY:
            return {
                ...state,
                setSearchResultsReady: action.payload,
            };


        default:
            return state;
    }
};

export default searchResultsReducer;
