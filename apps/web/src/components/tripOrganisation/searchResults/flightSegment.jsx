import {removeTextInBrackets} from "../functions/functions.jsx";

const FlightSegment = ({segment}) => {
    return (
        <div className="flight-segment strong-shadow rounded-button">
            <div className="flight-header">
                <span>{removeTextInBrackets(segment?.["airline:"])} ({segment?.airlineCode})</span>
            </div>
            <div className="flight-body">
                <div className="flight-point">
                    <div className="code">{segment?.departure}</div>
                    <div className="time">{segment?.departureTime}</div>
                </div>
                <div className="flight-line"></div>
                <div className="flight-point">
                    <div className="code">{segment?.arrival}</div>
                    <div className="time">{segment?.arrivalTime}</div>
                </div>
            </div>
        </div>
    );
};

export default FlightSegment;