import {
    RESET_START_DATE,
    SET_END_DATE,
    SET_START_DATE,
    RESET_END_DATE,
    CALENDAR_SWITCH
} from '../actions/tripOrganisationActions.jsx';

const initialState = { // Define the initial state
    startDate: null,
    endDate: null,
    CALENDAR_SWITCH: false,
};

const tripOrganisationReducer = (state = initialState, action) => { // Provide default state value
    switch (action.type) {
        case SET_START_DATE:
            return {
                ...state,
                startDate: action.payload,
            };
        case SET_END_DATE:
            return {
                ...state,
                endDate: action.payload,
            };
        case RESET_START_DATE:
            return {
                ...state,
                startDate: null,
            };
        case RESET_END_DATE:
            return {
                ...state,
                endDate: null,
            };
        case CALENDAR_SWITCH:
            return {
                ...state,
                calendarSwitch: action.payload,
            }
        default:
            return state;
    }
};

export default tripOrganisationReducer;