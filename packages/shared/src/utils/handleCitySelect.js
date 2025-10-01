import GetRequest from "../api/getRequest.js";

export const handleCitySelect = async ({
  geonameid,
  transportType,
  cityName,
  countryName,
  from,
  beginDate,
  finalDate,
  tag,
  selectedAirportsList,
  dataPerCity,
  dispatch,
  setIsLoadingCityData,
  setResponseCityData,
  addCityInfoAction, // passed action creator
}) => {
  if (!geonameid) {
    console.log("No city id set!!!");
    return;
  }

  // Use cached data if available
  if (Object.prototype.hasOwnProperty.call(dataPerCity, geonameid)) {
    console.log("Using cached city data from Redux for geonameid:", geonameid);
    setResponseCityData(dataPerCity[geonameid].info);
    return;
  }

  try {
    setIsLoadingCityData(true);

    const url = `/api/get_city_info?from=${from}&begin=${beginDate}&end=${finalDate}` +
                `&activityType=${tag}&selectedAirports=${selectedAirportsList.join(',')}` +
                `&geoname=${geonameid}&transportType=${transportType}` +
                `&cityName=${encodeURIComponent(cityName)}&countryName=${encodeURIComponent(countryName)}`;

    const city_response = await GetRequest(url);

    console.log("Fetched city data from API:", city_response);
    setResponseCityData(city_response);
    dispatch(addCityInfoAction(geonameid, {
      cityName,
      transportType,
      info: city_response
    }));
  } catch (error) {
    console.error("Failed to fetch city data:", error);
  } finally {
    setIsLoadingCityData(false);
  }
};
