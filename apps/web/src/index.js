import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import store from './store/store/store.jsx';
import App from './App';
import reportWebVitals from "./reportWebVitals.jsx";

// Unregister old service workers and register the new one
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then((registrations) => {
        registrations.forEach((registration) => registration.unregister());
    }).finally(() => {
        // Register the new service worker
        window.addEventListener('load', () => {
            navigator.serviceWorker.register(`${import.meta.env.VITE_PROTOCOL}://${import.meta.env.VITE_URL}/custom-service-worker.js`)
                .then((registration) => {
                    console.log('Service Worker registered with scope:', registration.scope);
                })
                .catch((error) => {
                    console.error('Service Worker registration failed:', error);
                });
        });
    });
}

// Get the root element
const container = document.getElementById('root');

// Create a root and render your app
const root = createRoot(container);
root.render(
    <Provider store={store}>
        <App />
    </Provider>
);

// Measure performance
reportWebVitals();
