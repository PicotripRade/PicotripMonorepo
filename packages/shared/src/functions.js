// shared/fetchUserLocation.js
import Cookies from "js-cookie";

export const fetchUserLocation = async () => {
    try {
        const response = await fetch('/api/get_initial_location');
        if (!response.ok) {
            throw new Error('Failed to fetch user location');
        }
        const data = await response.json();

        return {
            city: data.city,
            country: data.country,
            id: data.id, // assuming 'id' is originId
        };
    } catch (error) {
        console.error('Error fetching user location:', error);
        return {
            city: '',
            country: '',
            id: null,
        };
    }

};