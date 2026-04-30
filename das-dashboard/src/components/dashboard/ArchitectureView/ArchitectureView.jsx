import { useMemo, useState } from "react";

import { mockMachines } from "../../../pages/dashboard/dashboard_mock_data";

import {
  Container,
  Grid,
} from "./architectureview.styled";

import { ServiceChart } from "./ServiceChart";
import { ServerCard } from "./ServerCard";

import {
  StyledTab,
  StyledTabs,
} from "../MainContent/servertab/servertab.styled";

import {
  EXPECTED_SERVICES,
  SERVICE_LABELS,
} from "./utils/constants";

export default function ArchitectureView() {
  const [tab, setTab] = useState(0);
  const [selectedService, setSelectedService] =
    useState(null);

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

        const metricEntry =
          machine.metrics.agents.find(
            (m) => m.name === agent.name
          );

        collected.push({
          ...agent,
          displayName:
            SERVICE_LABELS[agent.name] || agent.name,
          type,
          hostServer: machine.serverIp,
          metrics: metricEntry || {
            cpu: [0, 0, 0, 0, 0, 0],
            memory: [0, 0, 0, 0, 0, 0],
          },
          timestamps: machine.metrics.timestamps,
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
              displayName:
                SERVICE_LABELS[name] || name,
              type,
              hostServer: "-",
              status: "Offline",
              health: "No status",
              age: "-",
              memory: "0MB",
              cpu: "0%",
              port: "-",
              image: "-",
              metrics: {
                cpu: [0, 0, 0, 0, 0, 0],
                memory: [0, 0, 0, 0, 0, 0],
              },
              timestamps: [
                "10:00",
                "10:05",
                "10:10",
                "10:15",
                "10:20",
                "10:25",
              ],
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

  const selectedMachine = selectedService
    ? {
        metrics: {
          timestamps: selectedService.timestamps,
          agents: [
            {
              name: selectedService.name,
              cpu: selectedService.metrics.cpu,
              memory: selectedService.metrics.memory,
            },
          ],
        },
      }
    : null;

  return (
    <Container>
      <StyledTabs
        value={tab}
        onChange={(e, value) => {
          setTab(value);
          setSelectedService(null);
        }}
        sx={{ mb: 3 }}
      >
        {tabNames.map((name) => (
          <StyledTab key={name} label={name} />
        ))}
      </StyledTabs>

      <Grid>
        {filteredServices.map((service) => (
          <ServerCard
            key={service.name}
            service={service}
            selectedService={selectedService}
            setSelectedService={setSelectedService}
          />
        ))}
      </Grid>

      {selectedService && (
        <ServiceChart
          selectedMachine={selectedMachine}
          selectedService={selectedService}
        />
      )}
    </Container>
  );
}