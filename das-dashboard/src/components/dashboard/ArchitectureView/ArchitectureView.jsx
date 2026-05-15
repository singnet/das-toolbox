import { useMemo, useState } from "react";
import { useDashboardContext } from "../../global_providers/DashboardContextProvider";
import { Container, Grid } from "./architectureview.styled";
import { ServiceChart } from "./ServiceChart";
import { ServerCard } from "./ServerCard";
import { StyledTab, StyledTabs } from "../MainContent/servertab/servertab.styled";
import { EXPECTED_SERVICES, SERVICE_LABELS } from "./utils/constants";

export default function ArchitectureView() {
  const { services, getAggregatedMetrics, lastUpdate } = useDashboardContext();
  const [tab, setTab] = useState(0);
  const [selectedServiceName, setSelectedServiceName] = useState(null);

  const tabNames = ["Agents", "Brokers", "Loaders", "AtomDB"];

  const processedServices = useMemo(() => {
    const finalData = [];
    const aggregated = getAggregatedMetrics();

    Object.entries(EXPECTED_SERVICES).forEach(([category, expectedList]) => {
      expectedList.forEach((baseName) => {
        const realService = services.find((s) => 
            s.container_name === baseName || 
            s.container_name.startsWith(`${baseName}-`)
        );

        if (realService) {
          const history = aggregated.agents.find(a => a.name === realService.container_name) || { cpu: [], memory: [] };

          finalData.push({
            name: realService.container_name,
            displayName: SERVICE_LABELS[baseName] || realService.container_name,
            type: category,
            status: realService.status === "running" ? "Running" : "Offline",
            cpu: `${realService.cpu_percent}%`,
            memory: `${Math.round(realService.memory_mb)}MB`,
            port: realService.port || "-",
            image: realService.image,
            age: realService.age,
            health: realService.service_health === "healthy" ? "Healthy" : 
                    (realService.service_health === "-" ? "Running" : "Unhealthy"),
            isPlaceholder: false,
            metrics: {
              cpu: history.cpu,
              memory: history.memory
            },
            timestamps: aggregated.timestamps
          });
        } else {
          finalData.push({
            name: baseName,
            displayName: SERVICE_LABELS[baseName] || baseName,
            type: category,
            status: "Offline",
            cpu: "0%",
            memory: "0MB",
            port: "-",
            image: "-",
            age: "-",
            health: "No status",
            isPlaceholder: true,
            metrics: { cpu: [], memory: [] },
            timestamps: aggregated.timestamps
          });
        }
      });
    });

    return finalData;
  }, [services, lastUpdate, getAggregatedMetrics]);

  const filteredServices = processedServices.filter(
    (service) => service.type === tabNames[tab]
  );

  const selectedService = processedServices.find(s => s.name === selectedServiceName);

  return (
    <Container>
      <StyledTabs
        value={tab}
        onChange={(e, value) => {
          setTab(value);
          setSelectedServiceName(null);
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
            setSelectedService={(s) => setSelectedServiceName(s?.name || null)}
          />
        ))}
      </Grid>

      {selectedService && (
        <ServiceChart selectedService={selectedService} />
      )}
    </Container>
  );
}