import { Box, ListItemButton, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

export const SidebarContainer = styled(Box)({
  width: 240,
  minWidth: 240,
  flexShrink: 0,
  height: "100%",
  overflow: "hidden",
  backgroundColor: palette.sidebar,
  borderRight: `1px solid ${palette.border}`,
  display: "flex",
  flexDirection: "column"
});

export const SidebarHeader = styled(Box)({
  height: 64,
  padding: "0 20px",
  display: "flex",
  alignItems: "center",
  gap: 10,
  borderBottom: `1px solid ${palette.borderSubtle}`,
  color: palette.textPrimary,
  backgroundColor: palette.surface,

  "& .MuiSvgIcon-root": {
    fontSize: 20,
    color: palette.accent
  }
});

export const SidebarTitle = styled(Typography)({
  fontSize: 15,
  fontWeight: 600,
  color: palette.textPrimary,
  letterSpacing: "-0.01em"
});

export const SidebarListContainer = styled(Box)({
  flex: 1,
  minHeight: 0,
  overflowY: "auto",
  overflowX: "hidden",
  padding: "12px 10px",
  boxSizing: "border-box"
});

export const SectionLabel = styled(Typography)({
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.06em",
  textTransform: "uppercase",
  color: palette.textMuted,
  padding: "8px 12px 6px"
});

export const StyledList = styled(Box)({
  width: "100%"
});

export const StyledItem = styled(ListItemButton)({
  minHeight: 36,
  padding: "6px 12px",
  marginBottom: 2,
  borderRadius: 8,
  gap: 8,
  color: palette.textSecondary,
  fontSize: 13,
  fontWeight: 500,
  transition: "background-color 0.15s ease, color 0.15s ease",

  "& .MuiListItemIcon-root": {
    minWidth: 28,
    color: "inherit"
  },

  "& .MuiListItemText-primary": {
    fontSize: 13,
    fontWeight: 500
  },

  "& .MuiSvgIcon-root": {
    fontSize: 18,
    color: palette.textMuted
  },

  "&:hover": {
    backgroundColor: palette.surfaceMuted,
    color: palette.textPrimary
  },

  "&.Mui-selected": {
    backgroundColor: `${palette.accentLight} !important`,
    color: `${palette.accent} !important`,
    border: `1px solid ${palette.accentMuted}`,

    "& .MuiListItemText-primary": {
      fontWeight: 600,
      color: palette.accent
    },

    "& .MuiSvgIcon-root": {
      color: palette.accent
    }
  },

  "&.Mui-disabled": {
    opacity: 0.45
  }
});

export const ActionDivider = styled(Box)({
  height: 1,
  backgroundColor: palette.borderSubtle,
  margin: "12px 8px"
});
