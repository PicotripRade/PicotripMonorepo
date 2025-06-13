export const ADD_CITY_INFO = "ADD_CITY_INFO";
export const SET_SELECTED_CITY = "SET_SELECTED_CITY";

export const addCityInfo = (geonameid, payload) => ({
  type: ADD_CITY_INFO,
  payload: {
    geonameid,
    ...payload,
  },
});

export const setSelectedCityRedux = (geonameid) => ({
  type: SET_SELECTED_CITY,
  payload: geonameid,
});