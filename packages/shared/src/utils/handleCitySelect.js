


import {formatDateToNumbersAndLetters} from "../functions";
import GetRequest from "../api/getRequest";
import {addCityInfo} from "../store/actions/CityInformationActions.jsx"; // adjust as needed

export const handleCitySelect = async ({
  startDate,
  endDate,
  originId,
  selectedTag,
  selectedAirports,
  dataPerCityRedux,
  setIsLoadingCityData,
  setResponseCityData,
  dispatch,
}) => {
  const beginDate = formatDateToNumbersAndLetters(startDate);
  const finalDate = formatDateToNumbersAndLetters(endDate);
  const from = originId;
  const tag = selectedTag || "";

  if (!geonameid) {
    console.log("No city id set!!!");
    return;
  }

  if (Object.prototype.hasOwnProperty.call(dataPerCityRedux, geonameid)) {
    console.log("Using cached city data from Redux for geonameid:", geonameid);
    setResponseCityData(dataPerCityRedux[geonameid].info);
    return;
  }

  try {
    setIsLoadingCityData(true);
    const city_response = await GetRequest(
      `/api/get_city_info?from=${from}&begin=${beginDate}&end=${finalDate}&activityType=${tag}` +
        `&selectedAirports=${selectedAirports.join(",")}&geoname=${geonameid}&transportType=${transportType}` +
        `&cityName=${encodeURIComponent(cityName)}&countryName=${encodeURIComponent(countryName)}`
    );

    console.log("Fetched city data from API:", city_response);
    setIsLoadingCityData(false);
    setResponseCityData(city_response);

    dispatch(
      addCityInfo(geonameid, {
        cityName,
        transportType,
        info: city_response,
      })
    );
  } catch (error) {
    console.error("Failed to fetch city data:", error);
    setIsLoadingCityData(false);
  }
};
