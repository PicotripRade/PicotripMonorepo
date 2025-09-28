import React from "react";
import { Text, View } from "react-native";
import UserDataEntryStep from "./src/components/steps/initialDataEntry/UserDataEntryStep";

export default function AppEntry() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <UserDataEntryStep></UserDataEntryStep>
    </View>
  );
}
