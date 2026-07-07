import { Table, TableHead, TableRow, TableBody } from "@mui/material";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { stopService, restartService, startService } from "../../../../api/ServicesAPI";
import { AgentRow } from "./AgentRow";
import { EmptyContent } from "./EmptyContent";
import { TableContainer, HeaderCell } from "./servicestable.styled";
import { ServerInfoHeader } from "./ServerInfoHeader";
import { useToast } from "../../../global_providers/ToastProvider"

export function AgentTable({ machine }) {
  const { showToast } = useToast();
  
  const {
    mergedServices,
    currentService,
    setCurrentService,
    currentMachine
  } = useDashboardContext();

  const getStatusColor = (status) => {
    if (status === "running") return "success";
    if (status === "offline") return "default";
    return "error";
  };
  const getHealthStatusColor = (health) => (health === "healthy" ? "success" : "error");

  function handleSelect(serviceKey) {
    setCurrentService((current) => (current === serviceKey ? null : serviceKey));
  }

  async function handleAction(actionType, containerName, serviceKey) {
    const host = currentMachine?.serverIp || "localhost";
    const serviceId = serviceKey || containerName;

    try {
      if (actionType.toLowerCase() === "start") {
        showToast({ message: `Starting service ${serviceId}...`, severity: "warning" });
        await startService(serviceId, host);
        showToast({ message: `Service ${serviceId} started successfully!`, severity: "success" });
        return;
      }

      if (actionType.toLowerCase() === "stop") {
        showToast({ message: `Stopping service ${containerName}...`, severity: "warning" });
        await stopService(containerName, host);
        showToast({ message: `Service ${containerName} stopped successfully!`, severity: "success" });
        return;
      }

      if (actionType.toLowerCase() === "restart") {
        showToast({ message: `Restarting service ${containerName}...`, severity: "info" });
        await restartService(containerName, host);
        showToast({ message: `Service ${containerName} restarted successfully!`, severity: "success" });
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
              <HeaderCell>Service Name</HeaderCell>
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
            {mergedServices.length === 0 ? (
              <EmptyContent />
            ) : (
              mergedServices.map((service) => (
                <AgentRow
                  key={service.service_key}
                  agent={service}
                  selected={currentService === service.service_key}
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