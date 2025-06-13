const PostRequest = async (requestData, path, responseType) => {
    try {
        // Ensure path is treated as absolute in production mode
        let requestUrl;
        if (process.env.REACT_APP_WORKMODE === 'dev') {
            requestUrl = `http://${process.env.REACT_APP_URL}:${process.env.REACT_APP_DJANGO_PORT}/${path}`;
        } else {
            // Add leading `/` to ensure path is absolute
            requestUrl = `/${path.replace(/^\/+/, '')}`;
        }

        const response = await fetch(
            requestUrl,
            {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            }
        );

        if (response.ok) {
            return responseType === 'json' ? await response.json() : await response.text();
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error("Fetch failed: ", error);
        throw error; // Rethrow the error to handle it in the component
    }
};

export default PostRequest;
