import { styled } from "@mui/material/styles";
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Paper,
  IconButton,
  Box,
  Chip,
  Tooltip,
} from "@mui/material";

import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import RestartAltIcon from "@mui/icons-material/RestartAlt";

import { useDashboardContext } from "../global_providers/DashboardContextProvider";

const TableContainer = styled(Paper)({
  border: "1px solid #ccc",
  borderRadius: "8px",
  overflow: "hidden",
});

const HeaderCell = styled(TableCell)({
  fontWeight: "bold",
  fontSize: "14px",
  backgroundColor: "#f0f0f0",
  padding: "14px",
});

const BodyCell = styled(TableCell)({
  fontSize: "14px",
  padding: "14px",
});

const StyledRow = styled(TableRow)({
  cursor: "pointer",
  transition: "0.2s ease",

  "&:hover": {
    backgroundColor: "#f9f9f9",
  },
});

const ActionsBox = styled(Box)({
  display: "flex",
  gap: "8px",
  justifyContent: "flex-end",
});

const ActionButton = styled(IconButton)({
  padding: "6px",
});

export function AgentTable({ machine }) {
  const { currentService, setCurrentService } = useDashboardContext();

  if (!machine) return null;

  const getStatusColor = (status) =>
    status === "Running" ? "success" : "error";

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
            <HeaderCell>Port</HeaderCell>
            <HeaderCell>Status</HeaderCell>
            <HeaderCell>Age</HeaderCell>
            <HeaderCell>CPU (%)</HeaderCell>
            <HeaderCell>Memory (MB)</HeaderCell>
            <HeaderCell align="right">Actions</HeaderCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {machine.agents.length === 0 ? (
            <TableRow>
              <BodyCell colSpan={7} align="center">
                No agents running
              </BodyCell>
            </TableRow>
          ) : (
            machine.agents.map((agent) => {
              const selected = currentService === agent.name;

              return (
                <StyledRow
                  key={agent.name}
                  onClick={() => handleSelect(agent.name)}
                  sx={{
                    backgroundColor: selected
                      ? "#f9fcd1"
                      : "inherit",

                    "&:hover": {
                      backgroundColor: selected
                        ? "#e5ebf1"
                        : "#f9f9f9",
                    },
                  }}
                >
                  <BodyCell>{agent.name}</BodyCell>
                  <BodyCell>{agent.port}</BodyCell>

                  <BodyCell>
                    <Chip
                      label={agent.status}
                      color={getStatusColor(agent.status)}
                      size="medium"
                    />
                  </BodyCell>

                  <BodyCell>{agent.age}</BodyCell>
                  <BodyCell>{agent.cpu}</BodyCell>
                  <BodyCell>{agent.memory}</BodyCell>

                  <BodyCell align="right">
                    <ActionsBox>
                      
                      <Tooltip title="Start">
                        <ActionButton
                          color="success"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <PlayCircleIcon />
                        </ActionButton>
                      </Tooltip>

                      <Tooltip title="Stop">
                        <ActionButton
                          color="error"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <StopCircleIcon />
                        </ActionButton>
                      </Tooltip>

                      <Tooltip title="Restart">
                        <ActionButton
                          onClick={(e) => e.stopPropagation()}
                        >
                          <RestartAltIcon />
                        </ActionButton>
                      </Tooltip>

                    </ActionsBox>
                  </BodyCell>
                </StyledRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}