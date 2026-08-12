import { useRef, useState } from "react";
import { CircularProgress, ListItemIcon, ListItemText } from "@mui/material";
import { Storage } from "@mui/icons-material";

import { StyledItem } from "./sidebar.styled";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { uploadMettaFile, loadMettaFile } from "../../../../api/AtomDBAPI";
import { extractApiError } from "../../../../api/APIUtils";

const LOADING_KEYS = ["load-metta", "overwrite-metta", "load-existing-metta", "upload-metta"];

export function MettaLoadActionControl({
  isServerOffline,
  disabled = false,
  onBusyChange,
}) {
  const [loadingAction, setLoadingAction] = useState(null);
  const mettaInputRef = useRef(null);

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

    try {
      setBusy("upload-metta");
      const uploadResponse = await uploadMettaFile(hostSnapshot, false, file);

      setBusy("load-metta");
      await loadMettaFile(hostSnapshot, uploadResponse.saved_path);
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
              "Failed to overwrite MeTTa file."
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
          }
        });
      } else {
        const { message, details, severity } = extractApiError(err, "Failed to upload MeTTa database.");
        showToast({ message, severity, details });
      }
    } finally {
      setBusy(null);
      if (event.target) event.target.value = "";
    }
  };

  return (
    <>
      <input
        ref={mettaInputRef}
        type="file"
        accept=".metta"
        hidden
        onChange={handleMettaUpload}
      />

      <StyledItem
        disabled={disabled || isLoading || isServerOffline}
        onClick={() => !disabled && !isLoading && !isServerOffline && mettaInputRef.current?.click()}
      >
        <ListItemIcon>
          {isLoading ? <CircularProgress size={16} /> : <Storage />}
        </ListItemIcon>
        <ListItemText primary="Load MeTTa Database" />
      </StyledItem>
    </>
  );
}
