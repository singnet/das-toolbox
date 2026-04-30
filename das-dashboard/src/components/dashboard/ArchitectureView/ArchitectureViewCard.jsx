import { useMemo, useState } from "react";
import {
  Box,
  Typography,
  Chip,
  Tabs,
  Tab,
} from "@mui/material";
import StorageIcon from "@mui/icons-material/Storage";

import { mockMachines } from "../../../pages/dashboard/dashboard_mock_data";

import {
  Container,
  Grid,
  ServerCard,
} from "./architectureview.styled";

import { InlineInfo } from "./InlineInfo";
import { MetricBar } from "./MetricBar";

const EXPECTED_SERVICES = {
  Agents: [
    "das-query-engine-40002",
    "das-link-creation-agent-40007",
    "das-inference-agent-40008",
    "das-evolution-agent-40009",
  ],
  Brokers: [
    "das-attention-broker-40001",
    "das-context-broker-40004",
    "das-atomdb-broker-40010",
  ],
  Loaders: [
    "metta-loader",
    "metta-mork-loader",
  ],
  AtomDB: [
    "das-cli-mongodb-40020",
    "das-cli-redis-40021",
    "das-morkdb-40022",
  ],
};

export default function ArchitectureView() {
  const [tab, setTab] = useState(0);

  const tabNames = [
    "Agents",
    "Brokers",
    "Loaders",
    "AtomDB",
  ];

  const services = useMemo(() => {
    const collected = [];

    mockMachines.forEach((machine) => {
      machine.agents.forEach((agent) => {
        let type = "Agents";

        if (
          agent.name.includes("mongodb") ||
          agent.name.includes("redis") ||
          agent.name.includes("mork")
        ) {
          type = "AtomDB";
        } else if (agent.name.includes("broker")) {
          type = "Brokers";
        } else if (agent.name.includes("loader")) {
          type = "Loaders";
        }

        collected.push({
          ...agent,
          type,
          hostServer: machine.serverIp,
        });
      });
    });

    const existingNames = collected.map(
      (service) => service.name
    );

    Object.entries(EXPECTED_SERVICES).forEach(
      ([type, names]) => {
        names.forEach((name) => {
          if (!existingNames.includes(name)) {
            collected.push({
              name,
              type,
              hostServer: "-",
              status: "Offline",
              health: "No status",
              age: "-",
              memory: "0MB",
              cpu: "0%",
              port: "-",
              image: "-",
            });
          }
        });
      }
    );

    return collected;
  }, []);

  const filteredServices = services.filter(
    (service) => service.type === tabNames[tab]
  );

  const getStatusColor = (status) =>
    status === "Running" ? "#22c55e" : "#ef4444";

  const getHealthColor = (health) => {
    switch (health) {
      case "Healthy":
        return "#22c55e";
      case "Degraded":
        return "#f59e0b";
      case "Critical":
        return "#ef4444";
      default:
        return "#ffffff";
    }
  };

  const parsePercent = (value) =>
    Number(String(value).replace("%", "")) || 0;

  const parseMemory = (value) => {
    const numeric =
      Number(String(value).replace(/[^\d.]/g, "")) || 0;

    return Math.min((numeric / 2500) * 100, 100);
  };

  return (
    <Container>
      <Tabs
        value={tab}
        onChange={(e, value) => setTab(value)}
        sx={{ mb: 3 }}
      >
        {tabNames.map((name) => (
          <Tab key={name} label={name} />
        ))}
      </Tabs>

      <Grid>
        {filteredServices.map((service) => (
          <ServerCard key={service.name}>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="flex-start"
              mb={2}
            >
              <Box display="flex" gap={1.5} alignItems="center">
                <StorageIcon sx={{ color: "#60a5fa" }} />

                <Box>
                  <Typography
                    fontWeight="bold"
                    fontSize={14}
                  >
                    {service.name}
                  </Typography>

                  <Typography
                    variant="caption"
                    color="#94a3b8"
                  >
                    Host: {service.hostServer}
                  </Typography>
                </Box>
              </Box>

              <Chip
                size="small"
                label={service.status}
                sx={{
                  background: `${getStatusColor(
                    service.status
                  )}20`,
                  color: getStatusColor(service.status),
                  fontWeight: 600,
                }}
              />
            </Box>

            <MetricBar
              label="CPU"
              value={service.cpu}
              progress={parsePercent(service.cpu)}
            />

            <MetricBar
              label="Memory"
              value={service.memory}
              progress={parseMemory(service.memory)}
            />

            <Box display="grid" gap={0.75} mt={2}>
              <InlineInfo
                label="Port"
                value={service.port}
              />

              <InlineInfo
                label="Image"
                value={service.image}
              />

              <InlineInfo
                label="Uptime"
                value={service.age}
              />

              <InlineInfo
                label="Service Health"
                value={service.health}
                valueColor={getHealthColor(
                  service.health
                )}
              />
            </Box>
          </ServerCard>
        ))}
      </Grid>
    </Container>
  );
}