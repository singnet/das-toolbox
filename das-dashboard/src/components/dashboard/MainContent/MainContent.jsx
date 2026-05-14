import styled from "@emotion/styled";
import { Box } from "@mui/material";

import { CPUViewChart } from "./CPUViewChart";
import { MemoryViewChart } from "./MemoryViewChart";
import { AgentTable } from "./servicestable/ServicesTable";

import { useDashboardContext } from "../../global_providers/DashboardContextProvider";

const MainBoxGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
});

const TableBox = styled(Box)({
  gridColumn: "span 2",
  padding: "25px",
});

export function MainContent() {
  const {
    currentMachine,
    currentService,
    getAggregatedMetrics,
  } = useDashboardContext();

  const aggregatedData = getAggregatedMetrics();

  return (
    <MainBoxGrid>
      <CPUViewChart
        machine={aggregatedData} 
        currentService={currentService}
      />

      <MemoryViewChart
        machine={aggregatedData}
        currentService={currentService}
      />

      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}