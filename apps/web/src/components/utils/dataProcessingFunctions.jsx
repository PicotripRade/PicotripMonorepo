const formatDisplayDate = (startDate, endDate) => {
    if (!startDate) return {start: "start", end: "end"};

    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    const formatSingleDate = (date) => {
        return `${date.getDate().toString().padStart(2, "0")} ${months[date.getMonth()]}`;
    };

    const startFormatted = formatSingleDate(startDate);

    if (!endDate) {
        return {
            start: startFormatted,
        };
    }

    const endFormatted = formatSingleDate(endDate);

    // Same month and year: "12-15 Mar"
    if (startDate.getMonth() === endDate.getMonth() &&
        startDate.getFullYear() === endDate.getFullYear()) {
        return {
            start: `${startDate.getDate().toString().padStart(2, "0")}`,
            end: `${endDate.getDate().toString().padStart(2, "0")} ${months[endDate.getMonth()]}`
        };
    }

    // Same year only: "12 Mar - 23 Apr"
    if (startDate.getFullYear() === endDate.getFullYear()) {
        return {
            start: startFormatted,
            end: endFormatted
        };
    }

    // Different years: "12 Mar '23 - 15 Jan '24"
    return {
        start: `${startFormatted} '${startDate.getFullYear().toString().slice(-2)}`,
        end: `${endFormatted} '${endDate.getFullYear().toString().slice(-2)}`
    };
};

export {
    formatDisplayDate
};