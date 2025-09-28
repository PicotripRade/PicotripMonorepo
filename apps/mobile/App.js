import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text } from 'react-native';

// Import your component (mobile-specific version)
import UserDataEntryStep from './src/components/steps/initialDataEntry/UserDataEntryStep';

const Stack = createNativeStackNavigator();

export default function App() {
  // Analytics / scripts you used on web won’t run in RN.
  // But you can still hook into analytics libs like expo-tracking-transparency, firebase-analytics, etc.

  useEffect(() => {
    // Example placeholder for native analytics init
    console.log("App started (mobile)");
  }, []);

  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={UserDataEntryStep} />
        {/* You can add more screens like Search, Details, etc */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
