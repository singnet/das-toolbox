import {
  Chip,
  Tooltip,
} from "@mui/material";

import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import RestartAltIcon from "@mui/icons-material/RestartAlt";

import {
  StyledRow,
  BodyCell,
  ActionsBox,
  ActionButton,
} from "./servicestable.styled";

export function AgentRow({
  agent,
  selected,
  handleSelect,
  getStatusColor,
  getHealthStatusColor,
}) {
  return (
    <StyledRow
      onClick={() => handleSelect(agent.name)}
      sx={{
        backgroundColor: selected ? "#f9fcd1" : "inherit",

        "&:hover": {
          backgroundColor: selected
            ? "#e5ebf1"
            : "#f9f9f9",
        },
      }}
    >
      <BodyCell>{agent.name}</BodyCell>
      <BodyCell>{agent.image}</BodyCell>
      <BodyCell>{agent.port}</BodyCell>
      <BodyCell>{agent.age}</BodyCell>
      <BodyCell>{agent.cpu}</BodyCell>
      <BodyCell>{agent.memory}</BodyCell>

      <BodyCell>
        <Chip
          label={agent.status}
          color={getStatusColor(agent.status)}
          size="medium"
        />
      </BodyCell>

      <BodyCell>
        <Chip
          label={agent.health}
          color={getHealthStatusColor(agent.health)}
          size="medium"
        />
      </BodyCell>

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
}