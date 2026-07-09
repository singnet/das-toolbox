import { useState } from "react";
import { CircularProgress, ListItemIcon, ListItemText } from "@mui/material";
import { PlayArrow, Stop } from "@mui/icons-material";

import { StyledItem } from "./sidebar.styled";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { startDatabases, stopDatabases } from "../../../../api/ServicesAPI";
import { extractErrorDetails } from "../../../../api/APIUtils";

const LOADING_KEYS = ["start-database", "stop-database"];

export function AtomDBActionControl({
  atomDbOnline,
  isServerOffline,
  disabled = false,
  onBusyChange,
}) {
  const [loadingAction, setLoadingAction] = useState(null);

  const { currentMachine } = useDashboardContext();
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
      showToast({ message: successMessage, severity: "success" });
    } catch (err) {
      console.error(errorMessage, err);
      showToast({ message: errorMessage, severity: "error", details: extractErrorDetails(err) });
    } finally {
      setBusy(null);
    }
  };

  const handleDatabaseAction = () => {
    if (atomDbOnline) {
      showConfirm({
        title: "Stop AtomDB",
        message: "Are you sure you want to stop AtomDB?\n\nAll in-memory data may be lost.",
        onConfirm: () => executeAsyncAction(
          "stop-database",
          () => stopDatabases(currentHost),
          "AtomDB stopped successfully.",
          "Failed to stop AtomDB."
        )
      });
      return;
    }

    showConfirm({
      title: "Start AtomDB",
      message: "Do you want to start AtomDB?",
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
