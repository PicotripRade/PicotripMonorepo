import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { removeTextInBrackets } from "@picotrip/shared";

const FlightSegment = ({ segment }) => {
  return (
    <View style={styles.segment}>
      {/* Airline header */}
      <View style={styles.header}>
        <Text style={styles.headerText}>
          {removeTextInBrackets(segment?.["airline:"])} ({segment?.airlineCode})
        </Text>
      </View>

      {/* Flight body */}
      <View style={styles.body}>
        {/* Departure */}
        <View style={styles.point}>
          <Text style={styles.code}>{segment?.departure}</Text>
          <Text style={styles.time}>{segment?.departureTime}</Text>
        </View>

        {/* Line */}
        <View style={styles.line} />

        {/* Arrival */}
        <View style={styles.point}>
          <Text style={styles.code}>{segment?.arrival}</Text>
          <Text style={styles.time}>{segment?.arrivalTime}</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  segment: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    marginVertical: 8,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    marginBottom: 8,
  },
  headerText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
  },
  body: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  point: {
    alignItems: "center",
    flex: 1,
  },
  code: {
    fontSize: 16,
    fontWeight: "700",
    color: "#222",
  },
  time: {
    fontSize: 14,
    color: "#555",
  },
  line: {
    flex: 0.5,
    height: 1,
    backgroundColor: "#ccc",
    marginHorizontal: 8,
  },
});

export default FlightSegment;
