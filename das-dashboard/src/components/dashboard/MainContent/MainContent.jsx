import styled from "@emotion/styled";
import { Box } from "@mui/material";

import { CPUViewChart } from "./CPUViewChart";
import { MemoryViewChart } from "./MemoryViewChart";
import { AgentTable } from "./ServicesTable";

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
  } = useDashboardContext();

  return (
    <MainBoxGrid>
      <CPUViewChart
        machine={currentMachine}
        currentService={currentService}
      />

      <MemoryViewChart
        machine={currentMachine}
        currentService={currentService}
      />

      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}