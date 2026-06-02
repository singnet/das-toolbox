import { useMemo } from "react";
import styled from "@emotion/styled";
import { Box, Typography, Card } from "@mui/material";
import ErrorIcon from "@mui/icons-material/Error";
import BarChartIcon from "@mui/icons-material/BarChart";

import { CPUViewChart } from "./charts/CPUViewChart";
import { MemoryViewChart } from "./charts/MemoryViewChart";
import { AgentTable } from "./servicestable/ServicesTable";
import { LoadingOverlay, EmptyState } from "./LoadingSkeleton";
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

const ChartPlaceholderContainer = styled(Card)({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "360px",
  margin: "25px",
  backgroundColor: "rgba(0, 0, 0, 0.02)",
  border: "2px dashed rgba(0, 0, 0, 0.12)",
  boxShadow: "none",
  color: "#9e9e9e",
  gap: "8px"
});

function ChartPlaceholder({ title }) {
  return (
    <ChartPlaceholderContainer>
      <BarChartIcon sx={{ fontSize: 48, color: "rgba(0, 0, 0, 0.26)" }} />
      <Typography variant="subtitle1" fontWeight="600" color="text.secondary">
        {title}
      </Typography>
      <Typography variant="body2" color="text.disabled">
        WAITING FOR METRICS...
      </Typography>
    </ChartPlaceholderContainer>
  );
}

export function MainContent() {
  const {
    machines,
    currentMachine,
    currentService,
    getAggregatedMetrics,
    isConnected,
    isSwitchingHost,
    connectionError,
    machineStats
  } = useDashboardContext();

  const aggregatedData = useMemo(() => getAggregatedMetrics(), [getAggregatedMetrics]);

  const hasHistory = useMemo(() => {
    return aggregatedData?.agents?.some(agent => agent.cpu?.length > 0 || agent.memory?.length > 0) ?? false;
  }, [aggregatedData]);

  const hasInitialPayload = useMemo(() => {
    return !!(machineStats && Object.keys(machineStats).length > 0);
  }, [machineStats]);

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

  if (!isConnected && !hasInitialPayload && !isSwitchingHost) {
    return (
      <MainBoxGrid>
        <LoadingOverlay />
      </MainBoxGrid>
    );
  }

  return (
    <MainBoxGrid>
      {isSwitchingHost && <LoadingOverlay text="Switching server..." />}

      {hasHistory ? (
        <CPUViewChart 
          key={`cpu-${currentMachine?.serverIp}`} 
          machine={aggregatedData} 
          currentService={currentService} 
        />
      ) : (
        <ChartPlaceholder title="CPU VIEW" />
      )}

      {hasHistory ? (
        <MemoryViewChart 
          key={`memory-${currentMachine?.serverIp}`} 
          machine={aggregatedData} 
          currentService={currentService} 
        />
      ) : (
        <ChartPlaceholder title="MEMORY VIEW" />
      )}

      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}