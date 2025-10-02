import PostRequest from "../api/postRequest";

export async function sendCoordinates(onSuccess, onError) {
    if (!navigator.geolocation) {
        console.error('Geolocation is not supported by this browser.');
        if (onError) onError(new Error('Geolocation not supported'));
        return;
    }

    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                try {
                    const locationData = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        timestamp: new Date().toISOString()
                    };
                    const readyToSend = `(${locationData.latitude},${locationData.longitude})`;
                    const path = 'api/set_geolocation/';

                    const response = await PostRequest(readyToSend, path, 'json');

                    if (response && response.city) {
                        const cityLocation = `${response.city.city}, ${response.city.country}`;
                        if (onSuccess) {
                            onSuccess({
                                location: cityLocation,
                                originId: response.city.id,
                                rawResponse: response
                            });
                        }
                        resolve(response);
                    } else {
                        throw new Error("Unexpected response");
                    }
                } catch (error) {
                    console.error("Error sending location:", error);
                    if (onError) onError(error);
                    reject(error);
                }
            },
            (err) => {
                console.error("Geolocation error:", err.message);
                if (onError) onError(err);
                reject(err);
            }
        );
    });
}
