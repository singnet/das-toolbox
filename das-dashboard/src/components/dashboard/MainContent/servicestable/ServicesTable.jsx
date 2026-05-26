import {
  Table,
  TableHead,
  TableRow,
  TableBody,
} from "@mui/material";

import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";

import {
  startService,
  stopService,
  restartService,
} from "../../../../api/ServicesAPI";

import { AgentRow } from "./AgentRow";
import { EmptyContent } from "./EmptyContent";
import { TableContainer, HeaderCell } from "./servicestable.styled";
import { ServerInfoHeader } from "./ServerInfoHeader";

export function AgentTable({ machine }) {

  const {
    services,
    currentService,
    setCurrentService,
    currentMachine
  } = useDashboardContext();

  const getStatusColor = (status) =>
    status === "running" ? "success" : "error";

  const getHealthStatusColor = (health) =>
    health === "healthy" ? "success" : "error";

  function handleSelect(containerName) {
    setCurrentService(current =>
      current === containerName ? null : containerName
    );
  }

  async function handleAction(actionType, containerName) {

    const host = currentMachine?.serverIp || "localhost";

    try {

      console.log(`Executing ${actionType} on ${containerName} (${host})`);

      switch (actionType.toLowerCase()) {

        case "start":
          await startService(containerName, host);
          break;

        case "stop":
          await stopService(containerName, host);
          break;

        case "restart":
          await restartService(containerName, host);
          break;

        default:
          console.warn(`Unknown action: ${actionType}`);
      }

    } catch (error) {
      console.error("Error while executing action:", error);
    }
  }

  if (!machine) return null;

  return (
    <>
      <ServerInfoHeader />

      <TableContainer elevation={1}>
        <Table>
          <TableHead>
            <TableRow>
              <HeaderCell>Container Name</HeaderCell>
              <HeaderCell>Image</HeaderCell>
              <HeaderCell>Port</HeaderCell>
              <HeaderCell>Age</HeaderCell>
              <HeaderCell>CPU (% / Core)</HeaderCell>
              <HeaderCell>Memory (MB)</HeaderCell>
              <HeaderCell>Status</HeaderCell>
              <HeaderCell>Health</HeaderCell>
              <HeaderCell align="right">Actions</HeaderCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {services.length === 0 ? (
              <EmptyContent />
            ) : (
              services.map((service) => (
                <AgentRow
                  key={service.container_name}
                  agent={service}
                  selected={currentService === service.container_name}
                  handleSelect={handleSelect}
                  onAction={handleAction}
                  getStatusColor={getStatusColor}
                  getHealthStatusColor={getHealthStatusColor}
                />
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}