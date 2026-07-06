import { Chip, Tooltip } from "@mui/material";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { StyledRow, BodyCell, ActionsBox, ActionButton } from "./servicestable.styled";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";
import { formatCpuCell, formatMemoryCell } from "../../../../utils/serviceInventory";

export function AgentRow({
  agent,
  selected,
  handleSelect,
  getStatusColor,
  getHealthStatusColor,
  onAction,
}) {
  const isRunning = agent.is_running;
  const rowKey = agent.service_key ?? agent.container_name;

  const executeAction = (e, actionType) => {
    e.stopPropagation();
    if (!isRunning || !onAction) {
      return;
    }
    onAction(actionType, agent.container_name);
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
      <BodyCell sx={{ fontWeight: 500 }}>{agent.display_name ?? agent.container_name}</BodyCell>
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
              disabled={isRunning}
              sx={{
                color: "#ffffff",
                backgroundColor: isRunning ? palette.borderSubtle : "#33e622",
                borderColor: isRunning ? palette.borderSubtle : "#33e622",
                "&:hover": {
                  backgroundColor: isRunning ? palette.borderSubtle : "#24ac18",
                  borderColor: isRunning ? palette.borderSubtle : "#24ac18",
                },
              }}
            >
              <PlayArrowIcon />
            </ActionButton>
          </Tooltip>

          <Tooltip title="Stop">
            <ActionButton
              onClick={(e) => executeAction(e, "STOP")}
              disabled={!isRunning}
              sx={{
                color: "#ffffff",
                backgroundColor: !isRunning ? palette.borderSubtle : "#dc2626",
                borderColor: !isRunning ? palette.borderSubtle : "#dc2626",
                "&:hover": {
                  backgroundColor: !isRunning ? palette.borderSubtle : "#b91c1c",
                  borderColor: !isRunning ? palette.borderSubtle : "#b91c1c",
                },
              }}
            >
              <StopCircleIcon />
            </ActionButton>
          </Tooltip>

          <Tooltip title="Restart">
            <ActionButton
              onClick={(e) => executeAction(e, "RESTART")}
              disabled={!isRunning}
              sx={{
                color: "#ffffff",
                backgroundColor: !isRunning ? palette.borderSubtle : palette.accent,
                borderColor: !isRunning ? palette.borderSubtle : palette.accent,
                "&:hover": {
                  backgroundColor: !isRunning ? palette.borderSubtle : palette.accentHover,
                  borderColor: !isRunning ? palette.borderSubtle : palette.accentHover,
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
