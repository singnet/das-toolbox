import { useMemo, useState } from "react";
import { useArchitectureTabMetricsContext } from "../../global_providers/ArchitectureTabMetricsProvider";
import { Container, Grid } from "./architectureview.styled";
import { ServiceChart } from "./ServiceChart";
import { ServerCard } from "./ServerCard";
import { StyledTab, StyledTabs } from "../MainContent/servertab/servertab.styled";
import { formatCpuCell, formatMemoryCell } from "../../../utils/serviceInventory";

const TAB_CATEGORIES = ["Agents", "AtomDB"];

function mapServiceType(type) {
  if (type === "atomdb") return "AtomDB";
  return "Agents";
}

function buildServiceCard(service, history = { cpu: [], memory: [] }) {
  const isRunning = service.is_running;

  return {
    id: `${service.serverIp}:${service.service_key}`,
    name: service.container_name,
    serviceKey: service.service_key,
    displayName: service.display_name,
    serverIp: service.serverIp,
    type: mapServiceType(service.type),
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
  const { fleetMergedServices, fleetMetricsByHost, fleetStreamTick } =
    useArchitectureTabMetricsContext();
  const [tab, setTab] = useState(0);
  const [selectedServiceId, setSelectedServiceId] = useState(null);

  const processedServices = useMemo(() => {
    return fleetMergedServices.map((service) => {
      const history =
        fleetMetricsByHost[service.serverIp]?.agents?.find(
          (agent) => agent.name === service.container_name
        ) || { cpu: [], memory: [] };

      return buildServiceCard(service, history);
    });
  }, [fleetMergedServices, fleetMetricsByHost, fleetStreamTick]);

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
