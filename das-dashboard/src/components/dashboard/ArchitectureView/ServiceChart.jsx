import { Box, Typography } from "@mui/material";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { CPUViewChart } from "../MainContent/CPUViewChart";
import { MemoryViewChart } from "../MainContent/MemoryViewChart";

export function ServiceChart({ selectedService }) {
  const { getAggregatedMetrics } = useDashboardContext();
  
  const aggregated = getAggregatedMetrics();

  const machine = {
    timestamps: aggregated.timestamps,
    agents: aggregated.agents.filter(a => a.name === selectedService.name)
  };

  if (machine.agents.length === 0) return null;

  return (
    <Box mt={4} key={selectedService.name}>
      <Typography variant="h6" fontWeight="bold" mb={2} color="#64748b">
        Metrics — {selectedService.displayName}
      </Typography>

      <Box
        display="grid"
        gridTemplateColumns={{ xs: "1fr", lg: "1fr 1fr" }}
        gap={3}
      >
        <Box sx={{ background: "#f8fafc", border: "1px solid #e2e8f0", p: 2, minHeight: 320 }}>
          <Typography fontSize={12} fontWeight={700} color="#475569" mb={1.5} textTransform="uppercase">
            CPU Usage In-Time
          </Typography>
          <Box sx={{ width: "100%", height: 250 }}>
            <CPUViewChart machine={machine} />
          </Box>
        </Box>

        <Box sx={{ background: "#f8fafc", border: "1px solid #e2e8f0", p: 2, minHeight: 320 }}>
          <Typography fontSize={12} fontWeight={700} color="#475569" mb={1.5} textTransform="uppercase">
            Memory Usage In-Time
          </Typography>
          <Box sx={{ width: "100%", height: 250 }}>
            <MemoryViewChart machine={machine} />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}