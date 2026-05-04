import { styled } from "@mui/material/styles";
import { Box } from "@mui/material";

export const Container = styled(Box)({
  marginLeft: "15px",
  marginRight: "15px"
});

export const Grid = styled(Box)({
  display: "grid",
  gridTemplateColumns:
    "repeat(auto-fill, minmax(380px, 1fr))",
  gap: 16,
});

export const StyledCard = styled(Box)({
  background: "#0f172a",
  border: "1px solid #1e293b",
  borderRadius: 12,
  padding: 18,
  color: "#e2e8f0",
  minHeight: 260,

  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",

  transition: "0.2s ease",

  "&:hover": {
    borderColor: "#3b82f6",
  },
});

export const MetricsRow = styled(Box)({
  display: "flex",
  gap: 8,
  marginTop: 12,
});

export const Metric = styled(Box)({
  flex: 1,
  background: "#1e293b",
  borderRadius: 8,
  padding: "6px 8px",
  textAlign: "center",
});