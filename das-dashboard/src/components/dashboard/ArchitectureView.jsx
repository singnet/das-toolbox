import { Box, Typography, Chip } from "@mui/material";
import { styled } from "@mui/material/styles";
import CircleIcon from "@mui/icons-material/Circle";

// 🔹 Container geral
const Container = styled(Box)({
  padding: "24px",
});

// 🔹 Grid
const Grid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
  gap: "20px",
});

// 🔹 Card da máquina
const MachineCard = styled(Box)({
  background: "#0f172a",
  border: "1px solid #1e293b",
  borderRadius: "12px",
  padding: "16px",
  color: "#e2e8f0",
  transition: "0.2s",

  "&:hover": {
    borderColor: "#008cff",
    boxShadow: "0 0 0 1px #008cff",
  },
});

// 🔹 Header máquina
const MachineHeader = styled(Box)({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "12px",
});

// 🔹 Agentes container
const AgentsBox = styled(Box)({
  display: "flex",
  flexDirection: "column",
  gap: "8px",
});

// 🔹 Agent item
const AgentItem = styled(Box)({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "8px 10px",
  borderRadius: "8px",
  background: "#1e293b",
});

// 🔹 Status bolinha
const StatusDot = styled(CircleIcon)({
  fontSize: "10px",
});

// 🔹 Mock
const machines = [
  {
    name: "localhost",
    ip: "127.0.0.1",
    running: true,
    agents: [
      { name: "agent-api", running: true },
      { name: "agent-worker", running: true },
      { name: "agent-db", running: false },
    ],
  },
  {
    name: "server-1",
    ip: "192.168.0.1",
    running: true,
    agents: [
      { name: "agent-api", running: true },
      { name: "agent-cache", running: true },
    ],
  },
  {
    name: "server-2",
    ip: "154.188.42.1",
    running: false,
    agents: [
      { name: "agent-worker", running: false },
      { name: "agent-queue", running: false },
    ],
  },
];

export default function ArchitectureView() {
  const getColor = (running) => (running ? "#22c55e" : "#ef4444");

  return (
    <Container>
      <Typography variant="h5" sx={{ mb: 3 }}>
        Architecture Overview
      </Typography>

      <Grid>
        {machines.map((machine) => (
          <MachineCard key={machine.ip}>

            {/* 🔹 Machine header */}
            <MachineHeader>
              <Box>
                <Typography fontWeight="bold">
                  {machine.name}
                </Typography>
                <Typography variant="caption">
                  {machine.ip}
                </Typography>
              </Box>

              <StatusDot sx={{ color: getColor(machine.running) }} />
            </MachineHeader>

            {/* 🔹 Agents */}
            <AgentsBox>
              {machine.agents.map((agent) => (
                <AgentItem key={agent.name}>

                  <Box display="flex" alignItems="center" gap={1}>
                    <StatusDot sx={{ color: getColor(agent.running) }} />
                    <Typography variant="body2">
                      {agent.name}
                    </Typography>
                  </Box>

                  <Chip
                    label={agent.running ? "Running" : "Stopped"}
                    size="small"
                    sx={{
                      background: agent.running
                        ? "rgba(34,197,94,0.15)"
                        : "rgba(239,68,68,0.15)",
                      color: getColor(agent.running),
                    }}
                  />
                </AgentItem>
              ))}
            </AgentsBox>

          </MachineCard>
        ))}
      </Grid>
    </Container>
  );
}