import styled from "@emotion/styled";
import { Circle } from "@mui/icons-material";
import { Box, Tab, Tabs, Typography } from "@mui/material";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

export const Container = styled(Box)({
  display: "flex",
  flexDirection: "column",
  backgroundColor: palette.surface,
  borderBottom: `1px solid ${palette.borderSubtle}`
});

export const Header = styled(Box)({
  display: "none"
});

export const Title = styled(Typography)({
  fontWeight: 600,
  fontSize: 14,
  color: palette.textPrimary
});

export const StyledTabs = styled(Tabs)({
  minHeight: 44,
  paddingLeft: 20,
  paddingRight: 20,

  "& .MuiTabs-indicator": {
    backgroundColor: palette.accent,
    height: 2,
    borderRadius: 2
  },

  "& .MuiTabs-flexContainer": {
    gap: 4
  }
});

export const StyledTab = styled(Tab)({
  textTransform: "none",
  fontWeight: 500,
  fontSize: 13,
  minHeight: 44,
  color: palette.textSecondary,
  borderRadius: "8px 8px 0 0",

  "&.Mui-selected": {
    color: palette.accent,
    fontWeight: 600
  },

  "&:hover": {
    color: palette.textPrimary,
    backgroundColor: palette.surfaceMuted
  }
});

export const StatusIcon = styled(Circle)({
  width: 8,
  height: 8
});
