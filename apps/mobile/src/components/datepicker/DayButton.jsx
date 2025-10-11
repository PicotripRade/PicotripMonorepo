import React from "react";
import { TouchableOpacity, Text, StyleSheet } from "react-native";

const DatepickerDayButton = ({ day, isActive, isInRange, isDisabled, onPress }) => {
  return (
    <TouchableOpacity
      style={[
        styles.dayContainer,
        isActive && styles.active,
        isInRange && styles.inRange,
        isDisabled && styles.disabled
      ]}
      onPress={onPress}
      disabled={isDisabled}
    >
      <Text
        style={[
          styles.dayText,
          isActive && styles.activeText,
          isInRange && styles.inRangeText,
          isDisabled && styles.disabledText
        ]}
      >
        {day}
      </Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  dayContainer: {
    flex: 1,
    aspectRatio: 1, // keeps it square and flexible
    justifyContent: "center",
    alignItems: "center",
    margin: 2,
    borderRadius: 8,
    backgroundColor: "#fff",
  },
  dayText: {
    fontSize: 16,
    color: "#333",
  },
  active: {
    backgroundColor: "#007AFF",
  },
  activeText: {
    color: "#fff",
    fontWeight: "bold",
  },
  inRange: {
    backgroundColor: "#D6E9FF",
  },
  inRangeText: {
    color: "#007AFF",
  },
  disabled: {
    backgroundColor: "#f0f0f0",
  },
  disabledText: {
    color: "#999",
  },
});

export default DatepickerDayButton;
