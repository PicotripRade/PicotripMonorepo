import React, { forwardRef } from "react";
import { View, Text, Image, TouchableOpacity, StyleSheet } from "react-native";

const Tag = forwardRef(({ id, icon, alt, onClick, isSelected }, ref) => {
  const handleClick = () => {
    onClick(id);
  };

  return (
    <TouchableOpacity onPress={handleClick} activeOpacity={0.7}>
      <View style={[styles.textWrapper, isSelected && styles.selectedWrapper]}>
        <View style={[styles.tag, isSelected && styles.selectedTag]}>
          <Image
            ref={ref}
            source={typeof icon === "string" ? { uri: icon } : icon}
            style={styles.tagIcon}
            resizeMode="contain"
          />
        </View>
        <Text style={styles.textTag}>{alt}</Text>
      </View>
    </TouchableOpacity>
  );
});

const styles = StyleSheet.create({
  textWrapper: {
    alignItems: "center",
    margin: 6,
  },
  selectedWrapper: {
    opacity: 0.9,
  },
  tag: {
    width: 64,
    height: 64,
    borderRadius: 16,
    backgroundColor: "#f0f0f0",
    justifyContent: "center",
    alignItems: "center",
    shadowColor: "#000",
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 3,
  },
  selectedTag: {
    backgroundColor: "#007AFF",
  },
  tagIcon: {
    width: 40,
    height: 40,
  },
  textTag: {
    marginTop: 6,
    fontSize: 14,
    textAlign: "center",
    color: "#333",
  },
});

export default Tag;
