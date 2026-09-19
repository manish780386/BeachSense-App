import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { getStatusConfig, COLORS } from "../constants/theme";

export default function StatusBadge({ status, size = "medium" }) {
  const config = getStatusConfig(status);
  const isSmall = size === "small";

  return (
    <View style={[styles.badge, { backgroundColor: config.color }, isSmall && styles.badgeSmall]}>
      <Ionicons name={config.icon} size={isSmall ? 12 : 16} color={COLORS.white} />
      <Text style={[styles.text, isSmall && styles.textSmall]}>{config.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: 20,
    paddingVertical: 6,
    paddingHorizontal: 12,
    gap: 6,
    alignSelf: "flex-start",
  },
  badgeSmall: { paddingVertical: 3, paddingHorizontal: 8, gap: 4 },
  text: { color: COLORS.white, fontWeight: "600", fontSize: 13 },
  textSmall: { fontSize: 11 },
});