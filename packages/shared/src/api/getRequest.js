// packages/shared/src/api/getRequest.js

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

async function getRequest(path, options = {}) {
  let requestUrl;

  const WORKMODE = ENV.VITE_WORKMODE || ENV.REACT_APP_WORKMODE || 'prod';
  const URL = ENV.VITE_URL || ENV.REACT_APP_URL || 'localhost';
  const PORT = ENV.VITE_DJANGO_PORT || ENV.REACT_APP_DJANGO_PORT || '8000';

  if (WORKMODE === 'dev') {
    requestUrl = `http://${URL}:${PORT}${path.startsWith('/') ? path : `/${path}`}`;
  } else {
    requestUrl = path.startsWith('/') ? path : `/${path}`;
  }

  const response = await fetch(requestUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed: ${response.status} ${text}`);
  }

  return response.json();
}

export default getRequest;
