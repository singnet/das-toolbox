import { Table, TableHead, TableRow, TableBody } from "@mui/material";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";
import { useServerTabMetricsContext } from "../../../global_providers/ServerTabMetricsProvider";
import { stopService, restartService, startService } from "../../../../api/ServicesAPI";
import { extractApiError } from "../../../../api/APIUtils";
import { AgentRow } from "./AgentRow";
import { EmptyContent } from "./EmptyContent";
import { TableContainer, HeaderCell } from "./servicestable.styled";
import { ServerInfoHeader } from "./ServerInfoHeader";
import { useToast } from "../../../global_providers/ToastProvider";

export function AgentTable({ machine }) {
  const { showToast } = useToast();

  const { currentMachine, currentService, setCurrentService } = useDashboardContext();
  const { hostMergedServices } = useServerTabMetricsContext();

  const getStatusColor = (status) => {
    if (status === "running") return "success";
    if (status === "offline") return "default";
    return "error";
  };
  const getHealthStatusColor = (health) => (health === "healthy" ? "success" : "error");

  function handleSelect(serviceKey) {
    setCurrentService((current) => (current === serviceKey ? null : serviceKey));
  }

  async function handleAction(actionType, serviceKey) {
    const host = currentMachine?.serverIp || "localhost";

    try {
      if (actionType.toLowerCase() === "start") {
        showToast({ message: `Starting service ${serviceKey}...`, severity: "warning" });
        await startService(serviceKey, host);
        showToast({ message: `Service ${serviceKey} started successfully!`, severity: "success" });
        return;
      }

      if (actionType.toLowerCase() === "stop") {
        showToast({ message: `Stopping service ${serviceKey}...`, severity: "warning" });
        await stopService(serviceKey, host);
        showToast({ message: `Service ${serviceKey} stopped successfully!`, severity: "success" });
        return;
      }

      if (actionType.toLowerCase() === "restart") {
        showToast({ message: `Restarting service ${serviceKey}...`, severity: "info" });
        await restartService(serviceKey, host);
        showToast({ message: `Service ${serviceKey} restarted successfully!`, severity: "success" });
      }
    } catch (error) {
      console.error("Error while executing action:", error);
      const { message, details, severity } = extractApiError(
        error,
        `Failed to ${actionType.toLowerCase()} service ${serviceKey}.`
      );
      showToast({ message, severity, details });
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
            {hostMergedServices.length === 0 ? (
              <EmptyContent />
            ) : (
              hostMergedServices.map((service) => (
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
