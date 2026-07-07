import { useMemo } from "react";
import styled from "@emotion/styled";
import { Box } from "@mui/material";
import ErrorIcon from "@mui/icons-material/Error";

import { CPUViewChart } from "./charts/CPUViewChart";
import { MemoryViewChart } from "./charts/MemoryViewChart";
import { AgentTable } from "./servicestable/ServicesTable";
import { LoadingOverlay, EmptyState, ChartPlaceholder } from "./LoadingSkeleton";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { palette } from "../../../pages/setup_das/SetupDasStyled";

const MainBoxGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  minHeight: "auto",
  width: "100%",
  backgroundColor: "inherit",
  alignContent: "start",
  position: "relative",
  padding: "24px 28px 28px",
  gap: 16,
  boxSizing: "border-box"
});

const ChartPanel = styled(Box)({
  backgroundColor: palette.surface,
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 12,
  padding: 16,
  boxShadow: palette.shadow,
  minHeight: 300,
  display: "flex",
  flexDirection: "column"
});

const TableBox = styled(Box)({
  gridColumn: "span 2",
  padding: 0
});

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

  const chartContainerName = useMemo(() => {
    if (!currentService) {
      return null;
    }

    const selected = mergedServices?.find((service) => service.service_key === currentService);
    return selected?.is_running ? selected.container_name : null;
  }, [mergedServices, currentService]);

  const hasChartData = useMemo(() => {
    return aggregatedMetrics?.agents?.some(
      (agent) => agent.cpu?.length > 0 || agent.memory?.length > 0
    );
  }, [aggregatedMetrics]);

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
      {hasChartData ? (
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

      {hasChartData ? (
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