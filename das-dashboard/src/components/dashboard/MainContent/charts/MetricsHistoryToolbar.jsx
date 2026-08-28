import { useState } from "react";
import {
  Button,
  Chip,
  CircularProgress,
  FormControlLabel,
  Menu,
  MenuItem,
  Switch,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import { METRICS_PERIODS } from "../../../../hooks/useServerTabHistory";
import { ChartToolbar, ChartToolbarGroup } from "../servermetrics.styled";
import { palette } from "../../../../pages/setup_das/SetupDasStyled";

export function MetricsHistoryToolbar({
  period,
  onPeriodChange,
  collecting,
  collectionBusy,
  historyLoading,
  onToggleCollection,
  onClearServer,
  onClearUnused,
  onClearAll,
}) {
  const [menuAnchor, setMenuAnchor] = useState(null);

  return (
    <ChartToolbar>
      <ChartToolbarGroup>
        <ToggleButtonGroup
          exclusive
          size="small"
          value={period}
          onChange={(_, value) => value && onPeriodChange(value)}
        >
          {METRICS_PERIODS.map((item) => (
            <ToggleButton
              key={item.value}
              value={item.value}
              sx={{
                textTransform: "none",
                fontSize: 12,
                fontWeight: 600,
                px: 1.5,
                "&.Mui-selected": {
                  backgroundColor: palette.accentLight,
                  color: palette.accent,
                  borderColor: palette.accentMuted,
                },
              }}
            >
              {item.label}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>

        {historyLoading && <CircularProgress size={16} sx={{ color: palette.accent }} />}
      </ChartToolbarGroup>

      <ChartToolbarGroup>
        <Chip
          size="small"
          label={collecting ? "Collecting" : "Idle"}
          sx={{
            fontWeight: 600,
            fontSize: 12,
            backgroundColor: collecting ? palette.accentLight : palette.surfaceMuted,
            color: collecting ? palette.accent : palette.textSecondary,
            border: `1px solid ${collecting ? palette.accentMuted : palette.border}`,
          }}
        />

        <FormControlLabel
          sx={{ ml: 0, mr: 0, "& .MuiFormControlLabel-label": { fontSize: 13, color: palette.textSecondary } }}
          control={
            <Switch
              size="small"
              checked={collecting}
              disabled={collectionBusy}
              onChange={onToggleCollection}
              sx={{
                "& .MuiSwitch-switchBase.Mui-checked": { color: palette.accent },
                "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
                  backgroundColor: palette.accent,
                },
              }}
            />
          }
          label="Metrics collection"
        />

        <Button
          size="small"
          variant="outlined"
          onClick={(event) => setMenuAnchor(event.currentTarget)}
          sx={{
            textTransform: "none",
            fontWeight: 600,
            fontSize: 12,
            color: palette.danger,
            borderColor: "rgba(220, 38, 38, 0.35)",
            "&:hover": {
              borderColor: palette.danger,
              backgroundColor: "rgba(220, 38, 38, 0.06)",
            },
          }}
        >
          Clear history
        </Button>

        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={() => setMenuAnchor(null)}
        >
          <MenuItem
            onClick={() => {
              setMenuAnchor(null);
              onClearServer();
            }}
          >
            This server
          </MenuItem>
          <MenuItem
            onClick={() => {
              setMenuAnchor(null);
              onClearUnused();
            }}
          >
            Unused servers
          </MenuItem>
          <MenuItem
            onClick={() => {
              setMenuAnchor(null);
              onClearAll();
            }}
          >
            All servers
          </MenuItem>
        </Menu>
      </ChartToolbarGroup>
    </ChartToolbar>
  );
}
