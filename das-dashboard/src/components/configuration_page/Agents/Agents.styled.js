import { styled } from "@mui/material/styles"
import { Box, Button, Typography } from "@mui/material"
import { palette } from "../../../pages/setup_das/SetupDasStyled"

export const AgentsLayout = styled(Box)({
  display: "flex",
  height: "100%",
  minHeight: 0,
  overflow: "hidden"
})

export const AgentNav = styled(Box)({
  width: 220,
  minWidth: 220,
  flexShrink: 0,
  borderRight: `1px solid ${palette.borderSubtle}`,
  backgroundColor: palette.surfaceMuted,
  overflowY: "auto",
  overflowX: "hidden",
  padding: "12px 10px",
  boxSizing: "border-box"
})

export const AgentNavGroupLabel = styled(Typography)({
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.06em",
  textTransform: "uppercase",
  color: palette.textMuted,
  padding: "10px 10px 6px"
})

export const AgentNavItem = styled(Button, {
  shouldForwardProp: (prop) => prop !== "active"
})(({ active }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "flex-start",
  gap: 10,
  width: "100%",
  textTransform: "none",
  fontWeight: active ? 600 : 500,
  fontSize: 13,
  borderRadius: 8,
  padding: "8px 10px",
  marginBottom: 2,
  minHeight: 36,
  color: active ? palette.accent : palette.textSecondary,
  backgroundColor: active ? palette.accentLight : "transparent",
  border: active ? `1px solid ${palette.accentMuted}` : "1px solid transparent",
  boxShadow: "none",

  "& .MuiSvgIcon-root": {
    fontSize: 17,
    color: active ? palette.accent : palette.textMuted
  },

  "&:hover": {
    backgroundColor: active ? palette.accentLight : palette.surface,
    boxShadow: "none"
  }
}))

export const AgentContent = styled(Box)({
  flex: 1,
  minWidth: 0,
  minHeight: 0,
  overflowY: "auto",
  padding: "24px 28px",
  boxSizing: "border-box"
})

export const AgentContentHeader = styled(Box)({
  marginBottom: 24
})

export const AgentTitle = styled(Typography)({
  fontSize: 18,
  fontWeight: 600,
  color: palette.textPrimary,
  letterSpacing: "-0.02em"
})

export const ConfigSection = styled(Box)({
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 10,
  padding: 20,
  marginBottom: 16,
  backgroundColor: palette.surface
})

export const ConfigSectionTitle = styled(Typography)({
  fontSize: 13,
  fontWeight: 600,
  color: palette.textPrimary,
  marginBottom: 16
})

export const FieldGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: 16,

  "@media (max-width: 720px)": {
    gridTemplateColumns: "1fr"
  }
})

export const SwitchGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: 8,

  "@media (max-width: 720px)": {
    gridTemplateColumns: "1fr"
  }
})

export const SaveButton = styled(Button)({
  textTransform: "none",
  fontWeight: 500,
  fontSize: 13,
  borderRadius: 8,
  height: 36,
  padding: "0 16px",
  color: "#ffffff",
  backgroundColor: palette.accent,
  boxShadow: "none",

  "&:hover": {
    backgroundColor: palette.accentHover,
    boxShadow: "none"
  }
})
