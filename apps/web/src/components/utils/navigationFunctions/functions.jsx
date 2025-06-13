// useBackToBase.js or inside functions.jsx
import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

function useBackToBase() {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const handlePopState = (event) => {
            if (location.pathname !== "/") {
                event.preventDefault(); // prevent default behavior
                navigate("/", { replace: true });
            }
        };

        window.addEventListener("popstate", handlePopState);

        return () => {
            window.removeEventListener("popstate", handlePopState);
        };
    }, [location, navigate]);
}

export default useBackToBase;
