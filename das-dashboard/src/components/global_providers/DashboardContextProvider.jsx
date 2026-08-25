import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";

import { getInitialState } from "../../api/DashboardAPI";

const DashboardContext = createContext(null);

export default function DashboardContextProvider({ children }) {
  const [machines, setMachines] = useState([]);
  const [currentMachine, setCurrentMachine] = useState(null);
  const [currentService, setCurrentService] = useState(null);
  const [currentContext, setCurrentContext] = useState("servers");

  const applyInitialState = useCallback((initialState) => {
    if (!initialState) return;

    const machineList = (initialState.hosts ?? [])
      .map((entry) => {
        if (typeof entry === "string") {
          return { serverIp: entry };
        }
        const ip = entry?.ip || entry?.serverIp;
        return ip ? { serverIp: ip } : null;
      })
      .filter(Boolean);

    setMachines(machineList);
    setCurrentMachine((current) => {
      if (!machineList.length) {
        return null;
      }
      if (!current) {
        return machineList[0];
      }
      return machineList.find((machine) => machine.serverIp === current.serverIp) ?? machineList[0];
    });
  }, []);

  useEffect(() => {
    let active = true;

    getInitialState()
      .then((initialState) => {
        if (active) {
          applyInitialState(initialState);
        }
      })
      .catch((error) => {
        console.error("Failed to load dashboard initial state:", error);
      });

    return () => {
      active = false;
    };
  }, [applyInitialState]);

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
        applyInitialState,
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
