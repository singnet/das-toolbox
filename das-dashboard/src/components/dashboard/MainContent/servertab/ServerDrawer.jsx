import {
  Box,
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  Typography,
} from "@mui/material";

import { StatusIcon } from "./servertab.styled";

export function ServerDrawer({
  drawerOpen,
  setDrawerOpen,
  machines,
  currentMachine,
  selectMachine,
  setStatusColor,
}) {
  return (
    <Drawer
      anchor="right"
      open={drawerOpen}
      onClose={() => setDrawerOpen(false)}
    >
      <Box
        sx={{
          width: 320,
          background: "#0f172a",
          color: "white",
          height: "100%",
        }}
      >
        <Box p={2}>
          <Typography variant="h6">
            All Servers
          </Typography>
        </Box>

        <Divider sx={{ borderColor: "#334155" }} />

        <List>
          {machines.map((server) => (
            <ListItemButton
              key={server.serverIp}
              onClick={() => selectMachine(server.serverIp)}
              selected={
                currentMachine?.serverIp === server.serverIp
              }
            >
              <StatusIcon
                sx={{
                  color: setStatusColor(server.running),
                  mr: 1.5,
                }}
              />

              <ListItemText
                primary={server.serverIp}
                secondary={
                  server.running ? "Online" : "Offline"
                }
                secondaryTypographyProps={{
                  color: "#94a3b8",
                }}
              />
            </ListItemButton>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}