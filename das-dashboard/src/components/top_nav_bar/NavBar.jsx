import { AppBar, Box, Menu, MenuItem, Toolbar, Typography } from '@mui/material'

import { styled } from "@mui/material/styles";

const MainAppBar = styled(AppBar)({
  backgroundColor: "#008cff",
  boxShadow: "2px 2px 2px 1px rgba(0, 0, 0, 0.2)",
});

const StyledToolbar = styled(Toolbar)({
  display: "flex",
  justifyContent: "space-between",
});

const AppBarItems = styled(Box)({
  display: "flex",
  gap: "10px",
  flexDirection: "row",
});

const AppBarItem = styled("a")({
  color: "white",
  textDecoration: "none",
  padding: "4px 8px",
  borderRadius: "4px",
  transition: "background-color 0.2s ease",

  "&:hover": {
    backgroundColor: "rgba(255,255,255,0.15)",
  },
});

export default function Navbar() {
  return (
    <MainAppBar position="static" elevation={0}>
      <StyledToolbar>

        <Typography variant="h6">
          Distributed AtomSpace
        </Typography>

        <AppBarItems>
          <AppBarItem href="/configuration">Configuration</AppBarItem>
          <AppBarItem href="/profiles">Profile</AppBarItem>
          <AppBarItem href="/dashboard">Dashboard</AppBarItem>
        </AppBarItems>

      </StyledToolbar>
    </MainAppBar>
  );
}