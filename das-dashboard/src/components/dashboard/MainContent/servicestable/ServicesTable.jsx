import { Table, TableHead, TableRow, TableBody } from "@mui/material";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { stopService, restartService } from "../../../../api/ServicesAPI";
import { AgentRow } from "./AgentRow";
import { EmptyContent } from "./EmptyContent";
import { TableContainer, HeaderCell } from "./servicestable.styled";
import { ServerInfoHeader } from "./ServerInfoHeader";
import { useToast } from "../../../global_providers/ToastProvider"

export function AgentTable({ machine }) {
  const { showToast } = useToast();
  
  const {
    services,
    currentService,
    setCurrentService,
    currentMachine
  } = useDashboardContext();

  const getStatusColor = (status) => (status === "running" ? "success" : "error");
  const getHealthStatusColor = (health) => (health === "healthy" ? "success" : "error");

  function handleSelect(containerName) {
    setCurrentService((current) => (current === containerName ? null : containerName));
  }

  async function handleAction(actionType, containerName) {
    const host = currentMachine?.serverIp || "localhost";
    
    try {
      console.log(`Executing ${actionType} on ${containerName} (${host})`);
      
      switch (actionType.toLowerCase()) {
        case "stop":
          showToast({
            message: `Stopping container ${containerName}...`,
            severity: "warning"
          });
          
          await stopService(containerName, host);
          
          showToast({
            message: `Container ${containerName} stopped successfully!`,
            severity: "success"
          });
          break;
          
        case "restart":
          showToast({
            message: `Restarting container ${containerName}...`,
            severity: "info"
          });
          
          await restartService(containerName, host);
          
          showToast({
            message: `Container ${containerName} restarted successfully!`,
            severity: "success"
          });
          break;
          
        default:
          console.warn(`Unknown action: ${actionType}`);
      }
    } catch (error) {
      console.error("Error while executing action:", error);
      
      showToast({
        message: `Failed to ${actionType.toLowerCase()} container ${containerName}.`,
        severity: "error",
        details: error.message || String(error)
      });
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
              <HeaderCell>Agent Name</HeaderCell>
              <HeaderCell>Image</HeaderCell>
              <HeaderCell>Port</HeaderCell>
              <HeaderCell>Age</HeaderCell>
              <HeaderCell>CPU (container %)</HeaderCell>
              <HeaderCell>Memory (GB)</HeaderCell>
              <HeaderCell>Status</HeaderCell>
              <HeaderCell>Health</HeaderCell>
              <HeaderCell align="center">Actions</HeaderCell>
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