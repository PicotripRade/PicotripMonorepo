import {ADD_CITY_INFO, SET_SELECTED_CITY} from "../actions/CityInformationActions.jsx";

const initialState = {
  cities: {},         // stores multiple cities by geonameid
  selectedCityId: null,  // ID of the currently selected city
};

const cityInfoReducer = (state = initialState, action) => {
  switch (action.type) {
    case ADD_CITY_INFO:
      const { geonameid, cityName, transportType, info } = action.payload;
      return {
        ...state,
        cities: {
          ...state.cities,
          [geonameid]: {
            cityName,
            transportType,
            info,
          },
        },
      };

    case SET_SELECTED_CITY:
      return {
        ...state,
        selectedCityId: action.payload,
      };

    default:
      return state;
  }
};

export default cityInfoReducer;
