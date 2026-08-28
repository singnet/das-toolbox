import { useMemo, useState } from "react";
import { useArchitectureTabMetricsContext } from "../../global_providers/ArchitectureTabMetricsProvider";
import { Container, Grid } from "./architectureview.styled";
import { ServiceChart } from "./ServiceChart";
import { ServerCard } from "./ServerCard";
import { StyledTab, StyledTabs } from "../MainContent/servertab/servertab.styled";
import { formatCpuCell, formatMemoryCell, isAtomDbService, serviceDisplayName } from "../../../utils/serviceRows";

const TAB_CATEGORIES = ["Agents", "AtomDB"];

function buildServiceCard(service, history = { cpu: [], memory: [] }) {
  const isRunning = service.is_running;
  const rowKey = service.container_name || service.service_command_label;

  return {
    id: `${service.serverIp}:${rowKey}`,
    name: service.container_name,
    serviceKey: service.service_command_label,
    displayName: serviceDisplayName(service),
    serverIp: service.serverIp,
    type: isAtomDbService(service) ? "AtomDB" : "Agents",
    status: isRunning ? "Running" : "Offline",
    cpu: formatCpuCell(service),
    memory: formatMemoryCell(service),
    port: service.port ?? "-",
    image: service.image ?? "-",
    age: service.age ?? "-",
    health:
      !isRunning
        ? "No status"
        : service.service_health === "healthy"
          ? "Healthy"
          : service.service_health === "-"
            ? "Running"
            : "Unhealthy",
    isPlaceholder: !isRunning,
    metrics: {
      cpu: history.cpu,
      memory: history.memory,
    },
  };
}

export default function ArchitectureView() {
  const { fleetServices, fleetMetricsByHost, fleetStreamTick } =
    useArchitectureTabMetricsContext();
  const [tab, setTab] = useState(0);
  const [selectedServiceId, setSelectedServiceId] = useState(null);

  const processedServices = useMemo(() => {
    return fleetServices.map((service) => {
      const history =
        fleetMetricsByHost[service.serverIp]?.agents?.find(
          (agent) => agent.name === service.container_name
        ) || { cpu: [], memory: [] };

      return buildServiceCard(service, history);
    });
  }, [fleetServices, fleetMetricsByHost, fleetStreamTick]);

  const filteredServices = processedServices.filter(
    (service) => service.type === TAB_CATEGORIES[tab]
  );

  const selectedService = processedServices.find((service) => service.id === selectedServiceId);

  return (
    <Container>
      <StyledTabs
        value={tab}
        onChange={(e, value) => {
          setTab(value);
          setSelectedServiceId(null);
        }}
        sx={{ mb: 3 }}
      >
        {TAB_CATEGORIES.map((name) => (
          <StyledTab key={name} label={name} />
        ))}
      </StyledTabs>

      <Grid>
        {filteredServices.map((service) => (
          <ServerCard
            key={service.id}
            service={service}
            selectedService={selectedService}
            setSelectedService={(nextService) =>
              setSelectedServiceId(nextService?.id || null)
            }
          />
        ))}
      </Grid>

      {selectedService && <ServiceChart selectedService={selectedService} />}
    </Container>
  );
}
