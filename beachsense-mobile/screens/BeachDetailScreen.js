import React from "react";
import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from "react-native";
import { useRoute } from "@react-navigation/native";
import StatusBadge from "../components/StatusBadge";
import ParameterTile from "../components/ParameterTile";
import { useBeachDetail } from "../services/beachHooks";
import { COLORS } from "../constants/theme";

export default function BeachDetailScreen() {
  const route = useRoute();
  const { beachId } = route.params;
  const { data: beach, isLoading, isError } = useBeachDetail(beachId);

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={COLORS.deep} />
      </View>
    );
  }

  if (isError || !beach) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Couldn't load beach details.</Text>
      </View>
    );
  }

  const p = beach.parameters;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16, gap: 16 }}>
      <View style={styles.headerCard}>
        <Text style={styles.beachName}>{beach.name}</Text>
        <Text style={styles.location}>
          {beach.district ? `${beach.district}, ` : ""}
          {beach.state}
        </Text>
        <StatusBadge status={beach.current_status?.status} />
        {beach.current_status?.score != null && (
          <Text style={styles.score}>Suitability Score: {beach.current_status.score}/100</Text>
        )}
      </View>

      {p ? (
        <View style={styles.grid}>
          <ParameterTile icon="water" label="Wave Height" value={p.wave_height_m} unit="m" />
          <ParameterTile icon="cloudy" label="Wind Speed" value={p.wind_speed_kmph} unit="km/h" />
          <ParameterTile icon="navigate" label="Current Speed" value={p.current_speed_kmph} unit="km/h" />
          <ParameterTile icon="leaf" label="Water Quality" value={p.water_quality_index} unit="/100" />
        </View>
      ) : (
        <Text style={styles.errorText}>No live ocean data available yet for this beach.</Text>
      )}

      {(p?.tsunami_alert || p?.storm_surge_alert || p?.high_wave_alert) && (
        <View style={styles.alertBox}>
          <Text style={styles.alertTitle}>Active Hazard Alerts</Text>
          {p.tsunami_alert && <Text style={styles.alertItem}>Tsunami Alert</Text>}
          {p.storm_surge_alert && <Text style={styles.alertItem}>Storm Surge Alert</Text>}
          {p.high_wave_alert && <Text style={styles.alertItem}>High Wave Alert</Text>}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.offWhite },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  headerCard: { backgroundColor: COLORS.white, borderRadius: 14, padding: 16, gap: 8, borderWidth: 1, borderColor: COLORS.border },
  beachName: { fontSize: 22, fontWeight: "800", color: COLORS.darkText },
  location: { fontSize: 13, color: COLORS.gray, marginBottom: 4 },
  score: { fontSize: 13, color: COLORS.gray, marginTop: 4 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 12 },
  alertBox: { backgroundColor: "#FDECEC", borderRadius: 12, padding: 14, borderWidth: 1, borderColor: COLORS.notSuitable, gap: 4 },
  alertTitle: { fontWeight: "700", color: COLORS.notSuitable, marginBottom: 4 },
  alertItem: { color: COLORS.notSuitable, fontSize: 13 },
  errorText: { color: COLORS.gray, textAlign: "center" },
});