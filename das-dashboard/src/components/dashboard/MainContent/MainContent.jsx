import { useMemo } from "react";
import styled from "@emotion/styled";
import { Box } from "@mui/material";
import ErrorIcon from "@mui/icons-material/Error";

import { CPUViewChart } from "./charts/CPUViewChart";
import { MemoryViewChart } from "./charts/MemoryViewChart";
import { AgentTable } from "./servicestable/ServicesTable";
import { LoadingOverlay, EmptyState, ChartPlaceholder } from "./LoadingSkeleton";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";

const MainBoxGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  minHeight: "auto",
  width: "100%",
  backgroundColor: "inherit",
  alignContent: "start",
  position: "relative"
});

const TableBox = styled(Box)({
  gridColumn: "span 2",
  padding: "25px"
});

export function MainContent() {
  const {
    machines,
    currentMachine,
    currentService,
    isSwitchingHost,
    connectionError,
    aggregatedMetrics,
    services,
    isConnected
  } = useDashboardContext();

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
        <CPUViewChart 
          key={`cpu-${currentMachine?.serverIp}`} 
          machine={aggregatedMetrics} 
          currentService={currentService} 
        />
      ) : (
        <ChartPlaceholder title="CPU Usage History" />
      )}

      {hasChartData ? (
        <MemoryViewChart 
          key={`memory-${currentMachine?.serverIp}`} 
          machine={aggregatedMetrics} 
          currentService={currentService} 
        />
      ) : (
        <ChartPlaceholder title="Memory Usage History" />
      )}

      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}