import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { COLORS } from "../constants/theme";

export default function ParameterTile({ icon, label, value, unit }) {
  return (
    <View style={styles.tile}>
      <Ionicons name={icon} size={22} color={COLORS.deep} />
      <Text style={styles.value}>
        {value}
        {unit ? <Text style={styles.unit}> {unit}</Text> : null}
      </Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  tile: {
    flex: 1,
    minWidth: "45%",
    backgroundColor: COLORS.offWhite,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
    padding: 14,
    alignItems: "center",
    gap: 4,
  },
  value: { fontSize: 18, fontWeight: "700", color: COLORS.darkText, marginTop: 4 },
  unit: { fontSize: 12, fontWeight: "400", color: COLORS.gray },
  label: { fontSize: 11.5, color: COLORS.gray },
});