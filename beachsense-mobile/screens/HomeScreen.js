import React from "react";
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from "react-native";
import { useNavigation } from "@react-navigation/native";
import BeachCard from "../components/BeachCard";
import { useBeaches } from "../services/beachHooks";
import { COLORS } from "../constants/theme";

export default function HomeScreen() {
  const navigation = useNavigation();
  const { data: beaches, isLoading, isError, refetch, isRefetching } = useBeaches();

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={COLORS.deep} />
        <Text style={styles.loadingText}>Loading beaches...</Text>
      </View>
    );
  }

  if (isError) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Couldn't reach the BeachSense server.</Text>
        <Text style={styles.errorSubText}>Check that the Django backend is running.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={beaches}
        keyExtractor={(item) => String(item.id)}
        onRefresh={refetch}
        refreshing={isRefetching}
        contentContainerStyle={{ paddingVertical: 12 }}
        ListEmptyComponent={
          <View style={styles.center}>
            <Text style={styles.errorText}>No beaches found. Run the seed_beaches command.</Text>
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
  center: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24, gap: 8 },
  loadingText: { color: COLORS.gray, marginTop: 8 },
  errorText: { color: COLORS.darkText, fontWeight: "600", textAlign: "center" },
  errorSubText: { color: COLORS.gray, fontSize: 12.5, textAlign: "center" },
});