import React, { useEffect } from "react";
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from "react-native";
import { useSelector } from "react-redux";
import { useNavigation } from "@react-navigation/native";
import BeachCard from "../components/BeachCard";
import { useUserLocation } from "../utils/useUserLocation";
import { useNearbyBeaches } from "../services/beachHooks";
import { COLORS } from "../constants/theme";

export default function AlertsScreen() {
  useUserLocation(); // requests permission + populates redux location on mount
  const navigation = useNavigation();
  const { latitude, longitude, permissionGranted } = useSelector((state) => state.location);
  const { data: nearbyBeaches, isLoading } = useNearbyBeaches(latitude, longitude, 15);

  if (!permissionGranted) {
    return (
      <View style={styles.center}>
        <Text style={styles.infoText}>
          Location permission is needed to show alerts for beaches near you.
        </Text>
      </View>
    );
  }

  if (isLoading || !latitude) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={COLORS.deep} />
      </View>
    );
  }

  const riskyBeaches = (nearbyBeaches || []).filter(
    (b) => b.current_status?.status && b.current_status.status !== "SUITABLE"
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Beaches near you needing caution</Text>
      <FlatList
        data={riskyBeaches}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={{ paddingBottom: 12 }}
        ListEmptyComponent={
          <View style={styles.center}>
            <Text style={styles.infoText}>No active hazard alerts near your location right now.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <BeachCard
            beach={item}
            onPress={() => navigation.navigate("BeachDetail", { beachId: item.id, beachName: item.name })}
          />
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.offWhite },
  center: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24 },
  header: { fontSize: 14, fontWeight: "600", color: COLORS.gray, padding: 16, paddingBottom: 4 },
  infoText: { color: COLORS.gray, textAlign: "center" },
});