import apiClient from "./apiClient";

/** GET /api/beaches/ — list all beaches with latest suitability status */
export async function fetchAllBeaches() {
  const { data } = await apiClient.get("/beaches/");
  return data;
}

/** GET /api/beaches/{id}/ — beach detail with raw ocean parameters */
export async function fetchBeachDetail(beachId) {
  const { data } = await apiClient.get(`/beaches/${beachId}/`);
  return data;
}

/** GET /api/beaches/nearby/?lat=&lng=&radius_km= */
export async function fetchNearbyBeaches(lat, lng, radiusKm = 15) {
  const { data } = await apiClient.get("/beaches/nearby/", {
    params: { lat, lng, radius_km: radiusKm },
  });
  return data;
}