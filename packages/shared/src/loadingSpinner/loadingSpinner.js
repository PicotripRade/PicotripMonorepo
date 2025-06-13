import React, {useEffect, useState} from 'react';
import 'web/src/commonStyles.css';
import Gif from 'web/src/images/gifs/grey-9026_128.gif';

function LoadingSpinner() {
    const [colorSpinner, setColorSpinner] = useState('');

    // Use useEffect to retrieve the CSS variable value when the component mounts
    useEffect(() => {
        // Get the root element (where CSS variables are defined)
        const root = document.documentElement;

        // Use getComputedStyle to retrieve the value of --disabled-text
        const disabledTextColor = getComputedStyle(root).getPropertyValue('--background-less-dark').trim();

        // Set the colorSpinner state with the retrieved value
        setColorSpinner(disabledTextColor);
    }, []);

    return (
        <div className="spinner-container">
            <img
                src={Gif}
                alt="Loading..."
                height={25}
                width={25}
                style={{filter: `drop-shadow(0 0 5px ${colorSpinner})`}} // optional use of color
            />
        </div>
    );
}

export default LoadingSpinner;