import styled from "@emotion/styled";
import { Box, Typography, Card } from "@mui/material";
import { useMemo } from "react";

import { CPUViewChart } from "./charts/CPUViewChart";
import { MemoryViewChart } from "./charts/MemoryViewChart";
import { AgentTable } from "./servicestable/ServicesTable";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { LoadingOverlay, EmptyState } from "./LoadingSkeleton";

import ErrorIcon from '@mui/icons-material/Error';
import BarChartIcon from '@mui/icons-material/BarChart';

const MainBoxGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  minHeight: "auto",
  width: "100%",
  backgroundColor: "inherit",
  alignContent: "start",
});

const TableBox = styled(Box)({
  gridColumn: "span 2",
  padding: "25px",
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
  gap: "8px",
});

export function MainContent() {
  const {
    machines,
    currentMachine,
    currentService,
    getAggregatedMetrics,
    isConnected,
    connectionError,
    machineStats
  } = useDashboardContext();

  const aggregatedData = useMemo(
    () => getAggregatedMetrics(),
    [getAggregatedMetrics]
  );

  const hasHistory = useMemo(() => {
    return !!(
      aggregatedData &&
      aggregatedData.timestamps &&
      aggregatedData.timestamps.length >= 5
    );
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

  if (machines.length === 0 && !connectionError) {
    return (
      <MainBoxGrid>
        <EmptyState />
      </MainBoxGrid>
    );
  }

  if (!isConnected && !hasInitialPayload) {
    return (
      <MainBoxGrid>
        <LoadingOverlay />
      </MainBoxGrid>
    );
  }

  return (
    <MainBoxGrid>
      {hasHistory && isConnected ? (
        <CPUViewChart machine={aggregatedData} currentService={currentService} />
      ) : (
        <ChartPlaceholderContainer>
          <BarChartIcon sx={{ fontSize: 48, color: "rgba(0, 0, 0, 0.26)" }} />
          <Typography variant="subtitle1" fontWeight="600" color="text.secondary">
            CPU VIEW
          </Typography>
          <Typography variant="body2" color="text.disabled">
            NO DATA TO BE DISPLAYED
          </Typography>
        </ChartPlaceholderContainer>
      )}

      {hasHistory && isConnected ? (
        <MemoryViewChart machine={aggregatedData} currentService={currentService} />
      ) : (
        <ChartPlaceholderContainer>
          <BarChartIcon sx={{ fontSize: 48, color: "rgba(0, 0, 0, 0.26)" }} />
          <Typography variant="subtitle1" fontWeight="600" color="text.secondary">
            MEMORY VIEW
          </Typography>
          <Typography variant="body2" color="text.disabled">
            NO DATA TO BE DISPLAYED
          </Typography>
        </ChartPlaceholderContainer>
      )}

      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}