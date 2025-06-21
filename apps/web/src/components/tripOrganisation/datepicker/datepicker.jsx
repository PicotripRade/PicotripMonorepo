import React, {useState, useEffect, useMemo, useRef} from "react";

import "./styles.css";
import DatepickerDayButton from "../buttons/dayButton.jsx";
import CustomButton from "../buttons/customButton.jsx";
import {useDispatch, useSelector} from "react-redux";
import {
    resetEndDate,
    resetStartDate, setCalendarSwitch, setEndDateRedux,
    setStartDateRedux,
} from "../../../store/store/actions/tripOrganisationActions.jsx";
import PlusMinus from "./../../../images/destinations/datepicker/plus-minus.svg";
import PlusMinusWhite from "./../../../images/destinations/datepicker/plus-minus-white.svg";
import {formatDisplayDate, monthsNames, dayNames, getNumberOfRows, isDaySelectable} from "@picotrip/shared";

const CustomCalendar = ({isOpen, onClose, onMonthSelection}) => {
        const [displayedMonths, setDisplayedMonths] = useState([new Date()]); // Array of displayed months

        const [selectedDateExtender, setSelectedDateExtender] = useState("exact");

        const startDate = useSelector((state) => state.tripOrganisation.startDate);
        const endDate = useSelector((state) => state.tripOrganisation.endDate);
        const isDates = useSelector((state) => state.tripOrganisation.calendarSwitch) || false;

        const scrollableRef = useRef(null);  // Add this ref
        const dispatch = useDispatch();

        const [selectedMonths, setSelectedMonths] = useState([]);


        useEffect(() => {
            // Initialize displayedMonths with the current month and the next 12 months
            const initialMonths = [];
            const current = new Date();
            for (let i = 0; i < 12; i++) {
                const newMonth = new Date(current.getFullYear(), current.getMonth() + i, 1);
                initialMonths.push(newMonth);
            }
            setDisplayedMonths(initialMonths);
        }, []);


        // Add this useEffect to handle scrolling when calendar opens
        useEffect(() => {
            if (isOpen && scrollableRef.current) {
                // Small timeout to ensure DOM is rendered
                setTimeout(() => {
                    scrollToFirstSelectableDay();
                }, 50);
            }
        }, [isOpen]);

        useEffect(() => {
            if (onMonthSelection) {
                // Convert to more readable format for parent component
                const formattedSelection = selectedMonths.map(({monthIndex, year}) => ({
                    month: monthsNames[monthIndex],
                    monthIndex,
                    year
                }));
                onMonthSelection(formattedSelection);
            }
        }, [selectedMonths, onMonthSelection]);

        // Add this function to find and scroll to first selectable day
        const scrollToFirstSelectableDay = () => {
            if (!scrollableRef.current) return;

            const dayElements = scrollableRef.current.querySelectorAll('[data-calendar-date]');

            for (let el of dayElements) {
                const elDate = new Date(el.getAttribute('data-calendar-date'));

                if (startDate) {
                    if (
                        elDate.getDate() === startDate.getDate() &&
                        elDate.getMonth() === startDate.getMonth() &&
                        elDate.getFullYear() === startDate.getFullYear()
                    ) {
                        el.scrollIntoView({behavior: 'smooth', block: 'start'});
                        return;
                    }
                } else {
                    // Scroll to first future date
                    const now = new Date();
                    if (elDate > new Date(now.setDate(now.getDate() - 1))) {
                        el.scrollIntoView({behavior: 'smooth', block: 'start'});
                        return;
                    }
                }
            }
        };

        const toggleSlider = () => {
            dispatch(setCalendarSwitch(!isDates));
        }

        const handleDayClick = (day, currentDate) => {
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);

            if (!startDate) {
                dispatch(setStartDateRedux(date));
                dispatch(resetEndDate());
            } else if (!endDate) {
                // Check if the selected end date is before the start date
                if (date < endDate) {
                    dispatch(setStartDateRedux(date));
                } else {
                    dispatch(setEndDateRedux(date));
                }
            } else {
                dispatch(resetStartDate());
                dispatch(resetEndDate());
            }
        };

        const isDayActive = (day, currentDate) => {

            if (!startDate) return false;
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
            return (
                date.getDate() === startDate.getDate() &&
                date.getMonth() === startDate.getMonth() &&
                date.getFullYear() === startDate.getFullYear()
            );
        };

        const isDayInRange = (day, currentDate) => {

            if (!startDate || !endDate) return false;
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
            return date >= Math.min(startDate, endDate) && date <= Math.max(startDate, endDate); // Corrected range check
        };


        const renderDays = useMemo(() => {
            return displayedMonths.map((currentDate, index) => {
                const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
                const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
                const days = [];



                // Check if the current month is the last month in the displayedMonths array
                const isLastMonth = index === displayedMonths.length - 1;

                for (let i = 0; i < firstDayOfMonth; i++) {
                    days.push(<div key={`empty-${i}-${currentDate.getMonth()}`} className="datepicker-day-empty"/>);
                }

                for (let i = 1; i <= daysInMonth; i++) {
                    const isDisabled = !isDaySelectable(i, currentDate);
                    days.push(
                        <div
                            key={`${i}-${currentDate.getMonth()}`}
                            data-calendar-date={new Date(
                                currentDate.getFullYear(),
                                currentDate.getMonth(),
                                i
                            ).toISOString()}
                        >
                            <DatepickerDayButton
                                key={`${i}-${currentDate.getMonth()}`}
                                day={i}
                                isActive={isDayActive(i, currentDate)}
                                isInRange={isDayInRange(i, currentDate)}
                                isStart={
                                    i === startDate?.getDate() &&
                                    startDate?.getMonth() === currentDate.getMonth() &&
                                    startDate?.getFullYear() === currentDate.getFullYear()
                                }
                                isEnd={
                                    i === endDate?.getDate() &&
                                    endDate?.getMonth() === currentDate.getMonth() &&
                                    endDate?.getFullYear() === currentDate.getFullYear()
                                }
                                onClick={() => handleDayClick(i, currentDate)}
                                isDisabled={isDisabled}
                            />
                        </div>
                    );
                }

                while (days.length % 7 !== 0) {
                    days.push(<div key={`extra-${days.length}-${currentDate.getMonth()}`}
                                   className="datepicker-day-empty"/>);
                }
                return (
                    <div key={currentDate.getMonth()} className={`month-container ${isLastMonth ? "last-month" : ""} `}>
                        <div className="calendar-header-inner">
                            {monthsNames[currentDate.getMonth()]}&nbsp;{currentDate.getFullYear()}
                        </div>
                        <div
                            className={`calendar-days ${getNumberOfRows(currentDate) === 5 ? "tight-rows" : ""} ${getNumberOfRows(currentDate) === 4 ? "very-tight-rows" : ""}`}>
                            {days}
                        </div>
                    </div>
                );
            });
        }, [displayedMonths, startDate, endDate]);


        // Usage in your JSX:
        const dateDisplay = formatDisplayDate(startDate, endDate);

        const handleDoneClick = () => onClose();

        return (
            <>
                <div className="time-range-container rounded-button bottom-shadow"
                >
                    {!isOpen && (
                        <div className="time-range-box rounded-button">
                            {<div className={"disabled-text rounded-left-button"}> When</div>}
                            <div className={"date-range-info-wrapper"}>
                                <div className="date-range-info rounded-right-button">
                                    <div className={`range-display ${startDate} ? "" : "unselected"}`}>
                                        {dateDisplay.start}
                                    </div>
                                    {!(dateDisplay.start && !dateDisplay.end) &&
                                        <div className={"line unselected"}>-</div>}
                                    <div className={`range-display ${endDate ? "" : "unselected"}`}>
                                        {dateDisplay.end}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    {isOpen && (
                        <>
                            <p className={"input-box-title"}> When's your trip?</p>
                            {import.meta.env.VITE_WORKMODE !== 'prod' && (
                                <div className="toggle-container" onClick={toggleSlider}>
                                    <div className={`slider ${isDates ? "toggled" : ""}`}></div>
                                    <div className="label">Dates</div>
                                    <div className="label">Flexible</div>
                                </div>
                            )}
                            <div>
                                <div className={`custom-calendar rounded-button`}>
                                    {console.log("sad mi reci is dates", isDates)}
                                    {isDates === false ? (
                                        <>
                                            <div className="datepicker-day-names">
                                                {dayNames.map((dayName, index) => (
                                                    <div key={index} className="datepicker-day-name">
                                                        {dayName}
                                                    </div>
                                                ))}
                                            </div>
                                            <div className={"calendar-open"}>
                                                <div className={`scrollable-wrapper`} ref={scrollableRef}>
                                                    <div className={"months-container"}>
                                                        {renderDays}
                                                    </div>
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="month-list-container">
                                            {Array.from({length: 12}).map((_, index) => {
                                                const now = new Date();
                                                const currentMonth = now.getMonth();
                                                const currentYear = now.getFullYear();

                                                const monthOffset = index;
                                                const monthIndex = (currentMonth + monthOffset) % 12;
                                                const year = currentYear + Math.floor((currentMonth + monthOffset) / 12);

                                                const monthName = monthsNames[monthIndex];

                                                // Check if this month is selected
                                                const isSelected = selectedMonths.some(
                                                    m => m.monthIndex === monthIndex && m.year === year
                                                );

                                                return (
                                                    <div
                                                        key={`${monthName}-${year}`}
                                                        className={`month-option ${isSelected ? "selected" : ""}`}
                                                        onClick={() => {
                                                            const monthKey = {monthIndex, year};

                                                            setSelectedMonths(prev => {
                                                                // Toggle selection
                                                                const alreadySelected = prev.some(
                                                                    m => m.monthIndex === monthIndex && m.year === year
                                                                );

                                                                let newSelection;
                                                                if (alreadySelected) {
                                                                    // Remove if already selected
                                                                    newSelection = prev.filter(
                                                                        m => !(m.monthIndex === monthIndex && m.year === year)
                                                                    );
                                                                } else {
                                                                    // Add if not selected
                                                                    newSelection = [...prev, monthKey];
                                                                }

                                                                return newSelection;
                                                            });
                                                        }}
                                                    >
                                                        {monthName} {year}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}

                                </div>
                                <div className={"empty-space"}></div>
                                <div className={"datepicker-navigation rounded-bottom-button"}>
                                    {isDates === false ? (
                                        <div className={"date-range-extenders"}>
                                            <div className={"scrollable-extenders"}>
                                                {["exact", "1 day", "2 days", "3 days", "5 days"].map((option) => (
                                                    <div
                                                        key={option}
                                                        className={`plus-minus-dates rounded-button ${selectedDateExtender === option ? "blue-selected" : ""}`}
                                                        onClick={() => setSelectedDateExtender(option)}
                                                    >
                                                        {option === "exact" ? (
                                                            "exact dates"
                                                        ) : (
                                                            <>
                                                                <img
                                                                    src={selectedDateExtender === option ? PlusMinusWhite : PlusMinus}
                                                                    alt="+/-"
                                                                    className="plus-minus-icon"
                                                                />
                                                                &nbsp;{option}
                                                            </>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (<div>
                                        Will add here something
                                    </div>)}
                                    <CustomButton onClick={handleDoneClick} label={"Done"}/>
                                </div>
                            </div>
                        </>
                    )
                    }
                </div>
            </>
        )
            ;
    }
;

export default CustomCalendar;
