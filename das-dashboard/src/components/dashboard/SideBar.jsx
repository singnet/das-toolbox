import { styled } from "@mui/material/styles";
import {
  Box,
  Typography,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Divider
} from "@mui/material";
import { useEffect, useState } from "react";

import DashboardIcon from "@mui/icons-material/Dashboard";
import AccountTreeIcon from "@mui/icons-material/AccountTree";
import SettingsEthernetIcon from "@mui/icons-material/SettingsEthernet";
import LayersIcon from "@mui/icons-material/Layers";
import WorkIcon from "@mui/icons-material/Work";

import { useDashboardContext } from "../global_providers/DashboardContextProvider";

const SidebarContainer = styled(Box)({
  width: 240,
  backgroundColor: "#f5f5f5",
  borderRight: "1px solid #ddd",
  padding: "16px 0",
  height: "100vh",
  display: "flex",
  flexDirection: "column",
});

const Title = styled(Typography)({
  padding: "0 16px",
  marginBottom: "16px",
  fontWeight: "bold",
});

const StyledList = styled(List)({
  width: "100%",
});

const SectionLabel = styled(Typography)({
  fontSize: "12px",
  fontWeight: 600,
  opacity: 0.6,
  padding: "8px 16px",
});

const StyledItem = styled(ListItemButton)({
  padding: "8px 16px",
  gap: "8px",

  "&.Mui-selected": {
    backgroundColor: "#008cff20",
    borderLeft: "3px solid #008cff",
  },

  "&:hover": {
    backgroundColor: "#e3f2fd",
  },
});

export function SideBar() {

  const [selected, setSelected] = useState("overview");
  const { currentContext, setCurrentContext } = useDashboardContext()

  return (
    <SidebarContainer>
      <Title variant="h6">DAS</Title>

      <StyledList>

        <SectionLabel>WORKLOADS</SectionLabel>

        <StyledItem
          selected={selected === "overview"}
          onClick={() => { 
            setSelected("overview") 
            setCurrentContext("overview")
          }}
        >
          <ListItemIcon>
            <SettingsEthernetIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Overview" />
        </StyledItem>

        <Divider sx={{ my: 1 }} />

        <SectionLabel>INFRA</SectionLabel>

        <StyledItem
          selected={selected === "architecture"}
          onClick={() => {
            setSelected("architecture")
            setCurrentContext("architecture")
          }}
        >
          <ListItemIcon>
            <AccountTreeIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Architecture" />
        </StyledItem>

      </StyledList>
    </SidebarContainer>
  );
}