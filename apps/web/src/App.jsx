import React, {useEffect} from 'react';
import {BrowserRouter as Router, Route, Routes, useLocation} from 'react-router-dom';
import UserDataEntryStep from "./components/tripOrganisation/steps/initialDataEntry/userDataEntryStep.jsx";

const TrackingWrapper = () => {
    const location = useLocation();

    useEffect(() => {
        if (import.meta.env.VITE_WORKMODE !== 'dev') {
            if (typeof window.gtag === 'function') {
                const pagePath = location.pathname + location.search;
                window.gtag('config', 'G-G9706RXBCT', {page_path: pagePath});
            } else {
                console.warn("Google Analytics gtag.js script is not initialized.");
            }
        }
    }, [location]);

    return null; // No UI rendering, only tracking logic
};

const App = () => {
    useEffect(() => {
        if (import.meta.env.VITE_WORKMODE !== 'dev') {
            const initializeHotjar = (id, version = 6) => {
                if (typeof window.hj === 'undefined') {
                    (function (h, o, t, j, a, r) {
                        h.hj = h.hj || function () {
                            (h.hj.q = h.hj.q || []).push(arguments)
                        };
                        h._hjSettings = {hjid: id, hjsv: version};
                        a = o.getElementsByTagName('head')[0];
                        r = o.createElement('script');
                        r.async = 1;
                        r.src = t + h._hjSettings.hjid + j + h._hjSettings.hjsv;
                        a.appendChild(r);
                    })(window, document, 'https://static.hotjar.com/c/hotjar-', '.js?sv=');
                }
            };

            initializeHotjar(5161776);
        }
    }, []);

    useEffect(() => {
        if (import.meta.env.VITE_WORKMODE !== 'dev') {
            const script = document.createElement('script');
            script.src = `https://www.googletagmanager.com/gtag/js?id=G-G9706RXBCT`;
            script.async = true;
            script.onload = () => {
                window.dataLayer = window.dataLayer || [];
                window.gtag = function () {
                    window.dataLayer.push(arguments);
                };
                window.gtag('js', new Date());
                window.gtag('config', 'G-G9706RXBCT');
            };
            document.head.appendChild(script);
        }
    }, []);


    return (
        <Router>
            <TrackingWrapper/>
            <Routes>
                <Route path="/" exact element={<UserDataEntryStep/>}/>
                <Route path="/en" exact element={<UserDataEntryStep/>}/>
                <Route path="/search" element={<UserDataEntryStep/>}/>
                <Route path="/search/en" element={<UserDataEntryStep/>}/>
            </Routes>
        </Router>
    );
};

export default App;
