import { Chip, Tooltip } from "@mui/material";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { StyledRow, BodyCell, ActionsBox, ActionButton } from "./servicestable.styled";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

export function AgentRow({
  agent,
  selected,
  handleSelect,
  getStatusColor,
  getHealthStatusColor,
  onAction, 
}) {
  
  const executeAction = (e, actionType) => {
    e.stopPropagation();
    if (onAction) {
      onAction(actionType, agent.container_name);
    }
  };

  return (
    <StyledRow
      onClick={() => handleSelect(agent.container_name)}
      sx={{
        backgroundColor: selected ? "#f8fafc" : "inherit",
        cursor: "pointer",
        transition: "all 0.2s ease",
        "&:hover": { backgroundColor: selected ? "#f1f5f9" : "#f8fafc" },
      }}
    >
      <BodyCell sx={{ fontWeight: 500 }}>{agent.container_name}</BodyCell>
      <BodyCell color="textSecondary">{agent.image}</BodyCell>
      <BodyCell>{agent.port}</BodyCell>
      <BodyCell>{agent.age}</BodyCell>

      <BodyCell>{agent.cpu_percent}%</BodyCell>
      <BodyCell>{Math.round(agent.memory_mb)} GB</BodyCell>

      <BodyCell>
        <Chip
          label={agent.status}
          color={getStatusColor(agent.status)}
          size="small"
          sx={{ textTransform: 'capitalize', fontWeight: 600, fontSize: '0.75rem' }}
        />
      </BodyCell>

      <BodyCell>
        <Chip
          label={agent.service_health === "-" ? "Running" : agent.service_health}
          color={getHealthStatusColor(agent.service_health === "healthy" ? "healthy" : "unhealthy")}
          size="small"
          sx={{ textTransform: 'capitalize', fontWeight: 600, fontSize: '0.75rem' }}
        />
      </BodyCell>

      <BodyCell align="right">
        <ActionsBox>
          <Tooltip title="Start">
            <ActionButton
              onClick={(e) => executeAction(e, "START")}
              disabled={agent.status !== "running"}
              sx={{
                color: "#ffffff",
                backgroundColor: agent.status !== "running" ? palette.borderSubtle : "#33e622",
                borderColor: agent.status !== "running" ? palette.borderSubtle : "#33e622",
                "&:hover": {
                  backgroundColor: agent.status !== "running" ? palette.borderSubtle : "#24ac18",
                  borderColor: agent.status !== "running" ? palette.borderSubtle : "#24ac18"
                }
              }}
            >
              <PlayArrowIcon />
            </ActionButton>
          </Tooltip>

          <Tooltip title="Stop">
            <ActionButton
              onClick={(e) => executeAction(e, "STOP")}
              disabled={agent.status !== "running"}
              sx={{
                color: "#ffffff",
                backgroundColor: agent.status !== "running" ? palette.borderSubtle : "#dc2626",
                borderColor: agent.status !== "running" ? palette.borderSubtle : "#dc2626",
                "&:hover": {
                  backgroundColor: agent.status !== "running" ? palette.borderSubtle : "#b91c1c",
                  borderColor: agent.status !== "running" ? palette.borderSubtle : "#b91c1c"
                }
              }}
            >
              <StopCircleIcon />
            </ActionButton>
          </Tooltip>

          <Tooltip title="Restart">
            <ActionButton
              onClick={(e) => executeAction(e, "RESTART")}
              sx={{
                color: "#ffffff",
                backgroundColor: palette.accent,
                borderColor: palette.accent,
                "&:hover": {
                  backgroundColor: palette.accentHover,
                  borderColor: palette.accentHover
                }
              }}
            >
              <RestartAltIcon />
            </ActionButton>
          </Tooltip>
        </ActionsBox>
      </BodyCell>
    </StyledRow>
  );
}