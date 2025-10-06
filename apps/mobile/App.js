// App.js - TEMPORARY MINIMAL VERSION

import React from 'react';
import { View, Text } from 'react-native';

// 🛑 REMOVE all imports below this line (temporarily)
// import { Provider } from 'react-redux';
// import { NavigationContainer } from '@react-navigation/native';
// import { createNativeStackNavigator } from '@react-navigation/native-stack';
// import store from '../../packages/shared/src/store/store.js';
// import { enableScreens } from 'react-native-screens';
// enableScreens();

// Simple placeholder screen
function HomeScreen() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text style={{ fontSize: 20 }}>✅ App is running and imports are minimal!</Text>
    </View>
  );
}

export default function App() {
  return <HomeScreen />;
}