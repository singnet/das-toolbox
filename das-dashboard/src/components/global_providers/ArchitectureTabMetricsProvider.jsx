import { createContext, useContext } from "react";
import { useArchitectureTabMetrics } from "../../hooks/useArchitectureTabMetrics";
import { useDashboardContext } from "./DashboardContextProvider";

const ArchitectureTabMetricsContext = createContext(null);

export function ArchitectureTabMetricsProvider({ children }) {
  const { machines, currentContext } = useDashboardContext();
  const isAgentsView = currentContext === "agents";

  const metrics = useArchitectureTabMetrics(isAgentsView ? machines : []);

  return (
    <ArchitectureTabMetricsContext.Provider value={metrics}>
      {children}
    </ArchitectureTabMetricsContext.Provider>
  );
}

export function useArchitectureTabMetricsContext() {
  const context = useContext(ArchitectureTabMetricsContext);
  if (!context) {
    throw new Error(
      "useArchitectureTabMetricsContext must be used inside ArchitectureTabMetricsProvider"
    );
  }
  return context;
}
