import { createContext, useContext } from "react";
import { useServerTabMetrics } from "../../hooks/useServerTabMetrics";
import { useDashboardContext } from "./DashboardContextProvider";

const ServerTabMetricsContext = createContext(null);

export function ServerTabMetricsProvider({ children }) {
  const { currentMachine, currentContext } = useDashboardContext();
  const isServersView = currentContext === "servers";

  const metrics = useServerTabMetrics(
    isServersView ? currentMachine?.serverIp : null,
    isServersView ? currentMachine?.services ?? [] : []
  );

  return (
    <ServerTabMetricsContext.Provider value={metrics}>
      {children}
    </ServerTabMetricsContext.Provider>
  );
}

export function useServerTabMetricsContext() {
  const context = useContext(ServerTabMetricsContext);
  if (!context) {
    throw new Error("useServerTabMetricsContext must be used inside ServerTabMetricsProvider");
  }
  return context;
}
