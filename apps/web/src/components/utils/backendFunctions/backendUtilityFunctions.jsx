// Function to get user location
    import GetRequest from "../../api/getRequest.jsx";

const fetchUserLocation = async () => {
        try {
            const response = await GetRequest('/api/get_initial_location');
            console.log('User location data:', response);
            return response;

        } catch (error) {
            console.error('Failed to fetch user location:', error);
            return error;
        }
    };

export default fetchUserLocation;