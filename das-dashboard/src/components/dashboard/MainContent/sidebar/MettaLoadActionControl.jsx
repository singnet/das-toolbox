import { useRef, useState } from "react";
import { CircularProgress, ListItemIcon, ListItemText, Tooltip } from "@mui/material";
import { Storage } from "@mui/icons-material";

import { StyledItem } from "./sidebar.styled";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { uploadMettaFile, loadMettaFile } from "../../../../api/AtomDBAPI";
import { extractApiError } from "../../../../api/APIUtils";
import { getMettaLoadAvailability } from "../../../../utils/mettaLoadPolicy";

const LOADING_KEYS = ["load-metta", "overwrite-metta", "load-existing-metta", "upload-metta"];

export function MettaLoadActionControl({
  atomdbType,
  atomDbOnline,
  isServerOffline,
  disabled = false,
  onBusyChange,
  onActionComplete,
}) {
  const [loadingAction, setLoadingAction] = useState(null);
  const mettaInputRef = useRef(null);

  const { currentMachine } = useDashboardContext();
  const { showToast } = useToast();
  const { showConfirm } = useDialog();

  const currentHost = currentMachine?.serverIp;
  const isLoading = LOADING_KEYS.includes(loadingAction);
  const actionLocked = disabled && !isLoading;

  const { canLoad, tooltip } = getMettaLoadAvailability(atomdbType, {
    atomDbOnline,
    isServerOffline,
    actionLocked,
  });

  const isDisabled = !canLoad || isLoading || isServerOffline || actionLocked;

  const setBusy = (actionKey) => {
    setLoadingAction(actionKey);
    onBusyChange?.(!!actionKey);
  };

  const refreshAfterLoad = async () => {
    try {
      await onActionComplete?.();
    } catch (refreshError) {
      console.error("Failed to refresh sidebar status after MeTTa load:", refreshError);
    }
  };

  const executeAsyncAction = async (actionKey, action, successMessage, errorMessage) => {
    try {
      setBusy(actionKey);
      await action();
      await refreshAfterLoad();
      showToast({ message: successMessage, severity: "success" });
    } catch (err) {
      console.error(errorMessage, err);
      const { message, details, severity } = extractApiError(err, errorMessage);
      showToast({ message, severity, details });
    } finally {
      setBusy(null);
    }
  };

  const handleMettaUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const hostSnapshot = currentHost;
    let reachedLoadStep = false;

    try {
      setBusy("upload-metta");
      const uploadResponse = await uploadMettaFile(hostSnapshot, false, file);

      setBusy("load-metta");
      reachedLoadStep = true;
      await loadMettaFile(hostSnapshot, uploadResponse.saved_path);
      await refreshAfterLoad();
      showToast({ message: "MeTTa database loaded successfully.", severity: "success" });
    } catch (err) {
      const responseData = err?.response?.data;

      if (err?.response?.status === 409 && responseData?.file_path) {
        const existingFilePath = responseData.file_path;

        showConfirm({
          title: "File already exists",
          message: `The file "${file.name}" already exists on the server.\n\nDo you want to OVERWRITE it? (Click CANCEL to safely load the existing server file instead).`,
          onConfirm: () => {
            executeAsyncAction(
              "overwrite-metta",
              async () => {
                const res = await uploadMettaFile(hostSnapshot, true, file);
                await loadMettaFile(hostSnapshot, res.saved_path);
              },
              "MeTTa file overwritten and loaded successfully.",
              "Failed to overwrite or load MeTTa file."
            );
          },
          onCancel: () => {
            executeAsyncAction(
              "load-existing-metta",
              async () => {
                await loadMettaFile(hostSnapshot, existingFilePath);
              },
              "Existing MeTTa file loaded successfully.",
              "Failed to load existing MeTTa file."
            );
          },
        });
      } else {
        const fallback = reachedLoadStep
          ? "Failed to load MeTTa file into the database."
          : "Failed to upload MeTTa file to the server.";
        const { message, details, severity } = extractApiError(err, fallback);
        showToast({ message, severity, details });
      }
    } finally {
      setBusy(null);
      if (event.target) event.target.value = "";
    }
  };

  const openFilePicker = () => {
    if (!canLoad || isLoading) return;

    const targetHost = currentHost || "the selected server";
    showConfirm({
      title: "Load MeTTa Database",
      message:
        `Load on ${targetHost} using the dashboard's saved AtomDB configuration.\n\n` +
        "The file is uploaded to that server, then das-cli metta load runs there.",
      onConfirm: () => mettaInputRef.current?.click(),
    });
  };

  const listItem = (
    <StyledItem disabled={isDisabled} onClick={openFilePicker}>
      <ListItemIcon>
        {isLoading ? <CircularProgress size={16} /> : <Storage />}
      </ListItemIcon>
      <ListItemText primary="Load MeTTa Database" />
    </StyledItem>
  );

  return (
    <>
      <input
        ref={mettaInputRef}
        type="file"
        accept=".metta"
        hidden
        onChange={handleMettaUpload}
      />

      <Tooltip title={tooltip} placement="right" arrow describeChild>
        <span style={{ display: "block" }}>{listItem}</span>
      </Tooltip>
    </>
  );
}
