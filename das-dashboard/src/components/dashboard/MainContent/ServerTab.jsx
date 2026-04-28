import { styled } from "@mui/material/styles";
import {
  Box,
  Tab,
  Tabs,
  Typography,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  IconButton,
  Divider,
} from "@mui/material";

import {
  Circle,
  Menu as MenuIcon,
} from "@mui/icons-material";

import { useState } from "react";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { mockMachines } from "../../../pages/dashboard/dashboard_mock_data";

const MAX_VISIBLE_TABS = 5;

const Container = styled(Box)({
  display: "flex",
  flexDirection: "column",
});

const Header = styled(Box)({
  padding: "10px 16px",
  backgroundColor: "#008cff",
  color: "white",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
});

const Title = styled(Typography)({
  fontWeight: "bold",
});

const StyledTabs = styled(Tabs)({
  borderBottom: "1px solid #ddd",

  "& .MuiTabs-indicator": {
    backgroundColor: "#008cff",
  },
});

const StyledTab = styled(Tab)({
  textTransform: "none",
  fontWeight: 500,

  "&.Mui-selected": {
    color: "#008cff",
  },
});

const StatusIcon = styled(Circle)({
  width: "10px",
  height: "10px",
});

export function ServerTab() {
  const { currentMachine, setCurrentMachine } = useDashboardContext();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const setStatusColor = (running) =>
    running ? "green" : "darkgrey";

  const visibleServers = mockMachines.slice(0, MAX_VISIBLE_TABS);
  const hiddenServers = mockMachines.slice(MAX_VISIBLE_TABS);

  const selectMachine = (serverIp) => {
    const selectedMachine = mockMachines.find(
      (m) => m.serverIp === serverIp
    );

    setCurrentMachine(selectedMachine);
    setDrawerOpen(false);
  };

  return (
    <Container>
      <Header>
        <Title>
          {currentMachine?.serverIp || "Select server"} - Metrics Overview
        </Title>

        {hiddenServers.length > 0 && (
          <IconButton
            size="small"
            onClick={() => setDrawerOpen(true)}
            sx={{ color: "white" }}
          >
            <MenuIcon />
          </IconButton>
        )}
      </Header>

      <StyledTabs
        value={currentMachine?.serverIp || false}
        onChange={(e, newValue) => selectMachine(newValue)}
      >
        {visibleServers.map((server) => (
          <StyledTab
            key={server.serverIp}
            value={server.serverIp}
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <StatusIcon
                  sx={{
                    color: setStatusColor(server.running),
                  }}
                />
                {server.serverIp}
              </Box>
            }
          />
        ))}
      </StyledTabs>

      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box
          sx={{
            width: 320,
            background: "#0f172a",
            color: "white",
            height: "100%",
          }}
        >
          <Box p={2}>
            <Typography variant="h6">
              All Servers
            </Typography>
          </Box>

          <Divider sx={{ borderColor: "#334155" }} />

          <List>
            {mockMachines.map((server) => (
              <ListItemButton
                key={server.serverIp}
                onClick={() => selectMachine(server.serverIp)}
                selected={
                  currentMachine?.serverIp === server.serverIp
                }
              >
                <StatusIcon
                  sx={{
                    color: setStatusColor(server.running),
                    mr: 1.5,
                  }}
                />

                <ListItemText
                  primary={server.serverIp}
                  secondary={
                    server.running ? "Online" : "Offline"
                  }
                  secondaryTypographyProps={{
                    color: "#94a3b8",
                  }}
                />
              </ListItemButton>
            ))}
          </List>
        </Box>
      </Drawer>
    </Container>
  );
}