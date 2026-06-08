import { useState, useEffect } from "react";
import { Box, IconButton } from "@mui/material";
import { Menu as MenuIcon } from "@mui/icons-material";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { ServerDrawer } from "./ServerDrawer";
import {
  Container,
  Header,
  Title,
  StyledTabs,
  StyledTab,
  StatusIcon,
} from "./servertab.styled";

const MAX_VISIBLE_TABS = 8;

export function ServerTab() {
  const {
    machines,
    currentMachine,
    setCurrentMachine,
    connectionError,
  } = useDashboardContext();

  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    if (machines && machines.length > 0 && !currentMachine) {
      setCurrentMachine(machines[0]);
    }
  }, [machines, currentMachine, setCurrentMachine]);

  const setStatusColor = (running) => (running ? "green" : "darkgrey");

  const visibleServers = machines ? machines.slice(0, MAX_VISIBLE_TABS) : [];
  const hiddenServers = machines ? machines.slice(MAX_VISIBLE_TABS) : [];

  const selectMachine = (serverIp) => {
    if (connectionError) return;

    const selectedMachine = machines.find((m) => m.serverIp === serverIp);
    if (selectedMachine) {
      setCurrentMachine(selectedMachine);
      setDrawerOpen(false);
    }
  };

  if (!machines || machines.length === 0) {
    return (
      <Container>
        <Header>
          <Title>No servers loaded. Please load a config file.</Title>
        </Header>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>
          {connectionError ? "Connection Failed" : `${currentMachine?.serverIp || "Select server"} - Metrics Overview`}
        </Title>

        {hiddenServers.length > 0 && (
          <IconButton
            size="small"
            disabled={!!connectionError}
            onClick={() => setDrawerOpen(true)}
            sx={{ color: connectionError ? "rgba(255,255,255,0.3)" : "white" }}
          >
            <MenuIcon />
          </IconButton>
        )}
      </Header>

      <StyledTabs
        value={currentMachine?.serverIp ?? false}
        onChange={(_, newValue) => selectMachine(newValue)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          pointerEvents: connectionError ? "none" : "auto",
          opacity: connectionError ? 0.6 : 1
        }}
      >
        {visibleServers.map((server) => (
          <StyledTab
            key={server.serverIp}
            value={server.serverIp}
            disabled={!!connectionError}
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

      <ServerDrawer
        drawerOpen={drawerOpen}
        setDrawerOpen={setDrawerOpen}
        machines={hiddenServers}
        currentMachine={currentMachine}
        selectMachine={selectMachine}
        setStatusColor={setStatusColor}
      />
    </Container>
  );
}