import {
    RESET_START_DATE,
    SET_END_DATE,
    SET_START_DATE,
    RESET_END_DATE,
    CALENDAR_SWITCH,
    AIRPORTS_LIST,
    SELECTED_AIRPORTS_LIST, STARTING_POINT, ARROW_BACK_PRESSED, IS_VALID_SELECTION, WHERE_FROM_EXPANDED, CALENDAR_OPEN
} from '../actions/tripOrganisationActions.jsx';

const initialState = { // Define the initial state
    startDate: null,
    endDate: null,
    calendarSwitch: false,
    airportList: [],
    selectedAirportsList: [],
    startingPoint: "",
    arrowBackPressed: false,
    isValidSelection: true,
    isWhereFromExpanded: true,
    isCalendarOpen: false,
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
        case AIRPORTS_LIST:
            return {
                ...state,
                airportList: action.payload,
            }
        case SELECTED_AIRPORTS_LIST:
            return {
                ...state,
                selectedAirportsList: Array.isArray(action.payload) ? action.payload : [],
            }
        case STARTING_POINT:
            return {
                ...state,
                startingPoint: action.payload,
            }
        case ARROW_BACK_PRESSED:
            return {
                ...state,
                tag: action.payload,
            }
        case IS_VALID_SELECTION:
            return {
                ...state,
                isValidSelection: action.payload,
            }
        case WHERE_FROM_EXPANDED:
            return {
                ...state,
                isWhereFromExpanded: action.payload,
            }
        case CALENDAR_OPEN:
            return {
                ...state,
                isCalendarOpen: action.payload,
            }
        default:
            return state;
    }
};

export default tripOrganisationReducer;