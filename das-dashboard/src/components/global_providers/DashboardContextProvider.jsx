import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useRef
} from "react";

import { useDashboardMetrics } from "../../../src/hooks/UseDashboardMetrics";
import { fetchDashboardDataStatic } from "../../api/MetricsAPI";

const DashboardContext = createContext(null);

export default function DashboardContextProvider({ children }) {
  const [machines, setMachines] = useState([]);
  const [currentMachine, setCurrentMachine] = useState(null);
  const [currentService, setCurrentService] = useState(null);
  const [currentContext, setCurrentContext] = useState("servers");
  
  const [globalServicesState, setGlobalServicesState] = useState({
    atomDbOnline: false,
    architectureOnline: false
  });

  const isMutatingRef = useRef(false);
  const mutationTimeoutRef = useRef(null);

  const forceGlobalStateUpdate = useCallback((newState) => {
    if (mutationTimeoutRef.current) clearTimeout(mutationTimeoutRef.current);
    
    // Ativa a trava
    isMutatingRef.current = true;
    
    setGlobalServicesState(prev => ({
      ...prev,
      ...newState
    }));

    mutationTimeoutRef.current = setTimeout(() => {
      isMutatingRef.current = false;
    }, 3000);
  }, []);

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

  useEffect(() => {
    if (machines.length === 0) return;

    const checkGlobalArchitectureStatus = async () => {
      let isAtomDbOnlineGlobal = false;
      let isArchitectureOnlineGlobal = false;

      const promises = machines.map(async (machine) => {
        try {
          const response = await fetchDashboardDataStatic("all", machine.serverIp);
          const rawServiceInfo = response?.content?.serviceInfo || [];
          
          const serviceList = Array.isArray(rawServiceInfo) 
            ? rawServiceInfo 
            : Object.values(rawServiceInfo);

          const hasAtomDb = serviceList.some(s =>
            (s.container_name?.includes("mongodb") || s.container_name?.includes("redis") || s.container_name?.includes("morkdb")) &&
            s.status === "running"
          );

          const hasArchitecture = serviceList.some(s =>
            (s.container_name?.includes("agent") || s.container_name?.includes("broker")) &&
            s.status === "running"
          );

          if (hasAtomDb) isAtomDbOnlineGlobal = true;
          if (hasArchitecture) isArchitectureOnlineGlobal = true;
        } catch (error) {
          console.error(`Error fetching static metrics for global check on ${machine.serverIp}:`, error);
        }
      });

      await Promise.all(promises);

      if (!isMutatingRef.current) {
        setGlobalServicesState({
          atomDbOnline: isAtomDbOnlineGlobal,
          architectureOnline: isArchitectureOnlineGlobal
        });
      }
    };

    checkGlobalArchitectureStatus();
  }, [machines]);

  const {
    machineStats,
    services,
    lastUpdate,
    isConnected,
    connectionError,
    isSwitchingHost,
    aggregatedMetrics
  } = useDashboardMetrics(
    currentMachine?.serverIp
  );

  useEffect(() => {
    if (!services || services.length === 0 || isMutatingRef.current) return;

    const hasLocalAtomDb = services.some(s =>
      (s.container_name?.includes("mongodb") || s.container_name?.includes("redis") || s.container_name?.includes("morkdb")) &&
      s.status === "running"
    );

    const hasLocalArchitecture = services.some(s =>
      (s.container_name?.includes("agent") || s.container_name?.includes("broker")) &&
      s.status === "running"
    );

    setGlobalServicesState(prev => ({
      atomDbOnline: prev.atomDbOnline || hasLocalAtomDb,
      architectureOnline: prev.architectureOnline || hasLocalArchitecture
    }));
  }, [services]);

  useEffect(() => {
    return () => {
      if (mutationTimeoutRef.current) clearTimeout(mutationTimeoutRef.current);
    };
  }, []);

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
        aggregatedMetrics,
        globalServicesState,
        setGlobalServicesState,
        forceGlobalStateUpdate,
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