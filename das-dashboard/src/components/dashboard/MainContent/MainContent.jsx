import { useMemo } from "react";
import ErrorIcon from "@mui/icons-material/Error";

import { CPUViewChart } from "./charts/CPUViewChart";
import { MemoryViewChart } from "./charts/MemoryViewChart";
import { AgentTable } from "./servicestable/ServicesTable";
import { LoadingOverlay, EmptyState, ChartPlaceholder } from "./LoadingSkeleton";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { useServerTabMetricsContext } from "../../global_providers/ServerTabMetricsProvider";
import { ChartPanel, MainBoxGrid, TableBox } from "./maincontent.styled";

export function MainContent() {
  const { machines, currentMachine, currentService } = useDashboardContext();
  const {
    hostMachineStats,
    hostMergedServices,
    hostStreamSwitching,
    hostStreamError,
    hostMetricsRollup,
  } = useServerTabMetricsContext();

  const selectedService = useMemo(
    () => hostMergedServices?.find((service) => service.service_key === currentService),
    [hostMergedServices, currentService]
  );

  const chartContainerName = selectedService?.is_running
    ? selectedService.container_name
    : null;

  const isOfflineSelection = Boolean(
    currentService && selectedService && !selectedService.is_running
  );

  const hasChartData = useMemo(() => {
    return hostMetricsRollup?.agents?.some(
      (agent) => agent.cpu?.length > 0 || agent.memory?.length > 0
    );
  }, [hostMetricsRollup]);

  const offlineChartPlaceholder = (
    <ChartPlaceholder
      title="Selected service is offline"
      description="Start the service to view CPU and memory history."
    />
  );

  if (hostStreamError) {
    return (
      <MainBoxGrid>
        <EmptyState title={hostStreamError.title} description={hostStreamError.description} icon={ErrorIcon} />
      </MainBoxGrid>
    );
  }

  if (machines.length === 0) {
    return (
      <MainBoxGrid>
        <EmptyState />
      </MainBoxGrid>
    );
  }

  if (hostStreamSwitching) {
    return (
      <MainBoxGrid>
        <LoadingOverlay text="Connecting and establishing stream..." />
      </MainBoxGrid>
    );
  }

  return (
    <MainBoxGrid>
      {isOfflineSelection ? (
        <ChartPanel>{offlineChartPlaceholder}</ChartPanel>
      ) : hasChartData ? (
        <ChartPanel>
          <CPUViewChart
            key={`cpu-${currentMachine?.serverIp}`}
            machine={hostMetricsRollup}
            currentService={chartContainerName}
            stats={hostMachineStats}
          />
        </ChartPanel>
      ) : (
        <ChartPlaceholder title="CPU Usage History" />
      )}

      {isOfflineSelection ? (
        <ChartPanel>{offlineChartPlaceholder}</ChartPanel>
      ) : hasChartData ? (
        <ChartPanel>
          <MemoryViewChart
            key={`memory-${currentMachine?.serverIp}`}
            machine={hostMetricsRollup}
            currentService={chartContainerName}
            stats={hostMachineStats}
          />
        </ChartPanel>
      ) : (
        <ChartPlaceholder title="Memory Usage History" />
      )}

      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}
