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
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

export function ServerDrawer({
  drawerOpen,
  setDrawerOpen,
  machines = [],
  currentMachine,
  selectMachine,
  setStatusColor,
}) {
  return (
    <Drawer
      anchor="right"
      open={drawerOpen}
      onClose={() => setDrawerOpen(false)}
      PaperProps={{
        sx: {
          width: 320,
          backgroundColor: palette.surface,
          borderLeft: `1px solid ${palette.border}`
        }
      }}
    >
      <Box sx={{ height: "100%" }}>
        <Box sx={{ px: 2.5, py: 2 }}>
          <Typography variant="h6" sx={{ fontSize: 16, fontWeight: 600, color: palette.textPrimary }}>
            All Servers
          </Typography>
        </Box>

        <Divider sx={{ borderColor: palette.borderSubtle }} />

        <List sx={{ py: 1 }}>
          {machines.map((server) => (
            <ListItemButton
              key={server.serverIp}
              onClick={() => selectMachine(server.serverIp)}
              selected={currentMachine?.serverIp === server.serverIp}
              sx={{
                mx: 1,
                borderRadius: 2,
                mb: 0.5,
                "&.Mui-selected": {
                  backgroundColor: palette.accentLight,
                  color: palette.accent
                },
                "&:hover": {
                  backgroundColor: palette.surfaceMuted
                }
              }}
            >
              <StatusIcon
                sx={{
                  color: setStatusColor(server.running),
                  mr: 1.5,
                }}
              />

              <ListItemText
                primary={server.serverIp}
                secondary={server.running ? "Online" : "Offline"}
                primaryTypographyProps={{
                  fontSize: 13,
                  fontWeight: 500,
                  color: palette.textPrimary
                }}
                secondaryTypographyProps={{
                  fontSize: 12,
                  color: palette.textMuted
                }}
              />
            </ListItemButton>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}
