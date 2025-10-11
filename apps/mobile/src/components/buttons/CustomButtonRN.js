import React, { useState } from "react";
import { Text, TouchableOpacity, StyleSheet } from "react-native";

const CustomButton = ({ onPress, label }) => {
  const [isPressed, setIsPressed] = useState(false);

  const isReady = label === "Done";

  const handleClick = () => {
    setIsPressed(true);
    setTimeout(() => {
      setIsPressed(false);
    }, 300);
    onPress();
  };

  return (
    <TouchableOpacity
      style={[
        styles.button,
        isReady && styles.ready,
        isPressed && styles.pressed,
      ]}
      onPress={handleClick}
      activeOpacity={0.8}
    >
      <Text style={styles.label}>{label}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: "#2196F3", // main-color
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 25, // rounded-button
    alignItems: "center",
    justifyContent: "center",
    marginVertical: 8,
  },
  ready: {
    backgroundColor: "#4CAF50", // green if ready
  },
  pressed: {
    transform: [{ scale: 0.95 }],
  },
  label: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
});

export default CustomButton;
