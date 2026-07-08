import { useMemo } from "react";
import ErrorIcon from "@mui/icons-material/Error";

import { CPUViewChart } from "./charts/CPUViewChart";
import { MemoryViewChart } from "./charts/MemoryViewChart";
import { AgentTable } from "./servicestable/ServicesTable";
import { LoadingOverlay, EmptyState, ChartPlaceholder } from "./LoadingSkeleton";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { ChartPanel, MainBoxGrid, TableBox } from "./maincontent.styled";

export function MainContent() {
  const {
    machines,
    machineStats,
    currentMachine,
    currentService,
    mergedServices,
    isSwitchingHost,
    connectionError,
    aggregatedMetrics,
  } = useDashboardContext();

  const selectedService = useMemo(
    () => mergedServices?.find((service) => service.service_key === currentService),
    [mergedServices, currentService]
  );

  const chartContainerName = selectedService?.is_running
    ? selectedService.container_name
    : null;

  const isOfflineSelection = Boolean(
    currentService && selectedService && !selectedService.is_running
  );

  const hasChartData = useMemo(() => {
    return aggregatedMetrics?.agents?.some(
      (agent) => agent.cpu?.length > 0 || agent.memory?.length > 0
    );
  }, [aggregatedMetrics]);

  const offlineChartPlaceholder = (
    <ChartPlaceholder
      title="Selected service is offline"
      description="Start the service to view CPU and memory history."
    />
  );

  if (connectionError) {
    return (
      <MainBoxGrid>
        <EmptyState title={connectionError.title} description={connectionError.description} icon={ErrorIcon} />
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

  if (isSwitchingHost) {
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
            machine={aggregatedMetrics}
            currentService={chartContainerName}
            stats={machineStats}
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
            machine={aggregatedMetrics}
            currentService={chartContainerName}
            stats={machineStats}
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
