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


export const getTagDescription = (tag) => {
    switch (tag) {
        case "summer_vacation":
            return "Summer";
        case "family_trip":
            return "Family Trip";
        case "mountains":
            return "Mountains";
        default:
            return tag;
    }
}


export const loadLocationCookies = () => {
    let airportList = [];
    let selectedAirports = [];
    const startingPoint = Cookies.get("startingPoint") || "";

    try {
        const cookieAirportList = Cookies.get("airportList");
        if (cookieAirportList) {
            airportList = JSON.parse(cookieAirportList);
        }
    } catch (e) {
        console.error("Failed to parse airportList from cookies:", e);
    }

    try {
        const cookieSelectedAirports = Cookies.get("selectedAirports");
        if (cookieSelectedAirports) {
            selectedAirports = JSON.parse(cookieSelectedAirports);
        }
    } catch (e) {
        console.error("Failed to parse selectedAirports from cookies:", e);
    }

    return {startingPoint, airportList, selectedAirports};
};


export const formatDateToMonthDayYear = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);

    const options = {year: 'numeric', month: 'short', day: 'numeric'};
    return d.toLocaleDateString('en-US', options);
};


export const formatDateToNumbersAndLetters = (date) => {
    if (!date) return '';
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${year}-${month}-${day}`;
};

export const removeTextInBrackets = (str) => {
    return str.replace(/\s*\(.*?\)\s*/g, '').trim();
};