import { useRef } from "react";
import { CircularProgress, ListItemIcon, ListItemText, Tooltip } from "@mui/material";
import { Storage } from "@mui/icons-material";

import { StyledItem } from "./sidebar.styled";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useDialog } from "../../../global_providers/DialogProvider";
import { uploadMettaFile, loadMettaFile } from "../../../../api/AtomDBAPI";
import { getMettaLoadAvailability } from "../../../../utils/mettaLoadPolicy";
import { useSidebarAction } from "./useSidebarAction";

export function MettaLoadActionControl({
  atomdbType,
  atomDbOnline,
  isServerOffline,
  disabled = false,
  onBusyChange,
  onActionComplete,
}) {
  const mettaInputRef = useRef(null);
  const { currentMachine } = useDashboardContext();
  const { showConfirm } = useDialog();
  const { busy, run } = useSidebarAction({ onBusyChange, onActionComplete });

  const currentHost = currentMachine?.serverIp;
  const { canLoad, tooltip } = getMettaLoadAvailability(atomdbType, {
    atomDbOnline,
    isServerOffline,
    actionLocked: disabled && !busy,
  });
  const isDisabled = !canLoad || busy;

  const uploadAndLoad = (host, file, forceOverwrite) => async () => {
    const response = await uploadMettaFile(host, forceOverwrite, file);
    await loadMettaFile(host, response.saved_path);
  };

  const handleMettaUpload = async (event) => {
    const file = event.target.files?.[0];
    if (event.target) event.target.value = "";
    if (!file) return;

    const hostSnapshot = currentHost;
    await run(async () => {
      try {
        await uploadAndLoad(hostSnapshot, file, false)();
      } catch (error) {
        const existingFilePath = error?.response?.status === 409
          ? error.response.data?.file_path
          : null;
        if (!existingFilePath) throw error;

        showConfirm({
          title: "File already exists",
          message: `The file "${file.name}" already exists on the server.\n\nDo you want to OVERWRITE it? (Click CANCEL to safely load the existing server file instead).`,
          onConfirm: () => run(
            uploadAndLoad(hostSnapshot, file, true),
            "MeTTa file overwritten and loaded successfully.",
            "Failed to overwrite or load MeTTa file."
          ),
          onCancel: () => run(
            () => loadMettaFile(hostSnapshot, existingFilePath),
            "Existing MeTTa file loaded successfully.",
            "Failed to load existing MeTTa file."
          ),
        });
        return false;
      }
    }, "MeTTa database loaded successfully.", "Failed to load the MeTTa database.");
  };

  const openFilePicker = () => {
    if (isDisabled) return;
    const targetHost = currentHost || "the selected server";
    showConfirm({
      title: "Load MeTTa Database",
      message: `Load on ${targetHost} using the saved AtomDB configuration.\n\nThe file is uploaded to that server, then das-cli metta load runs there.`,
      onConfirm: () => mettaInputRef.current?.click(),
    });
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
      <Tooltip title={tooltip} placement="right" arrow describeChild>
        <span style={{ display: "block" }}>
          <StyledItem disabled={isDisabled} onClick={openFilePicker}>
            <ListItemIcon>
              {busy ? <CircularProgress size={16} /> : <Storage />}
            </ListItemIcon>
            <ListItemText primary="Load MeTTa Database" />
          </StyledItem>
        </span>
      </Tooltip>
    </>
  );
}
