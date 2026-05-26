import styled from "@emotion/styled";
import { Box, Typography } from "@mui/material";

export const ServerInfoWrapper = styled(Box)({
  marginBottom: 24,
  paddingInline: 8,

  display: "flex",
  justifyContent: "center",
  alignItems: "center",

  gap: 32,
  color: "#334155",
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
  background: "#334155",
});

export const Label = styled(Typography)({
  fontSize: 11,
  color: "#334155",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
});

export const Value = styled(Typography)({
  fontWeight: 600,
  color: "#334155",
});