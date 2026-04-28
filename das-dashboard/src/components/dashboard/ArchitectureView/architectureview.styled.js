import { styled } from "@mui/material/styles";
import { Box } from "@mui/material";

export const Container = styled(Box)({
  padding: 20,
});

export const Grid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
  gap: 14,
});

export const ServerCard = styled(Box)({
  background: "#0f172a",
  border: "1px solid #1e293b",
  borderRadius: 12,
  padding: 14,
  color: "#e2e8f0",
  minHeight: 120,

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