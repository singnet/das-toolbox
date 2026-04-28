import {
  Table,
  TableHead,
  TableRow,
  TableBody,
} from "@mui/material";

import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";

import { AgentRow } from "./AgentRow";
import { EmptyContent } from "./EmptyContent";

import {
  TableContainer,
  HeaderCell,
} from "./servicestable.styled";

export function AgentTable({ machine }) {
  const { currentService, setCurrentService } = useDashboardContext();

  if (!machine) return null;

  const getStatusColor = (status) =>
    status === "Running" ? "success" : "error";

  const getHealthStatusColor = (health) =>
    health === "Healthy" ? "success" : "error";

  const handleSelect = (agentName) => {
    setCurrentService((current) =>
      current === agentName ? null : agentName
    );
  };

  return (
    <TableContainer elevation={1}>
      <Table>
        <TableHead>
          <TableRow>
            <HeaderCell>Container Name</HeaderCell>
            <HeaderCell>Container Info</HeaderCell>
            <HeaderCell>Port</HeaderCell>
            <HeaderCell>Age</HeaderCell>
            <HeaderCell>CPU (%)</HeaderCell>
            <HeaderCell>Memory (MB)</HeaderCell>
            <HeaderCell>Container Status</HeaderCell>
            <HeaderCell>Service Health</HeaderCell>
            <HeaderCell align="right">Actions</HeaderCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {machine.agents.length === 0 ? (
            <EmptyContent />
          ) : (
            machine.agents.map((agent) => (
              <AgentRow
                key={agent.name}
                agent={agent}
                selected={currentService === agent.name}
                handleSelect={handleSelect}
                getStatusColor={getStatusColor}
                getHealthStatusColor={getHealthStatusColor}
              />
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}