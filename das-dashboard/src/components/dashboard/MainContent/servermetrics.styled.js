import styled from "@emotion/styled";
import { palette } from "../../../pages/setup_das/SetupDasStyled";
import { Box } from "@mui/material";

export const MainBoxGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  minHeight: "auto",
  width: "100%",
  backgroundColor: "inherit",
  alignContent: "start",
  position: "relative",
  padding: "24px 28px 28px",
  gap: 16,
  boxSizing: "border-box"
});

export const ChartSection = styled(Box)({
  gridColumn: "span 2",
  display: "flex",
  flexDirection: "column",
  gap: 16,
  backgroundColor: palette.surface,
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 12,
  padding: 16,
  boxShadow: palette.shadow,
  boxSizing: "border-box"
});

export const ChartToolbar = styled(Box)({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12,
  flexWrap: "wrap"
});

export const ChartToolbarGroup = styled(Box)({
  display: "flex",
  alignItems: "center",
  gap: 8,
  flexWrap: "wrap"
});

export const ChartGrid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: 16,
  minHeight: 280
});

export const ChartPanel = styled(Box)({
  minHeight: 280,
  display: "flex",
  flexDirection: "column"
});

export const TableBox = styled(Box)({
  gridColumn: "span 2",
  padding: 0
});
