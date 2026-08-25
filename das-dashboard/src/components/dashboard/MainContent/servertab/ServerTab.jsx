import { useState, useEffect } from "react";
import { Box, IconButton } from "@mui/material";
import { Menu as MenuIcon } from "@mui/icons-material";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useServerTabMetricsContext } from "../../../global_providers/ServerTabMetricsProvider";
import { ServerDrawer } from "./ServerDrawer";
import {
  Container,
  StyledTabs,
  StyledTab,
  StatusIcon,
} from "./servertab.styled";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

const MAX_VISIBLE_TABS = 8;

export function ServerTab() {
  const { machines, currentMachine, setCurrentMachine, setCurrentService } = useDashboardContext();
  const { hostStreamConnected, hostStreamError } = useServerTabMetricsContext();

  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    if (machines && machines.length > 0 && !currentMachine) {
      setCurrentMachine(machines[0]);
    }
  }, [machines, currentMachine, setCurrentMachine]);

  const setStatusColor = (isActiveHost) => (isActiveHost ? palette.accent : palette.textMuted);

  const visibleServers = machines ? machines.slice(0, MAX_VISIBLE_TABS) : [];
  const hiddenServers = machines ? machines.slice(MAX_VISIBLE_TABS) : [];

  const selectMachine = (serverIp) => {
    if (hostStreamError) return;

    const selectedMachine = machines.find((m) => m.serverIp === serverIp);
    if (selectedMachine) {
      setCurrentMachine(selectedMachine);
      setCurrentService(null);
      setDrawerOpen(false);
    }
  };

  if (!machines || machines.length === 0) {
    return null;
  }

  return (
    <Container>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          pr: 1
        }}
      >
        <StyledTabs
          value={currentMachine?.serverIp ?? false}
          onChange={(_, newValue) => selectMachine(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            flex: 1,
            pointerEvents: hostStreamError ? "none" : "auto",
            opacity: hostStreamError ? 0.6 : 1
          }}
        >
          {visibleServers.map((server) => (
            <StyledTab
              key={server.serverIp}
              value={server.serverIp}
              disabled={!!hostStreamError}
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <StatusIcon
                    sx={{
                      color: setStatusColor(
                        server.serverIp === currentMachine?.serverIp && hostStreamConnected
                      ),
                    }}
                  />
                  {server.serverIp}
                </Box>
              }
            />
          ))}
        </StyledTabs>

        {hiddenServers.length > 0 && (
          <IconButton
            size="small"
            disabled={!!hostStreamError}
            onClick={() => setDrawerOpen(true)}
            sx={{
              color: palette.textSecondary,
              border: `1px solid ${palette.border}`,
              borderRadius: 2,
              ml: 1
            }}
          >
            <MenuIcon fontSize="small" />
          </IconButton>
        )}
      </Box>

      <ServerDrawer
        drawerOpen={drawerOpen}
        setDrawerOpen={setDrawerOpen}
        machines={hiddenServers}
        currentMachine={currentMachine}
        selectMachine={selectMachine}
        setStatusColor={setStatusColor}
        hostStreamConnected={hostStreamConnected}
      />
    </Container>
  );
}
