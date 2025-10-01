import React, { useState, useEffect, useMemo, useRef } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  Image,
  StyleSheet,
  Dimensions,
} from "react-native";
import { useDispatch, useSelector } from "react-redux";

import PlusMinus from "@picotrip/shared/assets/images/datepicker/plus-minus.svg";
import PlusMinusWhite from "@picotrip/shared/assets/images/datepicker/plus-minus-white.svg";

import {
  formatDisplayDate,
  monthsNames,
  dayNames,
  getNumberOfRows,
  isDaySelectable,
} from "@picotrip/shared";

import {
  resetEndDate,
  resetStartDate,
  setCalendarSwitch,
  setEndDateRedux,
  setStartDateRedux,
} from "@picotrip/shared/src/store/actions/tripOrganisationActions";
import DatepickerDayButton from "./DayButton";
import CustomButton from "../buttons/CustomButtonRN";

const { width: screenWidth } = Dimensions.get("window");

const CustomCalendar = ({ onClose, onMonthSelection }) => {
  const [displayedMonths, setDisplayedMonths] = useState([new Date()]);
  const [selectedDateExtender, setSelectedDateExtender] = useState("exact");
  const [selectedMonths, setSelectedMonths] = useState([]);

  const startDate = useSelector((state) => state.tripOrganisation.startDate);
  const endDate = useSelector((state) => state.tripOrganisation.endDate);
  const isDates = useSelector((state) => state.tripOrganisation.calendarSwitch) || false;
  const isOpen = useSelector((state) => state.tripOrganisation.isCalendarOpen);

  const scrollableRef = useRef(null);
  const dispatch = useDispatch();

  useEffect(() => {
    const initialMonths = [];
    const current = new Date();
    for (let i = 0; i < 12; i++) {
      initialMonths.push(new Date(current.getFullYear(), current.getMonth() + i, 1));
    }
    setDisplayedMonths(initialMonths);
  }, []);

  useEffect(() => {
    if (onMonthSelection) {
      const formattedSelection = selectedMonths.map(({ monthIndex, year }) => ({
        month: monthsNames[monthIndex],
        monthIndex,
        year,
      }));
      onMonthSelection(formattedSelection);
    }
  }, [selectedMonths, onMonthSelection]);

  const toggleSlider = () => {
    dispatch(setCalendarSwitch(!isDates));
  };

  const handleDayClick = (day, currentDate) => {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    if (!startDate) {
      dispatch(setStartDateRedux(date));
      dispatch(resetEndDate());
    } else if (!endDate) {
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
    return date >= Math.min(startDate, endDate) && date <= Math.max(startDate, endDate);
  };

  // ✅ Incorporated improved renderDays
  const renderDays = useMemo(() => {
    return displayedMonths.map((currentDate, index) => {
      const daysInMonth = new Date(
        currentDate.getFullYear(),
        currentDate.getMonth() + 1,
        0
      ).getDate();
      const firstDayOfMonth = new Date(
        currentDate.getFullYear(),
        currentDate.getMonth(),
        1
      ).getDay();

      const days = [];
      const isLastMonth = index === displayedMonths.length - 1;

      // empty slots before first day
      for (let i = 0; i < firstDayOfMonth; i++) {
        days.push(<View key={`empty-${i}`} style={styles.dayEmpty} />);
      }

      // actual days
      for (let i = 1; i <= daysInMonth; i++) {
        const isDisabled = !isDaySelectable(i, currentDate);
        days.push(
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
            onPress={() => handleDayClick(i, currentDate)}
            isDisabled={isDisabled}
          />
        );
      }

      // trailing fillers to keep rows even
      while (days.length % 7 !== 0) {
        days.push(<View key={`extra-${days.length}`} style={styles.dayEmpty} />);
      }

      return (
        <View
          key={currentDate.getMonth()}
          style={[styles.monthContainer, isLastMonth && styles.lastMonth]}
        >
          <Text style={styles.calendarHeader}>
            {monthsNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </Text>
          <View
            style={[
              styles.calendarDays,
              getNumberOfRows(currentDate) === 5 && styles.tightRows,
              getNumberOfRows(currentDate) === 4 && styles.veryTightRows,
            ]}
          >
            {days}
          </View>
        </View>
      );
    });
  }, [displayedMonths, startDate, endDate]);

  const dateDisplay = formatDisplayDate(startDate, endDate);

  return (
    <View style={styles.container}>
      {!isOpen && (
        <View style={styles.timeRangeBox}>
          <Text style={styles.label}>When</Text>
          <View style={styles.dateRangeInfo}>
            <Text style={[styles.rangeDisplay, !startDate && styles.unselected]}>
              {dateDisplay.start}
            </Text>
            <Text style={styles.separator}>-</Text>
            <Text style={[styles.rangeDisplay, !endDate && styles.unselected]}>
              {dateDisplay.end}
            </Text>
          </View>
        </View>
      )}
      {isOpen && (
        <>
          <Text style={styles.title}>When’s your trip?</Text>
          <View style={styles.customCalendar}>
            {!isDates ? (
              <>
                <View style={styles.dayNames}>
                  {dayNames.map((d, idx) => (
                    <Text key={idx} style={styles.dayName}>
                      {d}
                    </Text>
                  ))}
                </View>
                <ScrollView ref={scrollableRef} style={styles.scrollWrapper}>
                  <View style={styles.monthsContainer}>{renderDays}</View>
                </ScrollView>
              </>
            ) : (
              <ScrollView style={styles.monthList}>
                {Array.from({ length: 12 }).map((_, index) => {
                  const now = new Date();
                  const currentMonth = now.getMonth();
                  const currentYear = now.getFullYear();
                  const monthIndex = (currentMonth + index) % 12;
                  const year = currentYear + Math.floor((currentMonth + index) / 12);
                  const isSelected = selectedMonths.some(
                    (m) => m.monthIndex === monthIndex && m.year === year
                  );
                  return (
                    <TouchableOpacity
                      key={`${monthIndex}-${year}`}
                      style={[styles.monthOption, isSelected && styles.selected]}
                      onPress={() => {
                        setSelectedMonths((prev) => {
                          const already = prev.some(
                            (m) => m.monthIndex === monthIndex && m.year === year
                          );
                          if (already) {
                            return prev.filter(
                              (m) => !(m.monthIndex === monthIndex && m.year === year)
                            );
                          }
                          return [...prev, { monthIndex, year }];
                        });
                      }}
                    >
                      <Text>
                        {monthsNames[monthIndex]} {year}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            )}
          </View>
          <View style={styles.footer}>
            {!isDates ? (
              <ScrollView horizontal>
                {["exact", "1 day", "2 days", "3 days", "5 days"].map((option) => (
                  <TouchableOpacity
                    key={option}
                    style={[
                      styles.extender,
                      selectedDateExtender === option && styles.extenderSelected,
                    ]}
                    onPress={() => setSelectedDateExtender(option)}
                  >
                    {option === "exact" ? (
                      <Text>exact dates</Text>
                    ) : (
                      <>
                        <Image
                          source={selectedDateExtender === option ? PlusMinusWhite : PlusMinus}
                          style={styles.icon}
                        />
                        <Text>{option}</Text>
                      </>
                    )}
                  </TouchableOpacity>
                ))}
              </ScrollView>
            ) : (
              <Text>Flexible mode</Text>
            )}
            <CustomButton onPress={onClose} label="Done" />
          </View>
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 10 },
  timeRangeBox: { flexDirection: "row", justifyContent: "space-between", padding: 10 },
  label: { fontWeight: "bold" },
  dateRangeInfo: { flexDirection: "row" },
  rangeDisplay: { marginHorizontal: 5 },
  unselected: { color: "#aaa" },
  separator: { marginHorizontal: 5 },
  title: { fontSize: 16, marginVertical: 10 },
  customCalendar: { borderWidth: 1, borderRadius: 8, padding: 10 },
  dayNames: { flexDirection: "row", justifyContent: "space-between" },
  dayName: { width: screenWidth / 7, textAlign: "center" },
  scrollWrapper: { height: 300 },
  monthsContainer: { flexDirection: "column" },
  monthContainer: { marginVertical: 10 },
  lastMonth: { marginBottom: 40 },
  calendarHeader: { fontWeight: "bold", marginBottom: 5, textAlign: "center" },
  calendarDays: { flexDirection: "row", flexWrap: "wrap" },
  tightRows: {},
  veryTightRows: {},
  footer: { marginTop: 10 },
  extender: { padding: 8, margin: 5, borderRadius: 5, backgroundColor: "#eee" },
  extenderSelected: { backgroundColor: "blue" },
  icon: { width: 16, height: 16, marginRight: 5 },
  monthList: { maxHeight: 200 },
  monthOption: { padding: 10, borderBottomWidth: 1 },
  selected: { backgroundColor: "#ddd" },
  dayEmpty: {
    width: screenWidth / 7,
    height: 40,
    marginVertical: 2,
  },
});

export default CustomCalendar;
