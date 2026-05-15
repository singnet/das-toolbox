import {
  Table,
  TableHead,
  TableRow,
  TableBody,
} from "@mui/material";

import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { executeDashboardAction } from "../../../../api/DashboardServices";
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

  const handleSelect = (containerName) => {
    setCurrentService((current) =>
      current === containerName ? null : containerName
    );
  };

  const handleAction = async (actionType, containerName) => {
    const targetIp = currentMachine?.serverIp || "localhost";
    
    try {
      console.log(`Executing ${actionType} in ${containerName} (${targetIp})`);
      await executeDashboardAction(containerName, actionType.toLowerCase(), targetIp);
    } catch (error) {
      console.error("Error while executing action:", error);
    }
  };

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