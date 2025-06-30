import { combineReducers } from 'redux';
import tripOrganisationReducer from "./tripOrganisationReducer.jsx";
import cityInfoReducer from "./ctyInformationReducer.jsx";
import searchResultsReducer from "./searchResultsReducer.jsx";

const rootReducer = combineReducers({
  tripOrganisation: tripOrganisationReducer,
  cityInfoReducer: cityInfoReducer,
  searchResults: searchResultsReducer,
});

export default rootReducer;