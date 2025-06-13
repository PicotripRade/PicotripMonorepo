import React from "react";
import "./styles.css";

const DatepickerDayButton = ({ day, isActive, isInRange, onClick, isDisabled }) => {

  return (
      <div className={`datepicker-day ${isActive ? 'active' : ''} ${isInRange ? 'in-range' :''} ${isDisabled ? 'disabled' : ''}`} onClick={onClick}>
              <div className={`day-number ${isInRange ? 'in-range' : ''} {day-number ${isActive ? 'active' : ''} ${isDisabled ? 'disabled' : ''}`}>{day}</div>
      </div>
  );
};

export default DatepickerDayButton;
