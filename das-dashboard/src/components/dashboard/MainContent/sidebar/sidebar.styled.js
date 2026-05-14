import { Box, List, ListItemButton, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";

export const SidebarContainer = styled(Box)({
  width: 240,
  backgroundColor: "#f5f5f5",
  borderRight: "1px solid #ddd",
  padding: "16px 0",
  height: "100vh",
  display: "flex",
  flexDirection: "column",
});

export const Title = styled(Typography)({
  padding: "0 16px",
  marginBottom: "16px",
  fontWeight: "bold",
});

export const StyledList = styled(List)({
  width: "100%",
});

export const SectionLabel = styled(Typography)({
  fontSize: "12px",
  fontWeight: 600,
  opacity: 0.6,
  padding: "8px 16px",
});

export const StyledItem = styled(ListItemButton)({
  padding: "8px 16px",
  gap: "8px",

  "&.Mui-selected": {
    backgroundColor: "#008cff20",
    borderLeft: "3px solid #008cff",
  },

  "&:hover": {
    backgroundColor: "#e3f2fd",
  },
});