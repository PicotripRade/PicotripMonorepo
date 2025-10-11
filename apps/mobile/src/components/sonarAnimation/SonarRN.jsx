import React from "react";
import { View, Image, StyleSheet } from "react-native";
import sonarPath from "@picotrip/shared/assets/images/tags/mountain-svgrepo-com.svg";

const RadarScan = () => {
  return (
    <View style={styles.container}>
      {/* Distance circles */}
      <View style={styles.distance}>
        {[...Array(5)].map((_, i) => (
          <View key={i} style={styles.distanceCircle} />
        ))}
      </View>

      {/* Matrix layer */}
      <View style={styles.matrix} />

      {/* Rotary layer (can be animated later) */}
      <View style={styles.rotary} />

      {/* Display ships and peak */}
      <View style={styles.display}>
        <View style={styles.ship1} />
        <View style={styles.ship2} />
        <View style={styles.ship3} />
        <View style={styles.peak}>
          <Image source={sonarPath} style={styles.peakImage} />
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: 250,
    height: 250,
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
  },
  distance: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
  },
  distanceCircle: {
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 1,
    borderColor: "#00ff00",
    position: "absolute",
  },
  matrix: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,255,0,0.05)",
    borderRadius: 125,
  },
  rotary: {
    ...StyleSheet.absoluteFillObject,
    borderWidth: 2,
    borderColor: "rgba(0,255,0,0.2)",
    borderRadius: 125,
  },
  display: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
  },
  ship1: {
    width: 10,
    height: 10,
    backgroundColor: "red",
    position: "absolute",
    top: 30,
    left: 60,
    borderRadius: 5,
  },
  ship2: {
    width: 10,
    height: 10,
    backgroundColor: "blue",
    position: "absolute",
    top: 100,
    right: 50,
    borderRadius: 5,
  },
  ship3: {
    width: 10,
    height: 10,
    backgroundColor: "yellow",
    position: "absolute",
    bottom: 40,
    left: 90,
    borderRadius: 5,
  },
  peak: {
    width: 40,
    height: 40,
    justifyContent: "center",
    alignItems: "center",
  },
  peakImage: {
    width: 40,
    height: 40,
    resizeMode: "contain",
  },
});

export default RadarScan;
