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

export const ChartPanel = styled(Box)({
  backgroundColor: palette.surface,
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 12,
  padding: 16,
  boxShadow: palette.shadow,
  minHeight: 300,
  display: "flex",
  flexDirection: "column"
});

export const TableBox = styled(Box)({
  gridColumn: "span 2",
  padding: 0
});