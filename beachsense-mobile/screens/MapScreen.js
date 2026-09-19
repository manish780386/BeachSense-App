import React from "react";
import { View, StyleSheet, ActivityIndicator, Text } from "react-native";
import MapView, { Marker, Callout } from "react-native-maps";
import { useNavigation } from "@react-navigation/native";
import { useBeaches } from "../services/beachHooks";
import { getStatusConfig, COLORS } from "../constants/theme";

const INDIA_INITIAL_REGION = {
  latitude: 15.5,
  longitude: 77.5,
  latitudeDelta: 18,
  longitudeDelta: 18,
};

export default function MapScreen() {
  const navigation = useNavigation();
  const { data: beaches, isLoading } = useBeaches();

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={COLORS.deep} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <MapView style={StyleSheet.absoluteFill} initialRegion={INDIA_INITIAL_REGION}>
        {beaches?.map((beach) => {
          const config = getStatusConfig(beach.current_status?.status);
          return (
            <Marker
              key={beach.id}
              coordinate={{ latitude: beach.latitude, longitude: beach.longitude }}
              pinColor={config.color}
              onCalloutPress={() =>
                navigation.navigate("BeachDetail", { beachId: beach.id, beachName: beach.name })
              }
            >
              <Callout>
                <View style={{ maxWidth: 180 }}>
                  <Text style={{ fontWeight: "700" }}>{beach.name}</Text>
                  <Text style={{ color: config.color, fontWeight: "600" }}>{config.label}</Text>
                  <Text style={{ fontSize: 11, color: COLORS.gray }}>Tap for details</Text>
                </View>
              </Callout>
            </Marker>
          );
        })}
      </MapView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
});