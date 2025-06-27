import GetRequest from "./getRequest.js"; // Adjust path as needed

const getTripsInfo = ({ from, beginDate, finalDate, tag, selectedAirports }) => {
  console.log("getTripsInfo");
  console.log(selectedAirports);
  const query = `/api/get_trips_info?from=${from}&begin=${beginDate}&end=${finalDate}&activityType=${tag}&selectedAirports=${selectedAirports.join(',')}`;
  return GetRequest(query); // Returns a Promise
};

export default getTripsInfo;
