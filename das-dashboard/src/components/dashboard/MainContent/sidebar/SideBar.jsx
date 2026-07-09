import { useState } from "react";
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
import { getInfraStatus } from "../../../../utils/serviceInventory";

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

  const {
    setCurrentContext,
    currentMachine,
    mergedServices,
    isSwitchingHost
  } = useDashboardContext();

  const currentHost = currentMachine?.serverIp;
  const isServerOffline = !currentHost || isSwitchingHost;
  const { atomDbOnline, architectureOnline } = getInfraStatus(mergedServices);
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
              isServerOffline={isServerOffline}
              disabled={isAnyActionLoading && !busyActions.architecture}
              onBusyChange={(busy) => setActionBusy("architecture", busy)}
            />

            <AtomDBActionControl
              atomDbOnline={atomDbOnline}
              isServerOffline={isServerOffline}
              disabled={isAnyActionLoading && !busyActions.atomdb}
              onBusyChange={(busy) => setActionBusy("atomdb", busy)}
            />
          </List>
        </StyledList>
      </SidebarListContainer>
    </SidebarContainer>
  );
}
