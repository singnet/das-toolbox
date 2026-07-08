import { Box, Typography } from "@mui/material";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { CPUViewChart } from "../MainContent/charts/CPUViewChart";
import { MemoryViewChart } from "../MainContent/charts/MemoryViewChart";
import { palette } from "../../../pages/setup_das/SetupDasStyled";

export function ServiceChart({ selectedService }) {
  const { aggregatedMetricsByHost, machineStatsByHost } = useDashboardContext();

  const aggregated = aggregatedMetricsByHost[selectedService.serverIp] || { agents: [] };
  const machine = {
    agents: aggregated.agents.filter((agent) => agent.name === selectedService.name),
  };

  if (machine.agents.length === 0) {
    return null;
  }

  return (
    <Box mt={4} key={selectedService.id}>
      <Typography
        variant="h6"
        sx={{ fontWeight: 600, mb: 2, color: palette.textPrimary, fontSize: 16 }}
      >
        Metrics — {selectedService.displayName} ({selectedService.serverIp})
      </Typography>

      <Box
        display="grid"
        gridTemplateColumns={{ xs: "1fr", lg: "1fr 1fr" }}
        gap={2}
      >
        <ServiceChartPanel title="CPU Usage In-Time">
          <CPUViewChart machine={machine} currentService={selectedService.name} />
        </ServiceChartPanel>

        <ServiceChartPanel title="Memory Usage In-Time">
          <MemoryViewChart
            machine={machine}
            currentService={selectedService.name}
            stats={machineStatsByHost[selectedService.serverIp]}
          />
        </ServiceChartPanel>
      </Box>
    </Box>
  );
}

function ServiceChartPanel({ title, children }) {
  return (
    <Box
      sx={{
        backgroundColor: palette.surface,
        border: `1px solid ${palette.borderSubtle}`,
        borderRadius: 3,
        p: 2,
        minHeight: 320,
        boxShadow: palette.shadow
      }}
    >
      <Typography
        sx={{
          fontSize: 12,
          fontWeight: 600,
          color: palette.textMuted,
          mb: 1.5,
          textTransform: "uppercase",
          letterSpacing: "0.06em"
        }}
      >
        {title}
      </Typography>
      <Box sx={{ width: "100%", height: 250 }}>
        {children}
      </Box>
    </Box>
  );
}
