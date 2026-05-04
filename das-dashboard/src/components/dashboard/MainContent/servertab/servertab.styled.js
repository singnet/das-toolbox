import styled from "@emotion/styled";
import { Circle } from "@mui/icons-material";
import { Box, Tab, Tabs, Typography } from "@mui/material";


export const Container = styled(Box)({
  display: "flex",
  flexDirection: "column",
});

export const Header = styled(Box)({
  padding: "10px 16px",
  backgroundColor: "#008cff",
  color: "white",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
});

export const Title = styled(Typography)({
  fontWeight: "bold",
});

export const StyledTabs = styled(Tabs)({
  borderBottom: "1px solid #ddd",

  "& .MuiTabs-indicator": {
    backgroundColor: "#008cff",
  },
});

export const StyledTab = styled(Tab)({
  textTransform: "none",
  fontWeight: 500,

  "&.Mui-selected": {
    color: "#008cff",
  },
});

export const StatusIcon = styled(Circle)({
  width: "10px",
  height: "10px",
});