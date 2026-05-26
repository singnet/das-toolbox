import {
  ListItemText,
  ListItemIcon,
  Divider
} from "@mui/material";

import {
  SidebarContainer,
  Title,
  StyledList,
  SectionLabel,
  StyledItem
} from "./sidebar.styled";

import { useRef, useState } from "react";

import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useToast } from "../../../global_providers/ToastProvider";

import { handleLoadConfig } from "../../../../utils/FileLoader";

import { saveConfig } from "../../../../api/ConfigAPI";

import {
  startArchitecture,
  stopArchitecture,
  startDatabases,
  stopDatabases
} from "../../../../api/ServicesAPI";

import {
  uploadMettaFile,
  loadMettaFile
} from "../../../../api/AtomDBAPI";

import {
  navigationItems,
  buildActionItems
} from "./sidebar.constants";

import { ConfirmDialog } from "../../Dialogs/DialogBoxes";

export function SideBar() {

  const [selected, setSelected] = useState("servers");

  const [dialogState, setDialogState] = useState({
    open: false,
    action: null,
    message: ""
  });

  const {
    setCurrentContext,
    setDashboardBaseValues,
    services,
    currentMachine
  } = useDashboardContext();

  const { showToast } = useToast();

  const fileInputRef = useRef(null);
  const mettaInputRef = useRef(null);

  const currentHost = currentMachine?.serverIp;

  const atomDbOnline = services.some(
    service =>
      (
        service.container_name?.includes("mongodb") ||
        service.container_name?.includes("redis") ||
        service.container_name?.includes("morkdb")
      ) &&
      service.status === "running"
  );

  const architectureOnline = services.some(
    service =>
      service.container_name?.includes("agent") || service.container_name?.includes("broker") &&
      service.status === "running"
  );

  const onLoadConfig = async ({ parsed, file }) => {

    try {

      await saveConfig(file);

      setDashboardBaseValues(parsed);

      showToast(
        "Configuration loaded successfully.",
        "success"
      );

    } catch (err) {

      console.error("Config load failed:", err);

      showToast(
        "Failed to load configuration.",
        "error"
      );
    }
  };

  const handleMettaUpload = async (event) => {

    const file = event.target.files?.[0];

    if (!file) return;

    try {

      showToast(
        "Uploading MeTTa database...",
        "info"
      );

      const uploadResponse = await uploadMettaFile(
        currentHost,
        file
      );

      await loadMettaFile(
        currentHost,
        uploadResponse.saved_path
      );

      showToast(
        "MeTTa database loaded successfully.",
        "success"
      );

    } catch (err) {

      console.error("MeTTa upload failed:", err);

      showToast(
        "Failed to load MeTTa database.",
        "error"
      );
    }
  };

  const openConfirmDialog = (message, action) => {

    setDialogState({
      open: true,
      action,
      message
    });
  };

  const closeDialog = () => {

    setDialogState(prev => ({
      ...prev,
      open: false
    }));
  };

  const executeDialogAction = async () => {

    try {

      await dialogState.action?.();

    } catch (err) {

      console.error("Action execution failed:", err);

      showToast(
        "Action execution failed.",
        "error"
      );

    } finally {

      closeDialog();
    }
  };

  const handleArchitectureAction = () => {

    if (!atomDbOnline) {
      showToast(
        "AtomDB must be online before starting architecture.",
        "warning"
      );

      return;
    }

    if (architectureOnline) {

      openConfirmDialog(
        "Are you sure you want to stop all DAS services? Everything will be shut down except for the AtomDBs.",
        async () => {
          await stopArchitecture(currentHost);
          showToast(
            "Architecture stopped successfully.",
            "success"
          );
        }
      );

      return;
    }

    openConfirmDialog(
      "Start architecture?",
      async () => {
        await startArchitecture(currentHost);
        showToast(
          "Architecture started successfully.",
          "success"
        );
      }
    );
  };

  const handleDatabaseAction = () => {

    if (atomDbOnline) {
      openConfirmDialog(
        "Are you sure you want to stop the AtomDB service? All relevant data will be lost on shutdown.",
        async () => {
          await stopDatabases(currentHost);
          showToast(
            "AtomDB stopped successfully.",
            "success"
          );
        }
      );

      return;
    }

    openConfirmDialog(
      "Start AtomDB?",
      async () => {
        await startDatabases(currentHost);
        showToast(
          "AtomDB started successfully.",
          "success"
        );
      }
    );
  };

  const actionItems = buildActionItems({
    architectureOnline,
    atomDbOnline,
    handleArchitectureAction,
    handleDatabaseAction,
    openConfigLoader: () => fileInputRef.current?.click(),
    openMettaLoader: () => mettaInputRef.current?.click()
  });

  return (
    <SidebarContainer>

      <Title variant="h6">
        DAS
      </Title>

      <StyledList>

        <SectionLabel>
          INFRA
        </SectionLabel>

        {navigationItems.map(item => {

          const Icon = item.icon;

          return (
            <StyledItem
              key={item.key}
              selected={selected === item.key}
              onClick={() => {
                setSelected(item.key);
                setCurrentContext(item.context);
              }}
            >
              <ListItemIcon>
                <Icon fontSize="small" />
              </ListItemIcon>

              <ListItemText primary={item.label} />
            </StyledItem>
          );
        })}

        <Divider sx={{ my: 1 }} />

        <SectionLabel>
          ACTIONS
        </SectionLabel>

        <input
          ref={fileInputRef}
          type="file"
          accept=".json,application/json"
          hidden
          onChange={(e) => handleLoadConfig(e, onLoadConfig)}
        />

        <input
          ref={mettaInputRef}
          type="file"
          accept=".metta"
          hidden
          onChange={handleMettaUpload}
        />

        {actionItems.map(item => {
          const Icon = item.icon;

          return (
            <StyledItem
              key={item.label}
              onClick={item.disabled ? undefined : item.onClick}
              sx={{
                opacity: item.disabled ? 0.5 : 1,
                pointerEvents: item.disabled ? "none" : "auto"
              }}
            >
              <ListItemIcon>
                <Icon fontSize="small" />
              </ListItemIcon>

              <ListItemText primary={item.label} />
            </StyledItem>
          );
        })}

        <ConfirmDialog
          dialogOpen={dialogState.open}
          setDialogOpen={closeDialog}
          action={executeDialogAction}
          message={dialogState.message}
        />

      </StyledList>

    </SidebarContainer>
  );
}