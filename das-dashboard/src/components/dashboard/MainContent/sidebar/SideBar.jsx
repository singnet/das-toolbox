import { useRef, useState } from "react";
import { List, ListItemIcon, ListItemText, CircularProgress } from "@mui/material";
import { Dashboard as DashboardIcon, SettingsEthernet, Polyline, PlayArrow, Stop, Storage } from "@mui/icons-material";

import {
  SidebarContainer,
  SidebarHeader,
  SidebarTitle,
  SidebarListContainer,
  SectionLabel,
  StyledList,
  StyledItem,
  ActionDivider
} from "./sidebar.styled";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";

import { startArchitecture, stopArchitecture, startDatabases, stopDatabases } from "../../../../api/ServicesAPI";
import { uploadMettaFile, loadMettaFile } from "../../../../api/AtomDBAPI";
import { extractErrorDetails } from "../../../../api/APIUtils";

const navigationItems = [
  { key: "servers", label: "Servers", icon: SettingsEthernet, context: "servers" },
  { key: "agents", label: "Agents", icon: Polyline, context: "agents" }
];

export function SideBar() {
  const [selected, setSelected] = useState("servers");
  const [loadingAction, setLoadingAction] = useState(null);

  const {
    setCurrentContext,
    currentMachine,
    globalServicesState,
    forceGlobalStateUpdate,
    isSwitchingHost
  } = useDashboardContext();

  const { showToast } = useToast();
  const { showConfirm } = useDialog();

  const mettaInputRef = useRef(null);

  const currentHost = currentMachine?.serverIp;
  const isServerOffline = !currentHost || isSwitchingHost;

  const atomDbOnline = globalServicesState.atomDbOnline;
  const architectureOnline = globalServicesState.architectureOnline;

  const executeAsyncAction = async (actionKey, action, successMessage, errorMessage, onActionSuccess) => {
    try {
      setLoadingAction(actionKey);
      await action();
      showToast({ message: successMessage, severity: "success" });
      if (onActionSuccess) onActionSuccess();
    } catch (err) {
      console.error(errorMessage, err);
      showToast({ message: errorMessage, severity: "error", details: extractErrorDetails(err) });
    } finally {
      setLoadingAction(null);
    }
  };

  const handleMettaUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const hostSnapshot = currentHost;

    try {
      setLoadingAction("upload-metta");
      const uploadResponse = await uploadMettaFile(hostSnapshot, false, file);

      setLoadingAction("load-metta");
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
        showToast({ message: "Failed to upload MeTTa database.", severity: "error", details: extractErrorDetails(err) });
      }
    } finally {
      setLoadingAction(null);
      if (event.target) event.target.value = "";
    }
  };

  const handleArchitectureAction = () => {
    if (!atomDbOnline) {
      showToast({ message: "AtomDB must be online before starting architecture.", severity: "warning" });
      return;
    }

    if (architectureOnline) {
      showConfirm({
        title: "Stop DAS Services",
        message: "Are you sure you want to stop all DAS services?\n\nEverything will be shut down except AtomDB.",
        onConfirm: () => executeAsyncAction(
          "stop-architecture",
          () => stopArchitecture(currentHost),
          "Architecture stopped successfully.",
          "Failed to stop architecture.",
          () => forceGlobalStateUpdate({ architectureOnline: false })
        )
      });
      return;
    }

    showConfirm({
      title: "Start Architecture",
      message: "Do you want to start the architecture?",
      onConfirm: () => executeAsyncAction(
        "start-architecture",
        () => startArchitecture(currentHost),
        "Architecture started successfully.",
        "Failed to start architecture.",
        () => forceGlobalStateUpdate({ architectureOnline: true })
      )
    });
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
          "Failed to stop AtomDB.",
          () => forceGlobalStateUpdate({ atomDbOnline: false })
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
        "Failed to start AtomDB.",
        () => forceGlobalStateUpdate({ atomDbOnline: true })
      )
    });
  };

  const isActionLoading = ["load-metta", "overwrite-metta", "load-existing-metta", "upload-metta"].includes(loadingAction);

  return (
    <SidebarContainer>
      <SidebarHeader>
        <DashboardIcon />
        <SidebarTitle>Dashboard</SidebarTitle>
      </SidebarHeader>

      <SidebarListContainer>
        <StyledList>
          <SectionLabel>Infra</SectionLabel>

          <List disablePadding>
            {navigationItems.map(item => {
              const Icon = item.icon;
              const isNavDisabled = isSwitchingHost;
              return (
                <StyledItem
                  key={item.key}
                  selected={selected === item.key}
                  disabled={isNavDisabled}
                  onClick={() => {
                    if (isNavDisabled) return;
                    setSelected(item.key);
                    setCurrentContext(item.context);
                  }}
                >
                  <ListItemIcon>
                    <Icon />
                  </ListItemIcon>
                  <ListItemText primary={item.label} />
                </StyledItem>
              );
            })}
          </List>

          <ActionDivider />

          <SectionLabel>Actions</SectionLabel>

          <List disablePadding>
            <input ref={mettaInputRef} type="file" accept=".metta" hidden onChange={handleMettaUpload} />

            <StyledItem
              disabled={!!loadingAction || isServerOffline}
              onClick={() => !loadingAction && !isServerOffline && mettaInputRef.current?.click()}
            >
              <ListItemIcon>
                {isActionLoading ? <CircularProgress size={16} /> : <Storage />}
              </ListItemIcon>
              <ListItemText primary="Load MeTTa Database" />
            </StyledItem>

            <StyledItem
              disabled={!!loadingAction || isServerOffline || (!atomDbOnline && !architectureOnline)}
              onClick={() => !loadingAction && !isServerOffline && (atomDbOnline || architectureOnline) && handleArchitectureAction()}
            >
              <ListItemIcon>
                {["start-architecture", "stop-architecture"].includes(loadingAction) ? (
                  <CircularProgress size={16} />
                ) : architectureOnline ? <Stop /> : <PlayArrow />}
              </ListItemIcon>
              <ListItemText primary={architectureOnline ? "Stop Architecture" : "Start Architecture"} />
            </StyledItem>

            <StyledItem
              disabled={!!loadingAction || isServerOffline}
              onClick={() => !loadingAction && !isServerOffline && handleDatabaseAction()}
            >
              <ListItemIcon>
                {["start-database", "stop-database"].includes(loadingAction) ? (
                  <CircularProgress size={16} />
                ) : atomDbOnline ? <Stop /> : <PlayArrow />}
              </ListItemIcon>
              <ListItemText primary={atomDbOnline ? "Stop AtomDB" : "Start AtomDB"} />
            </StyledItem>
          </List>
        </StyledList>
      </SidebarListContainer>
    </SidebarContainer>
  );
}
