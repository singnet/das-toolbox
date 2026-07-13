import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";

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
      .catch((error) => {
        console.error("Failed to load dashboard hosts:", error);
      });

    return () => {
      active = false;
    };
  }, [setDashboardBaseValues]);

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
        setDashboardBaseValues,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}

export const useDashboardContext = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboardContext must be used inside DashboardContextProvider");
  }
  return context;
};
