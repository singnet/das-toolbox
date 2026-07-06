import styled from "@emotion/styled";
import { Box, Typography } from "@mui/material";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

export const ServerInfoWrapper = styled(Box)({
  marginBottom: 20,
  padding: "16px 20px",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  flexWrap: "wrap",
  gap: 24,
  color: palette.textPrimary,
  backgroundColor: palette.surface,
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 12,
  boxShadow: palette.shadow
});

export const ServerInfoBox = styled(Box)({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  textAlign: "center",
  minWidth: 120,
});

export const Divider = styled(Box)({
  width: 1,
  height: 32,
  background: palette.border,
});

export const Label = styled(Typography)({
  fontSize: 11,
  color: palette.textMuted,
  textTransform: "uppercase",
  letterSpacing: "0.06em",
  fontWeight: 600
});

export const Value = styled(Typography)({
  fontWeight: 600,
  fontSize: 18,
  color: palette.textPrimary,
});
