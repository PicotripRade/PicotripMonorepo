// packages/shared/src/api/postRequest.js

// Detect platform
const isReactNative = typeof navigator !== 'undefined' && navigator.product === 'ReactNative';

let ENV = {};

if (isReactNative) {
  // React Native environment
  ENV = require('@env');
} else if (typeof process !== 'undefined' && process.env) {
  // Web environment (CRA)
  ENV = process.env;
} else if (typeof window !== 'undefined' && window?.VITE_ENV) {
  // Vite workaround: window.VITE_ENV must be set manually in index.html
  ENV = window.VITE_ENV;
} else {
  ENV = {}; // fallback
}

const PostRequest = async (requestData, path, responseType = 'json') => {
  try {
    let requestUrl;

    const WORKMODE = ENV.VITE_WORKMODE || ENV.REACT_APP_WORKMODE || 'prod';
    const URL = ENV.VITE_URL || ENV.REACT_APP_URL || 'localhost';
    const PORT = ENV.VITE_DJANGO_PORT || ENV.REACT_APP_DJANGO_PORT || '8000';

    if (WORKMODE === 'dev') {
      requestUrl = `http://${URL}:${PORT}/${path.replace(/^\/+/, '')}`;
    } else {
      // Ensure path is absolute
      requestUrl = `/${path.replace(/^\/+/, '')}`;
    }

    console.log('POST request URL:', requestUrl);

    const response = await fetch(requestUrl, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (response.ok) {
      return responseType === 'json' ? await response.json() : await response.text();
    } else {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('Fetch failed: ', error);
    throw error; // rethrow to handle in component
  }
};

// Default export so existing imports work
export default PostRequest;
