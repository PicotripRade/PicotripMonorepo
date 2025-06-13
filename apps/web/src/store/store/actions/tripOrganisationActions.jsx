export const SET_START_DATE = 'SET_START_DATE';
export const SET_END_DATE = 'SET_END_DATE';
export const RESET_START_DATE = 'RESET_START_DATE';
export const RESET_END_DATE = 'RESET_END_DATE';

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