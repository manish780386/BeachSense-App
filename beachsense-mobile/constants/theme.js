export const COLORS = {
  deep: "#065A82",
  teal: "#1C7293",
  mid: "#21295C",
  white: "#FFFFFF",
  offWhite: "#F4F8FA",
  gray: "#5B6B73",
  darkText: "#16232A",
  border: "#DDE6EA",

  // Suitability status colours — used consistently across map markers,
  // badges and detail screens
  suitable: "#2E9E5B",
  caution: "#F2A93B",
  notSuitable: "#F04C4C",
};

export const STATUS_CONFIG = {
  SUITABLE: { label: "Suitable", color: COLORS.suitable, icon: "checkmark-circle" },
  CAUTION: { label: "Caution", color: COLORS.caution, icon: "warning" },
  NOT_SUITABLE: { label: "Not Suitable", color: COLORS.notSuitable, icon: "close-circle" },
};

export function getStatusConfig(status) {
  return STATUS_CONFIG[status] || { label: "Unknown", color: COLORS.gray, icon: "help-circle" };
}