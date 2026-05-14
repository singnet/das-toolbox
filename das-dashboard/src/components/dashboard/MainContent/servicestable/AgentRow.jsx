import { Chip, Tooltip } from "@mui/material";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { StyledRow, BodyCell, ActionsBox, ActionButton } from "./servicestable.styled";

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
        backgroundColor: selected ? "#f8fafc" : "inherit", // Ajustado para um tom mais suave
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
      <BodyCell>{Math.round(agent.memory_mb)} MB</BodyCell>

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
              disabled={agent.status === "running"}
              sx={{ color: agent.status === "running" ? "action.disabled" : "success.main" }}
            >
              <PlayCircleIcon fontSize="small" />
            </ActionButton>
          </Tooltip>

          <Tooltip title="Stop">
            <ActionButton 
              onClick={(e) => executeAction(e, "STOP")}
              disabled={agent.status !== "running"}
              sx={{ color: agent.status !== "running" ? "action.disabled" : "error.main" }}
            >
              <StopCircleIcon fontSize="small" />
            </ActionButton>
          </Tooltip>

          <Tooltip title="Restart">
            <ActionButton 
              onClick={(e) => executeAction(e, "RESTART")}
              sx={{ color: "primary.main" }}
            >
              <RestartAltIcon fontSize="small" />
            </ActionButton>
          </Tooltip>
        </ActionsBox>
      </BodyCell>
    </StyledRow>
  );
}