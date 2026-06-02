import {
  createContext,
  useContext,
  useState,
  useCallback
} from "react";

import { useDashboardMetrics } from "../../../src/hooks/UseDashboardMetrics";
const DashboardContext = createContext(null);

export default function DashboardContextProvider({ children }) {
  const [machines, setMachines] = useState([]);
  const [currentMachine, setCurrentMachine] = useState(null);
  const [currentService, setCurrentService] = useState(null);
  const [currentContext, setCurrentContext] = useState("servers");

  const setDashboardBaseValues = useCallback((config) => {
    if (!config) return;

    const foundIps = new Set();
    const machineList = [];

    const findEndpoints = (obj) => {
      if (!obj || typeof obj !== "object") {
        return;
      }

      const rawAddress = obj.endpoint || obj.ip;

      if (rawAddress) {
        const serverIp = String(rawAddress).split(":")[0];

        if (!foundIps.has(serverIp)) {
          foundIps.add(serverIp);
          machineList.push({
            serverIp,
            running: true
          });
        }
      }

      Object.values(obj).forEach((value) => {
        if (typeof value === "object") {
          findEndpoints(value);
        }
      });
    };

    findEndpoints(config);
    
    setMachines(machineList);

    if (machineList.length > 0) {
      setCurrentMachine(machineList[0]);
    } else {
      setCurrentMachine(null);
    }

  }, []);

  const {
    machineStats,
    services,
    lastUpdate,
    isConnected,
    connectionError,
    isSwitchingHost,
    getAggregatedMetrics
  } = useDashboardMetrics(
    currentMachine?.serverIp
  );

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
        lastUpdate,
        isConnected,
        isSwitchingHost,
        connectionError,
        setDashboardBaseValues,
        getAggregatedMetrics
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