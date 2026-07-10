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
  ActionDivider
} from "./sidebar.styled";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { getConfigHosts } from "../../../../api/ConfigAPI";
import { fetchInfraStatusForAllHosts } from "../../../../utils/infraStatus";

import { ArchitectureActionControl } from "./ArchitectureActionControl";
import { AtomDBActionControl } from "./AtomDBActionControl";
import { MettaLoadActionControl } from "./MettaLoadActionControl";

const navigationItems = [
  { key: "servers", label: "Servers", icon: SettingsEthernet, context: "servers" },
  { key: "agents", label: "Agents", icon: Polyline, context: "agents" }
];

export function SideBar() {
  const [selected, setSelected] = useState("servers");
  const [busyActions, setBusyActions] = useState({});
  const [atomDbOnline, setAtomDbOnline] = useState(false);
  const [architectureOnline, setArchitectureOnline] = useState(false);

  const {
    setCurrentContext,
    currentMachine,
    mergedServices,
    isSwitchingHost,
  } = useDashboardContext();

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
            <MettaLoadActionControl
              isServerOffline={isServerOffline}
              disabled={isAnyActionLoading && !busyActions.metta}
              onBusyChange={(busy) => setActionBusy("metta", busy)}
            />

            <ArchitectureActionControl
              atomDbOnline={atomDbOnline}
              architectureOnline={architectureOnline}
              mergedServices={mergedServices}
              isServerOffline={isServerOffline}
              disabled={isAnyActionLoading && !busyActions.architecture}
              onBusyChange={(busy) => setActionBusy("architecture", busy)}
              onActionComplete={loadInfraStatus}
            />

            <AtomDBActionControl
              atomDbOnline={atomDbOnline}
              isServerOffline={isServerOffline}
              disabled={isAnyActionLoading && !busyActions.atomdb}
              onBusyChange={(busy) => setActionBusy("atomdb", busy)}
              onActionComplete={loadInfraStatus}
            />
          </List>
        </StyledList>
      </SidebarListContainer>
    </SidebarContainer>
  );
}
