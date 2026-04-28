import { useState } from "react";

import {
  Box,
  IconButton,
} from "@mui/material";

import { Menu as MenuIcon } from "@mui/icons-material";

import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { mockMachines } from "../../../../pages/dashboard/dashboard_mock_data";

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
  const { currentMachine, setCurrentMachine } =
    useDashboardContext();

  const [drawerOpen, setDrawerOpen] = useState(false);

  const setStatusColor = (running) =>
    running ? "green" : "darkgrey";

  const visibleServers =
    mockMachines.slice(0, MAX_VISIBLE_TABS);

  const hiddenServers =
    mockMachines.slice(MAX_VISIBLE_TABS);

  const selectMachine = (serverIp) => {
    const selectedMachine = mockMachines.find(
      (machine) => machine.serverIp === serverIp
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
        onChange={(e, newValue) =>
          selectMachine(newValue)
        }
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