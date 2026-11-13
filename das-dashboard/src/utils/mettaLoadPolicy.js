const METTA_LOAD_ALLOWED_TYPES = new Set(["redismongodb", "morkdb"]);

const UNSUPPORTED_TOOLTIP =
  "MeTTa load is disabled for this AtomDB type. Only Redis + MongoDB and Mork + MongoDB can be loaded for now.";

export function getMettaLoadAvailability(
  atomdbType,
  { atomDbOnline, isServerOffline, actionLocked }
) {
  if (!atomdbType) {
    return { canLoad: false, tooltip: "Save a configuration before loading MeTTa." };
  }
  if (!METTA_LOAD_ALLOWED_TYPES.has(atomdbType)) {
    return { canLoad: false, tooltip: UNSUPPORTED_TOOLTIP };
  }
  if (isServerOffline) {
    return { canLoad: false, tooltip: "Select an online server to load MeTTa." };
  }
  if (!atomDbOnline) {
    return { canLoad: false, tooltip: "Start AtomDB on this server before loading MeTTa." };
  }
  if (actionLocked) {
    return { canLoad: false, tooltip: "Wait for the current action to finish." };
  }
  return {
    canLoad: true,
    tooltip: "Upload and load a .metta file on the selected server.",
  };
}
