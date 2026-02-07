import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import store from '@picotrip/shared/src/store/store.js';
import App from './App';
import reportWebVitals from "./reportWebVitals.jsx";
import i18n from "./functions/i18n";
import { I18nextProvider } from 'react-i18next';
import LoadingSpinner from "./components/utils/loadingSpinner/loadingSpinner.jsx";

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

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
    <Provider store={store}>
        <I18nextProvider i18n={i18n}>
            <React.Suspense fallback={<LoadingSpinner />}>
                <App />
            </React.Suspense>
        </I18nextProvider>
    </Provider>
);

// Measure performance
reportWebVitals();
