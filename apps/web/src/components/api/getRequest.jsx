// src/api/getRequest.jsx
const GetRequest = async (path) => {  // Remove the extra function wrapper
    let requestUrl;

    if (import.meta.env.VITE_WORKMODE === 'dev') {
        requestUrl = `http://${import.meta.env.VITE_URL}:${import.meta.env.VITE_DJANGO_PORT}${path.startsWith('/') ? path : `/${path}`}`;
        console.log("request url", requestUrl);
    } else {
        requestUrl = `/${path.replace(/^\/+/, '')}`;
    }

    try {
        const response = await fetch(requestUrl, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Fetching data failed: ", error);
        throw error;
    }
};

export default GetRequest;
