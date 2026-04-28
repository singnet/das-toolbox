import { useState } from "react";
import {
  Box,
  Typography,
  Chip,
  IconButton,
} from "@mui/material";
import { styled } from "@mui/material/styles";

import DnsIcon from "@mui/icons-material/Dns";
import VisibilityIcon from "@mui/icons-material/Visibility";

import { mockMachines } from "../../../pages/dashboard/dashboard_mock_data";
import { ServerDetailsDialog } from "./ServerDetailsPanel";

import {
  Container,
  Grid,
  ServerCard,
  MetricsRow,
  Metric,
} from "./architectureview.styled";

export default function ArchitectureView() {
  const [selectedMachine, setSelectedMachine] = useState(null);

  const getStatusColor = (running) =>
    running ? "#22c55e" : "#ef4444";

  return (
    <Container>
      <Typography variant="h5" fontWeight="bold" mb={3}>
        Infrastructure Overview
      </Typography>

      <Grid>
        {mockMachines.map((machine) => (
          <ServerCard key={machine.serverIp}>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
            >
              <Box display="flex" gap={1} alignItems="center">
                <DnsIcon sx={{ color: "#60a5fa" }} />

                <Box>
                  <Typography fontWeight="bold" fontSize={14}>
                    {machine.serverIp}
                  </Typography>

                  <Chip
                    size="small"
                    label={machine.running ? "Online" : "Offline"}
                    sx={{
                      mt: 0.5,
                      background: `${getStatusColor(machine.running)}20`,
                      color: getStatusColor(machine.running),
                    }}
                  />
                </Box>
              </Box>

              <IconButton
                size="small"
                onClick={() => setSelectedMachine(machine)}
                sx={{ color: "#94a3b8" }}
              >
                <VisibilityIcon />
              </IconButton>
            </Box>

            <MetricsRow>
              <Metric>
                <Typography variant="caption">CPU</Typography>
                <Typography fontWeight="bold">
                  {Math.floor(Math.random() * 60)}%
                </Typography>
              </Metric>

              <Metric>
                <Typography variant="caption">RAM</Typography>
                <Typography fontWeight="bold">
                  {(Math.random() * 8).toFixed(1)} GB
                </Typography>
              </Metric>

              <Metric>
                <Typography variant="caption">Services</Typography>
                <Typography fontWeight="bold">
                  {machine.agents.length}
                </Typography>
              </Metric>
            </MetricsRow>
          </ServerCard>
        ))}
      </Grid>

      <ServerDetailsDialog
        machine={selectedMachine}
        open={!!selectedMachine}
        onClose={() => setSelectedMachine(null)}
      />
    </Container>
  );
}