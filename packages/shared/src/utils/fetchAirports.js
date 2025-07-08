
import {setAirportsList, setSelectedAirportsList} from "../store/actions/tripOrganisationActions.jsx";
import GetRequest from "../api/getRequest.js"; // adjust import path to your shared API helper


export const fetchAirports = async ({
  originId,
  dispatch,
  setAutocompleteKey,
}) => {
  console.log("fetch airports function");
  try {
    const airports_list = await GetRequest(`/api/get_airports_list/?city_id=${originId}`);
    dispatch(setAirportsList(airports_list));
    dispatch(setSelectedAirportsList(airports_list.map(a => a.iata_code)));

    if (setAutocompleteKey) {
      setAutocompleteKey(prev => prev + 1); // Force re-render
    }
  } catch (error) {
    console.error('Failed to fetch airports list:', error);
  }
};
