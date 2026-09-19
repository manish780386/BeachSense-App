import { useEffect } from "react";
import { useDispatch } from "react-redux";
import * as Location from "expo-location";
import { setUserLocation, setPermissionGranted } from "../redux/slices/locationSlice";

export function useUserLocation() {
  const dispatch = useDispatch();

  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      dispatch(setPermissionGranted(status === "granted"));

      if (status !== "granted") return;

      const position = await Location.getCurrentPositionAsync({});
      dispatch(
        setUserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        })
      );
    })();
  }, [dispatch]);
}