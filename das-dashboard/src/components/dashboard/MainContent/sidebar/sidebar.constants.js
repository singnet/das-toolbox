import { ListItemText, ListItemIcon, Divider, CircularProgress } from "@mui/material";
import { SidebarContainer, Title, StyledList, SectionLabel, StyledItem } from "./sidebar.styled";
import { useRef, useState } from "react";
import { SettingsEthernet, Polyline, FileUpload, PlayArrow, Stop, Storage } from "@mui/icons-material";

import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { useDialog } from "../../../global_providers/DialogProvider";

import { handleLoadConfig } from "../../../../utils/FileLoader";
import { saveConfig } from "../../../../api/ConfigAPI";
import { startArchitecture, stopArchitecture, startDatabases, stopDatabases } from "../../../../api/ServicesAPI";
import { uploadMettaFile, loadMettaFile } from "../../../../api/AtomDBAPI";
import { extractErrorDetails } from "../../../../api/APIUtils";

// Navigation items of the sidebar
const navigationItems = [
  { key: "servers", label: "Servers", icon: SettingsEthernet, context: "servers" },
  { key: "agents", label: "Agents", icon: Polyline, context: "agents" }
];

export function SideBar() {
  const [selected, setSelected] = useState("servers");
  const [loadingAction, setLoadingAction] = useState(null);

  const { setCurrentContext, setDashboardBaseValues, services, currentMachine } = useDashboardContext();
  const { showToast } = useToast();
  const { showConfirm } = useDialog();

  const fileInputRef = useRef(null);
  const mettaInputRef = useRef(null);

  const currentHost = currentMachine?.serverIp;
  const isServerOffline = !currentHost;

  const atomDbOnline = services.some(s =>
    (s.container_name?.includes("mongodb") || s.container_name?.includes("redis") || s.container_name?.includes("morkdb")) &&
    s.status === "running"
  );

  const architectureOnline = services.some(s =>
    (s.container_name?.includes("agent") || s.container_name?.includes("broker")) &&
    s.status === "running"
  );

  const executeAsyncAction = async (actionKey, action, successMessage, errorMessage) => {
    try {
      setLoadingAction(actionKey);
      await action();
      showToast({ message: successMessage, severity: "success" });
    } catch (err) {
      console.error(errorMessage, err);
      showToast({ message: errorMessage, severity: "error", details: extractErrorDetails(err) });
    } finally {
      setLoadingAction(null);
    }
  };

  const onLoadConfig = async ({ parsed, file }) => {
    await executeAsyncAction("load-config", async () => {
      await saveConfig(file);
      setDashboardBaseValues(parsed);
    }, "Configuration loaded successfully.", "Failed to load configuration.");
  };

  const handleMettaUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const executeLoad = async (filePath) => {
      await executeAsyncAction("load-metta", async () => { await loadMettaFile(currentHost, filePath); },
        "MeTTa database loaded successfully.", "Failed to load MeTTa database."
      );
    };

    try {
      setLoadingAction("upload-metta");
      const uploadResponse = await uploadMettaFile(currentHost, false, file);
      setLoadingAction(null);
      await executeLoad(uploadResponse.saved_path);
    } catch (err) {
      setLoadingAction(null);
      console.error("MeTTa upload failed:", err);
      const responseData = err?.response?.data;

      if (err?.response?.status === 409 && responseData?.file_path) {
        const existingFilePath = responseData.file_path;
        showConfirm({
          title: "File already exists",
          message: `The file "${file.name}" already exists on the server.\n\nDo you want to overwrite it?`,
          onConfirm: async () => {
            await executeAsyncAction("overwrite-metta", async () => {
              const res = await uploadMettaFile(currentHost, true, file);
              await loadMettaFile(currentHost, res.saved_path);
            }, "MeTTa file overwritten successfully.", "Failed to overwrite MeTTa file.");
          },
          onCancel: async () => { await executeLoad(existingFilePath); }
        });
        return;
      }
      showToast({ message: "Failed to upload MeTTa database.", severity: "error", details: extractErrorDetails(err) });
    } finally {
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
        onConfirm: async () => {
          await executeAsyncAction("stop-architecture", () => stopArchitecture(currentHost), "Architecture stopped successfully.", "Failed to stop architecture.");
        }
      });
      return;
    }
    showConfirm({
      title: "Start Architecture",
      message: "Do you want to start the architecture?",
      onConfirm: async () => {
        await executeAsyncAction("start-architecture", () => startArchitecture(currentHost), "Architecture started successfully.", "Failed to start architecture.");
      }
    });
  };

  const handleDatabaseAction = () => {
    if (atomDbOnline) {
      showConfirm({
        title: "Stop AtomDB",
        message: "Are you sure you want to stop AtomDB?\n\nAll in-memory data may be lost.",
        onConfirm: async () => {
          await executeAsyncAction("stop-database", () => stopDatabases(currentHost), "AtomDB stopped successfully.", "Failed to stop AtomDB.");
        }
      });
      return;
    }
    showConfirm({
      title: "Start AtomDB",
      message: "Do you want to start AtomDB?",
      onConfirm: async () => {
        await executeAsyncAction("start-database", () => startDatabases(currentHost), "AtomDB started successfully.", "Failed to start AtomDB.");
      }
    });
  };

  // Helper para agrupar propriedades visuais repetitivas de botões bloqueados
  const getButtonStyles = (isDisabled) => ({
    opacity: isDisabled ? 0.5 : 1,
    pointerEvents: isDisabled ? "none" : "auto",
    cursor: loadingAction ? "wait" : isDisabled ? "not-allowed" : "pointer"
  });

  return (
    <SidebarContainer>
      <Title variant="h6">DAS</Title>

      <StyledList>
        <SectionLabel>INFRA</SectionLabel>
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
              <ListItemIcon><Icon fontSize="small" /></ListItemIcon>
              <ListItemText primary={item.label} />
            </StyledItem>
          );
        })}

        <Divider sx={{ my: 1 }} />
        <SectionLabel>ACTIONS</SectionLabel>

        <input ref={fileInputRef} type="file" accept=".json,application/json" hidden onChange={(e) => handleLoadConfig(e, onLoadConfig)} />
        <input ref={mettaInputRef} type="file" accept=".metta" hidden onChange={handleMettaUpload} />

        {/* 1. LOAD CONFIG FILE (Sempre ativo, exceto se estiver em loading global) */}
        <StyledItem 
          onClick={loadingAction ? undefined : () => fileInputRef.current?.click()} 
          sx={getButtonStyles(!!loadingAction)}
        >
          <ListItemIcon>
            {loadingAction === "load-config" ? <CircularProgress size={16} /> : <FileUpload fontSize="small" />}
          </ListItemIcon>
          <ListItemText primary="Load Config File" />
        </StyledItem>

        {/* 2. LOAD METTA DATABASE (Requer servidor online E AtomDB online) */}
        <StyledItem 
          onClick={loadingAction || isServerOffline || !atomDbOnline ? undefined : () => mettaInputRef.current?.click()} 
          sx={getButtonStyles(!!loadingAction || isServerOffline || !atomDbOnline)}
        >
          <ListItemIcon>
            {loadingAction === "load-metta" || loadingAction === "overwrite-metta" ? <CircularProgress size={16} /> : <Storage fontSize="small" />}
          </ListItemIcon>
          <ListItemText primary="Load MeTTa Database" />
        </StyledItem>

        {/* 3. START/STOP ARCHITECTURE (Requer servidor online. Só executa se AtomDB estiver de pé) */}
        <StyledItem 
          onClick={loadingAction || isServerOffline ? undefined : handleArchitectureAction} 
          sx={getButtonStyles(!!loadingAction || isServerOffline || (!atomDbOnline && !architectureOnline))}
        >
          <ListItemIcon>
            {loadingAction === "start-architecture" || loadingAction === "stop-architecture" ? (
              <CircularProgress size={16} />
            ) : architectureOnline ? <Stop fontSize="small" /> : <PlayArrow fontSize="small" />}
          </ListItemIcon>
          <ListItemText primary={architectureOnline ? "Stop Architecture" : "Start Architecture"} />
        </StyledItem>

        {/* 4. START/STOP ATOMDB (Requer servidor online para permitir ação de start) */}
        <StyledItem 
          onClick={loadingAction || isServerOffline ? undefined : handleDatabaseAction} 
          sx={getButtonStyles(!!loadingAction || isServerOffline)}
        >
          <ListItemIcon>
            {loadingAction === "start-database" || loadingAction === "stop-database" ? (
              <CircularProgress size={16} />
            ) : atomDbOnline ? <Stop fontSize="small" /> : <PlayArrow fontSize="small" />}
          </ListItemIcon>
          <ListItemText primary={atomDbOnline ? "Stop AtomDB" : "Start AtomDB"} />
        </StyledItem>

      </StyledList>
    </SidebarContainer>
  );
}