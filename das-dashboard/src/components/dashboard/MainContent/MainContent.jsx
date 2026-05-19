import styled from "@emotion/styled";
import { Box } from "@mui/material";
import { CPUViewChart } from "./CPUViewChart";
import { MemoryViewChart } from "./MemoryViewChart";
import { AgentTable } from "./servicestable/ServicesTable";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { LoadingOverlay, EmptyState } from "./LoadingSkeleton";

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

export function MainContent() {
  const {
    machines,
    machineStats,
    currentMachine,
    currentService,
    getAggregatedMetrics,
  } = useDashboardContext();

  const aggregatedData = getAggregatedMetrics();

  if (machines.length === 0) {
    return (
      <MainBoxGrid>
        <EmptyState />
      </MainBoxGrid>
    );
  }

  const isLoading = !machineStats || aggregatedData.agents.length === 0;

  if (isLoading) {
    return (
      <MainBoxGrid>
        <LoadingOverlay />
      </MainBoxGrid>
    );
  }

  return (
    <MainBoxGrid>
      <CPUViewChart machine={aggregatedData} currentService={currentService} />
      <MemoryViewChart machine={aggregatedData} currentService={currentService} />
      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}