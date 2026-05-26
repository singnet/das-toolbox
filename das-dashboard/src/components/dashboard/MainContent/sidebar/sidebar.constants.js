import {
  SettingsEthernet,
  Polyline,
  FileUpload,
  PlayArrow,
  Stop,
  Storage
} from "@mui/icons-material";

export const navigationItems = [
  {
    key: "servers",
    label: "Servers",
    icon: SettingsEthernet,
    context: "servers"
  },
  {
    key: "agents",
    label: "Agents",
    icon: Polyline,
    context: "agents"
  }
];

export const buildActionItems = ({
  architectureOnline,
  atomDbOnline,
  handleArchitectureAction,
  handleDatabaseAction,
  openConfigLoader,
  openMettaLoader
}) => [
    {
        label: "Load Config File",
        icon: FileUpload,
        onClick: openConfigLoader
    },
    {
    label: "Load MeTTa Database",
    icon: Storage,
    onClick: openMettaLoader,
    disabled: !atomDbOnline
    },
    {
        label: architectureOnline
        ? "Stop Architecture"
        : "Start Architecture",
        icon: architectureOnline
        ? Stop
        : PlayArrow,
        onClick: handleArchitectureAction,
        disabled: !atomDbOnline && !architectureOnline
    },
    {
        label: atomDbOnline
        ? "Stop AtomDB"
        : "Start AtomDB",
        icon: atomDbOnline
        ? Stop
        : PlayArrow,
        onClick: handleDatabaseAction
    },
];