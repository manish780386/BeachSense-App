import { useQuery } from "@tanstack/react-query";
import { fetchAllBeaches, fetchBeachDetail, fetchNearbyBeaches } from "../services/beachApi";

export function useBeaches() {
  return useQuery({
    queryKey: ["beaches"],
    queryFn: fetchAllBeaches,
  });
}

export function useBeachDetail(beachId) {
  return useQuery({
    queryKey: ["beach", beachId],
    queryFn: () => fetchBeachDetail(beachId),
    enabled: !!beachId,
  });
}

export function useNearbyBeaches(lat, lng, radiusKm = 15) {
  return useQuery({
    queryKey: ["nearbyBeaches", lat, lng, radiusKm],
    queryFn: () => fetchNearbyBeaches(lat, lng, radiusKm),
    enabled: !!lat && !!lng,
  });
}