import { useMemo, useState } from "react";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { Container, Grid } from "./architectureview.styled";
import { ServiceChart } from "./ServiceChart";
import { ServerCard } from "./ServerCard";
import { StyledTab, StyledTabs } from "../MainContent/servertab/servertab.styled";
import { SERVICE_LABELS } from "./utils/constants";
import { formatCpuCell, formatMemoryCell } from "../../../utils/serviceInventory";

const TAB_CATEGORIES = ["Agents", "Brokers", "Loaders", "AtomDB"];
const LOADER_MARKERS = ["metta-loader", "metta-mork-loader"];

function mapServiceType(type) {
  if (type === "broker") return "Brokers";
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
  const {
    allMergedServices,
    aggregatedMetricsByHost,
    servicesByHost,
    allMachinesLastUpdate,
  } = useDashboardContext();
  const [tab, setTab] = useState(0);
  const [selectedServiceId, setSelectedServiceId] = useState(null);

  const processedServices = useMemo(() => {
    const cards = allMergedServices.map((service) => {
      const history =
        aggregatedMetricsByHost[service.serverIp]?.agents?.find(
          (agent) => agent.name === service.container_name
        ) || { cpu: [], memory: [] };

      return buildServiceCard(service, history);
    });

    const seenLoaderIds = new Set(
      cards.filter((card) => card.type === "Loaders").map((card) => card.id)
    );

    Object.entries(servicesByHost).forEach(([serverIp, runtimeServices]) => {
      runtimeServices.forEach((runtime) => {
        const marker = LOADER_MARKERS.find((name) =>
          runtime.container_name?.includes(name)
        );
        if (!marker) {
          return;
        }

        const id = `${serverIp}:${marker}`;
        if (seenLoaderIds.has(id)) {
          return;
        }

        seenLoaderIds.add(id);
        const history =
          aggregatedMetricsByHost[serverIp]?.agents?.find(
            (agent) => agent.name === runtime.container_name
          ) || { cpu: [], memory: [] };

        cards.push({
          id,
          name: runtime.container_name,
          serviceKey: marker,
          displayName: SERVICE_LABELS[marker] || runtime.container_name,
          serverIp,
          type: "Loaders",
          status: runtime.status === "running" ? "Running" : "Offline",
          cpu: formatCpuCell(runtime),
          memory: formatMemoryCell(runtime),
          port: runtime.port ?? "-",
          image: runtime.image ?? "-",
          age: runtime.age ?? "-",
          health:
            runtime.status === "running"
              ? runtime.service_health === "healthy"
                ? "Healthy"
                : runtime.service_health === "-"
                  ? "Running"
                  : "Unhealthy"
              : "No status",
          isPlaceholder: runtime.status !== "running",
          metrics: {
            cpu: history.cpu,
            memory: history.memory,
          },
        });
      });
    });

    return cards;
  }, [allMergedServices, aggregatedMetricsByHost, servicesByHost, allMachinesLastUpdate]);

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
