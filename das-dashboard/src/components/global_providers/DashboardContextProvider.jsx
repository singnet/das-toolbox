import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";

import { useDashboardMetrics } from "../../hooks/UseDashboardMetrics";
import { useAllMachinesMetrics } from "../../hooks/UseAllMachinesMetrics";
import { getConfigHosts } from "../../api/ConfigAPI";
import { hostsToMachines } from "../../utils/serviceInventory";

const DashboardContext = createContext(null);

export default function DashboardContextProvider({ children }) {
  const [machines, setMachines] = useState([]);
  const [currentMachine, setCurrentMachine] = useState(null);
  const [currentService, setCurrentService] = useState(null);
  const [currentContext, setCurrentContext] = useState("servers");

  const setDashboardBaseValues = useCallback((hosts) => {
    if (!Array.isArray(hosts)) {
      return;
    }

    const machineList = hostsToMachines(hosts);
    setMachines(machineList);
    setCurrentMachine(machineList[0] ?? null);
  }, []);

  useEffect(() => {
    let active = true;

    getConfigHosts()
      .then(({ hosts }) => {
        if (active) {
          setDashboardBaseValues(hosts ?? []);
        }
      })
      .catch(() => {});

    return () => {
      active = false;
    };
  }, [setDashboardBaseValues]);

  const {
    machineStats,
    services,
    mergedServices,
    lastUpdate,
    isConnected,
    connectionError,
    isSwitchingHost,
    aggregatedMetrics,
  } = useDashboardMetrics(
    currentMachine?.serverIp,
    currentMachine?.expectedServices ?? []
  );

  const {
    allMergedServices,
    aggregatedMetricsByHost,
    servicesByHost,
    machineStatsByHost,
    lastUpdate: allMachinesLastUpdate,
  } = useAllMachinesMetrics(machines);

  return (
    <DashboardContext.Provider
      value={{
        machines,
        setMachines,
        currentMachine,
        setCurrentMachine,
        currentService,
        setCurrentService,
        currentContext,
        setCurrentContext,
        machineStats,
        services,
        mergedServices,
        lastUpdate,
        isConnected,
        isSwitchingHost,
        connectionError,
        setDashboardBaseValues,
        aggregatedMetrics,
        allMergedServices,
        aggregatedMetricsByHost,
        servicesByHost,
        machineStatsByHost,
        allMachinesLastUpdate,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}

export const useDashboardContext = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error(
      "useDashboardContext must be used inside DashboardContextProvider"
    );
  }
  return context;
};
