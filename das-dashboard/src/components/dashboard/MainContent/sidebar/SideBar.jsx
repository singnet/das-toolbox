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
} from './sidebar.styled';

import FileUploadIcon from '@mui/icons-material/FileUpload';
import SettingsEthernetIcon from "@mui/icons-material/SettingsEthernet";
import { Polyline } from "@mui/icons-material";

import { useRef, useState } from "react";

import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { handleLoadConfig } from "../../../../utils/FileLoader";
import { saveConfigtoDashboard } from "../../../../api/DashboardServices";

export function SideBar() {
  const [selected, setSelected] = useState("servers");

  const {
    setCurrentContext,
    setDashboardBaseValues
  } = useDashboardContext();

  const fileInputRef = useRef(null);

  const onLoad = async ({ parsed, file }) => {
    try {
      
      await saveConfigtoDashboard(file);
      setDashboardBaseValues(parsed);

    } catch (err) {
      console.error("Config load failed:", err);
    }
  };

  return (
    <SidebarContainer>
      <Title variant="h6">DAS</Title>

      <StyledList>
        <SectionLabel>INFRA</SectionLabel>

        <StyledItem
          selected={selected === "servers"}
          onClick={() => {
            setSelected("servers");
            setCurrentContext("servers");
          }}
        >
          <ListItemIcon>
            <SettingsEthernetIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Servers" />
        </StyledItem>

        <Divider sx={{ my: 1 }} />

        <SectionLabel>ARCHITECTURE</SectionLabel>

        <StyledItem
          selected={selected === "agents"}
          onClick={() => {
            setSelected("agents");
            setCurrentContext("agents");
          }}
        >
          <ListItemIcon>
            <Polyline fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Agents" />
        </StyledItem>

        <Divider sx={{ my: 1 }} />

        <SectionLabel>ACTIONS</SectionLabel>

        <StyledItem onClick={() => fileInputRef.current?.click()}>
          <ListItemIcon>
            <FileUploadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Load Config File" />
        </StyledItem>

        <input
          ref={fileInputRef}
          type="file"
          accept=".json,application/json"
          hidden
          onChange={(e) => handleLoadConfig(e, onLoad)}
        />
      </StyledList>
    </SidebarContainer>
  );
}