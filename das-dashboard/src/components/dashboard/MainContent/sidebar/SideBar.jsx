import { useCallback, useEffect, useState } from "react";
import { List, ListItemIcon, ListItemText } from "@mui/material";
import { Dashboard as DashboardIcon, SettingsEthernet, Polyline } from "@mui/icons-material";

import {
  SidebarContainer,
  SidebarHeader,
  SidebarTitle,
  SidebarListContainer,
  SectionLabel,
  StyledList,
  StyledItem,
  ActionDivider,
} from "./sidebar.styled";

import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useServerTabMetricsContext } from "../../../global_providers/ServerTabMetricsProvider";
import { getConfigHosts } from "../../../../api/ConfigAPI";
import { fetchInfraStatusForAllHosts } from "../../../../utils/infraStatus";

import { ArchitectureActionControl } from "./ArchitectureActionControl";
import { AtomDBActionControl } from "./AtomDBActionControl";
import { MettaLoadActionControl } from "./MettaLoadActionControl";

const navigationItems = [
  { key: "servers", label: "Servers", icon: SettingsEthernet, context: "servers" },
  { key: "agents", label: "Agents", icon: Polyline, context: "agents" },
];

export function SideBar() {
  const [selected, setSelected] = useState("servers");
  const [busyActions, setBusyActions] = useState({});
  const [atomDbOnline, setAtomDbOnline] = useState(false);
  const [architectureOnline, setArchitectureOnline] = useState(false);

  const { setCurrentContext, currentMachine, currentContext } = useDashboardContext();
  const { hostStreamSwitching } = useServerTabMetricsContext();

  const loadInfraStatus = useCallback(async () => {
    const { hosts } = await getConfigHosts();
    const serverIps = (hosts ?? []).map((host) => host.ip).filter(Boolean);
    const statusByHost = await fetchInfraStatusForAllHosts(serverIps);

    setAtomDbOnline(
      Object.values(statusByHost).some((status) => status.atomDbOnline)
    );
    setArchitectureOnline(
      Object.values(statusByHost).some((status) => status.architectureOnline)
    );
  }, []);

  useEffect(() => {
    loadInfraStatus().catch((error) => {
      console.error("Failed to load sidebar infra status:", error);
    });
  }, [loadInfraStatus]);

  const currentHost = currentMachine?.serverIp;
  const isSwitchingHost = currentContext === "servers" && hostStreamSwitching;
  const isServerOffline = !currentHost || isSwitchingHost;
  const isAnyActionLoading = Object.values(busyActions).some(Boolean);

  const setActionBusy = (actionKey, busy) => {
    setBusyActions((current) => ({ ...current, [actionKey]: busy }));
  };

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
            {navigationItems.map((item) => {
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

            <AtomDBActionControl
              atomDbOnline={atomDbOnline}
              isServerOffline={isServerOffline}
              disabled={isAnyActionLoading && !busyActions.atomdb}
              onBusyChange={(busy) => setActionBusy("atomdb", busy)}
              onActionComplete={loadInfraStatus}
            />

            <ArchitectureActionControl
              atomDbOnline={atomDbOnline}
              architectureOnline={architectureOnline}
              isServerOffline={isServerOffline}
              disabled={isAnyActionLoading && !busyActions.architecture}
              onBusyChange={(busy) => setActionBusy("architecture", busy)}
              onActionComplete={loadInfraStatus}
            />

            <MettaLoadActionControl
              isServerOffline={isServerOffline}
              disabled={isAnyActionLoading && !busyActions.metta}
              onBusyChange={(busy) => setActionBusy("metta", busy)}
            />
            
          </List>
        </StyledList>
      </SidebarListContainer>
    </SidebarContainer>
  );
}
