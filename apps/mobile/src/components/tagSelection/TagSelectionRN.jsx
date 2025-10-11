import React, { forwardRef } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native";
import { useSelector } from "react-redux";

// If you use react-native-svg-transformer, you can import SVGs like this:
import SkiingIcon from "@picotrip/shared/assets/images/tags/ski-svgrepo-com.svg";
import SummerVacationIcon from "@picotrip/shared/assets/images/tags/summer-svgrepo-com.svg";
import HikingIcon from "@picotrip/shared/assets/images/tags/hiking-svgrepo-com-2.svg";
import FamilyTripIcon from "@picotrip/shared/assets/images/tags/family-svgrepo-com.svg";
import LakesIcon from "@picotrip/shared/assets/images/tags/lake-svgrepo-com.svg";
import ParachuteIcon from "@picotrip/shared/assets/images/tags/parachute-svgrepo-com.svg";
import CavingIcon from "@picotrip/shared/assets/images/tags/underground-cave-svgrepo-com.svg";
import MountainIcon from "@picotrip/shared/assets/images/tags/mountain-svgrepo-com.svg";

import Tag from "./TagRN";
import CustomNextButton from "../buttons/CustomButtonRN"; // <-- RN version of your Tag component


const TagSelection = forwardRef(({ onSearchClick, selectedTag, onTagChange }, ref) => {
  const tagsExpanded = useSelector((state) => state.tripOrganisation.isTagsExpanded);

  const handleTagClick = (tagId) => {
    if (selectedTag === tagId) {
      if (onTagChange) onTagChange(null);
    } else {
      if (onTagChange) onTagChange(tagId);
    }
  };

  const tags = [
    { id: "skiing", icon: SkiingIcon, alt: "Skiing" },
    { id: "summer_vacation", icon: SummerVacationIcon, alt: "Summer Vacation" },
    { id: "hiking", icon: HikingIcon, alt: "Hiking" },
    { id: "mountains", icon: MountainIcon, alt: "Mountains" },
    { id: "family_trip", icon: FamilyTripIcon, alt: "Family Trip" },
    { id: "lakes", icon: LakesIcon, alt: "Lakes" },
    { id: "parachuting", icon: ParachuteIcon, alt: "Parachuting" },
    { id: "caving", icon: CavingIcon, alt: "Caving" },
  ];

  if (tagsExpanded) {
    return (
      <View style={[styles.container, styles.expanded]}>
        <Text style={styles.title}>What you want to do?</Text>

        <View style={styles.tagsContainer}>
          {tags.map((tag) => (
            <Tag
              key={tag.id}
              id={tag.id}
              icon={tag.icon}
              alt={tag.alt}
              onPress={() => handleTagClick(tag.id)}
              isSelected={tag.id === selectedTag}
              ref={ref}
            />
          ))}
        </View>

        <View style={styles.emptySpace} />

        <View style={styles.inputNavigation}>
          <CustomNextButton label="Search" onPress={onSearchClick} color="nav-color" />
        </View>
      </View>
    );
  } else {
    return (
      <View style={[styles.container, styles.collapsed]}>
        <View style={styles.disabledBox}>
          <Text style={styles.disabledText}>What</Text>
        </View>

        <View style={[styles.activityTag, !selectedTag && styles.unselected]}>
          {!selectedTag ? (
            <Text style={styles.placeholder}>Type of activity</Text>
          ) : (
            <Text style={styles.selectedText}>{selectedTag}</Text>
          )}
        </View>
      </View>
    );
  }
});

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    padding: 10,
    backgroundColor: "#fff",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 3,
    elevation: 3,
  },
  expanded: {
    marginBottom: 10,
  },
  collapsed: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 10,
    justifyContent: "space-between",
  },
  title: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 10,
  },
  tagsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  emptySpace: {
    height: 20,
  },
  inputNavigation: {
    marginTop: 10,
  },
  disabledBox: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: "#f2f2f2",
    marginRight: 8,
  },
  disabledText: {
    color: "#888",
    fontWeight: "500",
  },
  activityTag: {
    flex: 1,
    padding: 8,
    borderRadius: 8,
    backgroundColor: "#f2f2f2",
  },
  unselected: {
    backgroundColor: "#fafafa",
  },
  placeholder: {
    color: "#aaa",
  },
  selectedText: {
    fontWeight: "600",
    color: "#333",
  },
});

export default TagSelection;
