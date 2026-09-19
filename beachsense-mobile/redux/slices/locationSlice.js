import { createSlice } from "@reduxjs/toolkit";

const locationSlice = createSlice({
  name: "location",
  initialState: {
    latitude: null,
    longitude: null,
    permissionGranted: false,
  },
  reducers: {
    setUserLocation: (state, action) => {
      state.latitude = action.payload.latitude;
      state.longitude = action.payload.longitude;
    },
    setPermissionGranted: (state, action) => {
      state.permissionGranted = action.payload;
    },
  },
});

export const { setUserLocation, setPermissionGranted } = locationSlice.actions;
export default locationSlice.reducer;