import { Chip, Tooltip } from "@mui/material";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { StyledRow, BodyCell, ActionsBox, ActionButton } from "./servicestable.styled";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";
import { formatCpuCell, formatMemoryCell, serviceDisplayName, serviceRowKey } from "../../../../utils/serviceRows";

export function AgentRow({
  agent,
  selected,
  handleSelect,
  getStatusColor,
  getHealthStatusColor,
  onAction,
}) {
  const isRunning = agent.is_running;
  const rowKey = serviceRowKey(agent);
  const command = agent.service_command_label;
  const canExecuteAction = Boolean(command);

  const executeAction = (e, actionType) => {
    e.stopPropagation();
    if (!onAction || !command) {
      return;
    }

    const action = actionType.toLowerCase();
    if (action === "start" && isRunning) {
      return;
    }
    if ((action === "stop" || action === "restart") && !isRunning) {
      return;
    }

    onAction(actionType, command);
  };

  const statusLabel = agent.status === "offline" ? "Offline" : agent.status;
  const healthLabel = agent.service_health === "-" || !agent.service_health
    ? (isRunning ? "Running" : "-")
    : agent.service_health;

  return (
    <StyledRow
      onClick={() => handleSelect(rowKey)}
      sx={{
        backgroundColor: selected ? palette.accentLight : "inherit",
        cursor: "pointer",
        transition: "background-color 0.15s ease",
        "&:hover": {
          backgroundColor: selected ? palette.accentLight : palette.surfaceMuted,
        },
      }}
    >
      <BodyCell sx={{ fontWeight: 500 }}>{serviceDisplayName(agent)}</BodyCell>
      <BodyCell color="textSecondary">{agent.image}</BodyCell>
      <BodyCell>{agent.port}</BodyCell>
      <BodyCell>{agent.age}</BodyCell>
      <BodyCell>{formatCpuCell(agent)}</BodyCell>
      <BodyCell>{formatMemoryCell(agent)}</BodyCell>

      <BodyCell>
        <Chip
          label={statusLabel}
          color={getStatusColor(agent.status)}
          size="small"
          sx={{ textTransform: "capitalize", fontWeight: 600, fontSize: "0.75rem" }}
        />
      </BodyCell>

      <BodyCell>
        <Chip
          label={healthLabel}
          color={isRunning ? getHealthStatusColor(healthLabel === "healthy" ? "healthy" : "unhealthy") : "default"}
          size="small"
          sx={{ textTransform: "capitalize", fontWeight: 600, fontSize: "0.75rem" }}
        />
      </BodyCell>

      <BodyCell align="right">
        <ActionsBox>
          <Tooltip title="Start">
            <ActionButton
              onClick={(e) => executeAction(e, "START")}
              disabled={isRunning || !canExecuteAction}
              sx={{
                color: "#ffffff",
                backgroundColor: isRunning || !canExecuteAction ? palette.borderSubtle : palette.success,
                borderColor: isRunning || !canExecuteAction ? palette.borderSubtle : palette.success,
                "&:hover": {
                  backgroundColor: isRunning || !canExecuteAction ? palette.borderSubtle : palette.successHover,
                  borderColor: isRunning || !canExecuteAction ? palette.borderSubtle : palette.successHover,
                },
              }}
            >
              <PlayArrowIcon />
            </ActionButton>
          </Tooltip>

          <Tooltip title="Stop">
            <ActionButton
              onClick={(e) => executeAction(e, "STOP")}
              disabled={!isRunning || !canExecuteAction}
              sx={{
                color: "#ffffff",
                backgroundColor: !isRunning || !canExecuteAction ? palette.borderSubtle : palette.danger,
                borderColor: !isRunning || !canExecuteAction ? palette.borderSubtle : palette.danger,
                "&:hover": {
                  backgroundColor: !isRunning || !canExecuteAction ? palette.borderSubtle : palette.dangerHover,
                  borderColor: !isRunning || !canExecuteAction ? palette.borderSubtle : palette.dangerHover,
                },
              }}
            >
              <StopCircleIcon />
            </ActionButton>
          </Tooltip>

          <Tooltip title="Restart">
            <ActionButton
              onClick={(e) => executeAction(e, "RESTART")}
              disabled={!isRunning || !canExecuteAction}
              sx={{
                color: "#ffffff",
                backgroundColor: !isRunning || !canExecuteAction ? palette.borderSubtle : palette.accent,
                borderColor: !isRunning || !canExecuteAction ? palette.borderSubtle : palette.accent,
                "&:hover": {
                  backgroundColor: !isRunning || !canExecuteAction ? palette.borderSubtle : palette.accentHover,
                  borderColor: !isRunning || !canExecuteAction ? palette.borderSubtle : palette.accentHover,
                },
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
