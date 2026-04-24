import styled from "@emotion/styled";
import { Box, Table } from "@mui/material";
import { CPUViewChart } from "./CPUViewChart";
import { MemoryViewChart } from "./MemoryViewChart";
import { AgentTable } from "./ServicesTable";
import { useDashboardContext } from "../global_providers/DashboardContextProvider";

const MainBoxGrid = styled(Box)(
    {
        display:"grid",
        gridTemplateColumns: "1fr 1fr",
        
    }
)

const TableBox = styled(Box)(
    {
        gridColumn: "span 2",
        padding:"25px"
    }
)

export function MainContent() {
  const { currentMachine } = useDashboardContext();

  return (
    <MainBoxGrid>
      <CPUViewChart machine={currentMachine} />
      <MemoryViewChart machine={currentMachine} />

      <TableBox>
        <AgentTable machine={currentMachine} />
      </TableBox>
    </MainBoxGrid>
  );
}