import { Box, Paper, styled } from "@mui/material";
import { palette } from "../../../pages/setup_das/SetupDasStyled";

export const AtomDBFormBox = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: "16px",
  width: "100%"
});

export const AtomDBConnectionForm = styled(Box)({
  display: "grid",
  gridTemplateColumns: "repeat(12, 1fr)",
  gap: "16px",
  border: `1px solid ${palette.borderSubtle}`,
  borderRadius: 10,
  padding: 20,
  width: "100%",
  boxSizing: "border-box"
});

export const GridSpan9 = styled(Box)({
  gridColumn: "span 9",
  width: "100%"
});

export const GridSpan3 = styled(Box)({
  gridColumn: "span 3",
  width: "100%"
});

export const GridSpan5 = styled(Box)({
  gridColumn: "span 5",
  width: "100%"
});

export const GridSpan6 = styled(Box)({
  gridColumn: "span 6",
  width: "100%"
});

export const GridSpan12 = styled(Box)({
  gridColumn: "span 12",
  width: "100%"
});

export const SectionTitle = styled(Box)({
  gridColumn: "span 12",
  marginTop: "8px",
  marginBottom: "4px"
});

export const GridSpan4 = styled(Box)({
  gridColumn: "span 4",
  width: "100%"
});

export const CheckboxContainer = styled(Box)({
  gridColumn: "span 12",
  display: "flex",
  gap: "24px",
  alignItems: "center",
  marginTop: "8px"
});

export const ClusterGridContainer = styled(Box)({
  gridColumn: "span 12",
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: "16px",
  alignItems: "start",
  width: "100%"
});

export const ActionButtonContainer = styled(Box)({
  gridColumn: "span 12",
  display: "flex",
  justifyContent: "flex-start",
  marginTop: "16px"
});

export const PeerCard = styled(Paper)({
  gridColumn: "span 12",
  padding: 16,
  marginBottom: 16,
  display: "grid",
  gridTemplateColumns: "repeat(12, 1fr)",
  gap: "16px",
  width: "100%",
  boxSizing: "border-box"
});

export const PeerHeaderContainer = styled(Box)({
  gridColumn: "span 12",
  display: "flex",
  gap: "16px",
  alignItems: "center",
  width: "100%"
});