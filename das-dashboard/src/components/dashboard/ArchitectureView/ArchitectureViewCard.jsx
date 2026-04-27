import {
  Box,
  Typography,
  Chip,
  Divider,
} from "@mui/material";
import { styled } from "@mui/material/styles";

import DnsIcon from "@mui/icons-material/Dns";
import MemoryIcon from "@mui/icons-material/Memory";
import SettingsEthernetIcon from "@mui/icons-material/SettingsEthernet";
import CircleIcon from "@mui/icons-material/Circle";

import { mockMachines } from "../../../pages/dashboard/dashboard_mock_data";

const Container = styled(Box)({
  padding: "24px",
});

const Grid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(480px, 1fr))",
  gap: "24px",
});

const ServerCard = styled(Box)({
  background: "#0f172a",
  border: "1px solid #1e293b",
  borderRadius: "16px",
  padding: "20px",
  color: "#e2e8f0",
  transition: "0.2s",

  "&:hover": {
    borderColor: "#3b82f6",
    boxShadow: "0 0 0 1px #3b82f6",
  },
});

const Header = styled(Box)({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "16px",
});

const MetricsRow = styled(Box)({
  display: "flex",
  gap: "16px",
  marginBottom: "16px",
});

const MetricBox = styled(Box)({
  flex: 1,
  padding: "12px",
  background: "#1e293b",
  borderRadius: "10px",
  textAlign: "center",
});

const AgentList = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: "12px",
});

const AgentCard = styled(Box)({
  background: "#1e293b",
  borderRadius: "12px",
  padding: "14px",
});

const Row = styled(Box)({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
});

const StatusDot = styled(CircleIcon)({
  fontSize: 10,
});

export default function ArchitectureView() {
  const getColor = (running) =>
    running ? "#22c55e" : "#ef4444";

  return (
    <Container>
      <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>
        Infrastructure Overview
      </Typography>

      <Grid>
        {mockMachines.map((machine) => (
          <ServerCard key={machine.serverIp}>
            <Header>
              <Box display="flex" alignItems="center" gap={1.5}>
                <DnsIcon sx={{ color: "#60a5fa" }} />

                <Box>
                  <Typography fontWeight="bold">
                    {machine.serverIp}
                  </Typography>

                  <Typography variant="caption" color="#94a3b8">
                    {machine.agents.length} deployed services
                  </Typography>
                </Box>
              </Box>

              <Chip
                icon={
                  <StatusDot
                    sx={{ color: getColor(machine.running) }}
                  />
                }
                label={machine.running ? "Online" : "Offline"}
                size="small"
                sx={{
                  background: machine.running
                    ? "rgba(34,197,94,0.15)"
                    : "rgba(239,68,68,0.15)",
                  color: getColor(machine.running),
                }}
              />
            </Header>

            <MetricsRow>
              <MetricBox>
                <Typography variant="caption" color="#94a3b8">
                  CPU AVG
                </Typography>
                <Typography fontWeight="bold">
                  {Math.floor(Math.random() * 60)}%
                </Typography>
              </MetricBox>

              <MetricBox>
                <Typography variant="caption" color="#94a3b8">
                  RAM AVG
                </Typography>
                <Typography fontWeight="bold">
                  {(Math.random() * 8).toFixed(1)} GB
                </Typography>
              </MetricBox>

              <MetricBox>
                <Typography variant="caption" color="#94a3b8">
                  SERVICES
                </Typography>
                <Typography fontWeight="bold">
                  {machine.agents.length}
                </Typography>
              </MetricBox>
            </MetricsRow>

            <Divider sx={{ borderColor: "#334155", mb: 2 }} />

            <AgentList>
              {machine.agents.map((agent) => (
                <AgentCard key={agent.name}>
                  <Row>
                    <Typography fontWeight="600">
                      {agent.name}
                    </Typography>

                    <Chip
                      size="small"
                      label={agent.status}
                      sx={{
                        background:
                          agent.status === "Running"
                            ? "rgba(34,197,94,0.15)"
                            : "rgba(239,68,68,0.15)",
                        color:
                          agent.status === "Running"
                            ? "#22c55e"
                            : "#ef4444",
                      }}
                    />
                  </Row>

                  <Row mt={1}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <SettingsEthernetIcon sx={{ fontSize: 16 }} />
                      <Typography variant="caption">
                        Port {agent.port}
                      </Typography>
                    </Box>

                    <Typography variant="caption">
                      Age: {agent.age}
                    </Typography>
                  </Row>

                  <Row mt={1}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <MemoryIcon sx={{ fontSize: 16 }} />
                      <Typography variant="caption">
                        RAM: {agent.memory}
                      </Typography>
                    </Box>

                    <Typography variant="caption">
                      CPU: {agent.cpu}
                    </Typography>
                  </Row>
                </AgentCard>
              ))}
            </AgentList>
          </ServerCard>
        ))}
      </Grid>
    </Container>
  );
}