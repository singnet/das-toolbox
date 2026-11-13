import { CircularProgress, ListItemIcon, ListItemText } from "@mui/material";
import { PlayArrow, Stop } from "@mui/icons-material";

import { StyledItem } from "./sidebar.styled";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { startDatabases, stopDatabases } from "../../../../api/ServicesAPI";
import { useSidebarAction } from "./useSidebarAction";

const ATOMDB_TYPE_LABELS = {
  redismongodb: "Redis + MongoDB",
  morkdb: "Mork + MongoDB",
  inmemorydb: "In-Memory",
  remotedb: "RemoteDB",
  adapterdb: "AdapterDB",
};

export function AtomDBActionControl({
  atomdbType,
  atomDbOnline,
  isServerOffline,
  disabled = false,
  onBusyChange,
  onActionComplete,
}) {
  const { currentMachine } = useDashboardContext();
  const { showConfirm } = useDialog();
  const { busy, run } = useSidebarAction({ onBusyChange, onActionComplete });

  const currentHost = currentMachine?.serverIp;

  const handleDatabaseAction = async () => {
    if (atomDbOnline) {
      showConfirm({
        title: "Stop AtomDB",
        message: "Are you sure you want to stop the AtomDB?\n\nAll components will be stopped, so any data they may be carrying will be lost.",
        onConfirm: () => run(
          () => stopDatabases(currentHost),
          "AtomDB stopped successfully.",
          "Failed to stop AtomDB."
        )
      });
      return;
    }

    const localHost = !currentHost || ["localhost", "127.0.0.1", "0.0.0.0"].includes(currentHost);
    const remoteTopology = atomdbType === "remotedb" && localHost;
    const displayedType = atomdbType === "remotedb" && !localHost ? "redismongodb" : atomdbType;
    const typeLabel = ATOMDB_TYPE_LABELS[displayedType] ?? displayedType ?? "AtomDB";
    const targetHost = currentHost || "the selected server";

    showConfirm({
      title: "Start AtomDB",
      message: remoteTopology
        ? "Start Redis + MongoDB on each configured local or remote peer? Components already running will be kept."
        : `Start ${typeLabel} on ${targetHost}? Components already running will be kept.`,
      onConfirm: () => run(
        () => startDatabases(currentHost),
        "AtomDB started successfully.",
        "Failed to start AtomDB."
      )
    });
  };

  return (
    <StyledItem
      disabled={disabled || busy || isServerOffline}
      onClick={() => !disabled && !busy && !isServerOffline && handleDatabaseAction()}
    >
      <ListItemIcon>
        {busy ? (
          <CircularProgress size={16} />
        ) : atomDbOnline ? (
          <Stop />
        ) : (
          <PlayArrow />
        )}
      </ListItemIcon>
      <ListItemText primary={atomDbOnline ? "Stop AtomDB" : "Start AtomDB"} />
    </StyledItem>
  );
}
