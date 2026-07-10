import { Box, Checkbox, ListItemIcon, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

export const ControlRoot = styled(Box)({
  marginBottom: 2,
  borderRadius: 8,
  overflow: "hidden",
  border: `1px solid transparent`,
  transition: "border-color 0.15s ease",

  "&[data-expanded='true']": {
    borderColor: palette.borderSubtle,
    backgroundColor: palette.surface,
  },
});

export const ActionRow = styled(Box)({
  display: "flex",
  alignItems: "stretch",
  minHeight: 36,
  borderRadius: 8,
  overflow: "hidden",
});

export const PrimaryAction = styled(Box, {
  shouldForwardProp: (prop) => prop !== "disabled" && prop !== "online",
})(({ disabled, online }) => ({
  flex: 1,
  display: "flex",
  alignItems: "center",
  gap: 8,
  padding: "6px 12px",
  color: disabled ? palette.textMuted : palette.textSecondary,
  fontSize: 13,
  fontWeight: 500,
  cursor: disabled ? "not-allowed" : "pointer",
  opacity: disabled ? 0.45 : 1,
  transition: "background-color 0.15s ease, color 0.15s ease",

  ...(!disabled && {
    "&:hover": {
      backgroundColor: palette.surfaceMuted,
      color: online ? palette.danger : palette.textPrimary,
    },
  }),
}));

export const ExpandToggle = styled(Box, {
  shouldForwardProp: (prop) => prop !== "disabled" && prop !== "expanded",
})(({ disabled, expanded }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  width: 36,
  borderLeft: `1px solid ${palette.borderSubtle}`,
  color: disabled ? palette.textMuted : palette.textSecondary,
  cursor: disabled ? "not-allowed" : "pointer",
  opacity: disabled ? 0.45 : 1,
  transition: "background-color 0.15s ease, transform 0.2s ease",
  transform: expanded ? "rotate(180deg)" : "rotate(0deg)",

  ...(!disabled && {
    "&:hover": {
      backgroundColor: palette.surfaceMuted,
      color: palette.textPrimary,
    },
  }),
}));

export const ActionIcon = styled(ListItemIcon)({
  minWidth: 28,
  color: "inherit",

  "& .MuiSvgIcon-root": {
    fontSize: 18,
  },
});

export const AgentPanel = styled(Box)({
  padding: "4px 8px 8px",
  borderTop: `1px solid ${palette.borderSubtle}`,
  backgroundColor: palette.surfaceMuted,
});

export const AgentOption = styled(Box)({
  display: "flex",
  alignItems: "center",
  minHeight: 30,
  paddingLeft: 4,
  borderRadius: 6,

  "&:hover": {
    backgroundColor: palette.surface,
  },
});

export const AgentCheckbox = styled(Checkbox)({
  padding: 4,

  "& .MuiSvgIcon-root": {
    fontSize: 18,
  },
});

export const AgentLabel = styled(Typography)({
  fontSize: 12,
  fontWeight: 500,
  color: palette.textSecondary,
  flex: 1,
});

export const GroupLabel = styled(Typography)({
  fontSize: 10,
  fontWeight: 600,
  letterSpacing: "0.06em",
  textTransform: "uppercase",
  color: palette.textMuted,
  padding: "6px 8px 2px",
});
