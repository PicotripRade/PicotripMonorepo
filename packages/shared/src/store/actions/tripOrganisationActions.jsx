export const SET_START_DATE = 'SET_START_DATE';
export const SET_END_DATE = 'SET_END_DATE';
export const RESET_START_DATE = 'RESET_START_DATE';
export const RESET_END_DATE = 'RESET_END_DATE';
export const CALENDAR_SWITCH = 'CALENDAR_SWITCH';

export const AIRPORTS_LIST = 'AIRPORTS_LIST';
export const SELECTED_AIRPORTS_LIST = 'SELECTED_AIRPORTS_LIST';
export const TAG_SELECTION = 'TAG_SELECTION';

export const setStartDateRedux = (date) => ({
    type: SET_START_DATE,
    payload: date
});
export const setEndDateRedux = (date) => ({
    type: SET_END_DATE,
    payload: date
});
export const resetStartDate = () => ({
    type: RESET_START_DATE
});

export const resetEndDate = () => ({
    type: RESET_END_DATE
});

export const setCalendarSwitch = (calendarSwitch) => ({
    type: CALENDAR_SWITCH,
    payload: calendarSwitch
});

export const setAirportsList = (airports) => ({
    type: AIRPORTS_LIST,
    payload: airports
});

export const setSelectedAirportsList = (airports) => ({
    type: SELECTED_AIRPORTS_LIST,
    payload: airports
});

export const setTag = (tag) => ({
    type: TAG_SELECTION,
    payload: tag
});