import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";

import HomeScreen from "../screens/HomeScreen.js";
import MapScreen from "../screens/MapScreen";
import AlertsScreen from "../screens/AlertsScreen";
import BeachDetailScreen from "../screens/BeachDetailScreen";
import { COLORS } from "../constants/theme";

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function Tabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerStyle: { backgroundColor: COLORS.deep },
        headerTintColor: COLORS.white,
        tabBarActiveTintColor: COLORS.deep,
        tabBarInactiveTintColor: COLORS.gray,
        tabBarIcon: ({ color, size }) => {
          const icons = { Home: "home", Map: "map", Alerts: "notifications" };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: "BeachSense" }} />
      <Tab.Screen name="Map" component={MapScreen} />
      <Tab.Screen name="Alerts" component={AlertsScreen} />
    </Tab.Navigator>
  );
}

export default function RootNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: COLORS.deep }, headerTintColor: COLORS.white }}>
      <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />
      <Stack.Screen
        name="BeachDetail"
        component={BeachDetailScreen}
        options={({ route }) => ({ title: route.params?.beachName || "Beach Detail" })}
      />
    </Stack.Navigator>
  );
}