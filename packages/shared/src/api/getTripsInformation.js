import GetRequest from "./getRequest.js";

const getTripsInfo = ({ from, beginDate, finalDate, tag, selectedAirports }) => {
  const query = `/api/get_trips_info?from=${from}&begin=${beginDate}&end=${finalDate}&activityType=${tag}&selectedAirports=${selectedAirports.join(',')}`;
  return GetRequest(query); // Returns a Promise
};

export default getTripsInfo;
