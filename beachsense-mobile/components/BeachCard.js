import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import StatusBadge from "./StatusBadge";
import { COLORS } from "../constants/theme";

export default function BeachCard({ beach, onPress }) {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.left}>
        <Text style={styles.name}>{beach.name}</Text>
        <Text style={styles.location}>
          {beach.district ? `${beach.district}, ` : ""}
          {beach.state}
        </Text>
        <StatusBadge status={beach.current_status?.status} size="small" />
      </View>
      <Ionicons name="chevron-forward" size={22} color={COLORS.gray} />
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 14,
    marginHorizontal: 16,
    marginVertical: 6,
    borderWidth: 1,
    borderColor: COLORS.border,
    gap: 8,
  },
  left: { flex: 1, gap: 6 },
  name: { fontSize: 16, fontWeight: "700", color: COLORS.darkText },
  location: { fontSize: 12.5, color: COLORS.gray },
});