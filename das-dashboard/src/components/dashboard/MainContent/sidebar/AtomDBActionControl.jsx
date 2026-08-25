import { useState } from "react";
import { CircularProgress, ListItemIcon, ListItemText } from "@mui/material";
import { PlayArrow, Stop } from "@mui/icons-material";

import { StyledItem } from "./sidebar.styled";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { startDatabases, stopDatabases } from "../../../../api/ServicesAPI";
import { getConfigDefaults } from "../../../../api/ConfigAPI";
import { extractApiError } from "../../../../api/APIUtils";

const LOADING_KEYS = ["start-database", "stop-database"];

const ATOMDB_TYPE_LABELS = {
  redismongodb: "Redis + MongoDB",
  morkdb: "Mork + MongoDB",
  inmemorydb: "In-Memory",
  remotedb: "RemoteDB",
  adapterdb: "AdapterDB",
};

export function AtomDBActionControl({
  atomDbOnline,
  isServerOffline,
  disabled = false,
  onBusyChange,
  onActionComplete,
}) {
  const [loadingAction, setLoadingAction] = useState(null);

  const { currentMachine, machines } = useDashboardContext();
  const { showToast } = useToast();
  const { showConfirm } = useDialog();

  const currentHost = currentMachine?.serverIp;
  const isLoading = LOADING_KEYS.includes(loadingAction);

  const setBusy = (actionKey) => {
    setLoadingAction(actionKey);
    onBusyChange?.(!!actionKey);
  };

  const executeAsyncAction = async (actionKey, action, successMessage, errorMessage) => {
    try {
      setBusy(actionKey);
      await action();
      try {
        await onActionComplete?.();
      } catch (refreshError) {
        console.error("Failed to refresh sidebar status after action:", refreshError);
      }
      showToast({ message: successMessage, severity: "success" });
    } catch (err) {
      console.error(errorMessage, err);
      const { message, details, severity } = extractApiError(err, errorMessage);
      showToast({ message, severity, details });
    } finally {
      setBusy(null);
    }
  };

  const handleDatabaseAction = async () => {
    if (atomDbOnline) {
      showConfirm({
        title: "Stop AtomDB",
        message: "Are you sure you want to stop the AtomDB?\n\nAll components will be stopped, so any data they may be carrying will be lost.",
        onConfirm: () => executeAsyncAction(
          "stop-database",
          () => stopDatabases(currentHost),
          "AtomDB stopped successfully.",
          "Failed to stop AtomDB."
        )
      });
      return;
    }

    let atomdbType;
    try {
      const defaults = await getConfigDefaults();
      atomdbType = defaults?.content?.atomdb?.atomdb_type;
    } catch (error) {
      console.error("Failed to load AtomDB type for confirmation:", error);
    }

    const typeLabel = ATOMDB_TYPE_LABELS[atomdbType] ?? atomdbType ?? "AtomDB";
    const serversList = machines.map((machine) => machine.serverIp).filter(Boolean).join(", ")
      || "configured servers";

    showConfirm({
      title: "Start AtomDB",
      message:
        `An ${typeLabel} AtomDB will be started in the servers: ${serversList}. ` +
        "Any AtomDB component running on these machines will be re-started " +
        "so any data they may be carrying will be lost.",
      onConfirm: () => executeAsyncAction(
        "start-database",
        () => startDatabases(currentHost),
        "AtomDB started successfully.",
        "Failed to start AtomDB."
      )
    });
  };

  return (
    <StyledItem
      disabled={disabled || isLoading || isServerOffline}
      onClick={() => !disabled && !isLoading && !isServerOffline && handleDatabaseAction()}
    >
      <ListItemIcon>
        {isLoading ? (
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
