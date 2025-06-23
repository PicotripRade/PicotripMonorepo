import { combineReducers } from 'redux';
import tripOrganisationReducer from "./tripOrganisationReducer.jsx";
import cityInfoReducer from "./ctyInformationReducer.jsx";

const rootReducer = combineReducers({
  tripOrganisation: tripOrganisationReducer,
  cityInfoReducer: cityInfoReducer
});

export default rootReducer;