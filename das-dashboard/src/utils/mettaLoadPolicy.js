export const METTA_LOAD_ALLOWED_TYPES = new Set(["redismongodb", "morkdb"]);

const BLOCKED_REASONS = {
  inmemorydb:
    "In-Memory AtomDB has no persistent store for MeTTa load.",
  remotedb:
    "RemoteDB MeTTa load is currently disabled.",
  adapterdb:
    "AdapterDB cannot be loaded via MeTTa load. Use Redis + MongoDB or Mork + MongoDB.",
};

export function getMettaLoadBlockedReason(atomdbType) {
  if (!atomdbType) {
    return "AtomDB type is unknown. Save a configuration before loading MeTTa.";
  }
  if (METTA_LOAD_ALLOWED_TYPES.has(atomdbType)) {
    return null;
  }
  return (
    BLOCKED_REASONS[atomdbType] ??
    `MeTTa load is not supported for AtomDB type "${atomdbType}".`
  );
}

export function isMettaLoadAllowed(atomdbType) {
  return METTA_LOAD_ALLOWED_TYPES.has(atomdbType);
}

export function getMettaLoadAvailability(
  atomdbType,
  { atomDbOnline, isServerOffline, actionLocked }
) {
  const blockedReason = getMettaLoadBlockedReason(atomdbType);
  if (blockedReason) {
    return { canLoad: false, tooltip: blockedReason };
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
    tooltip: "Upload and load a .metta file on the selected server (Redis + Mongo or Mork + Mongo).",
  };
}
