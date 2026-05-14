import { createContext, useContext, useRef, useState, useEffect, useCallback } from "react";
import { normalizeService } from "../../utils/NormalizeMetrics";
import { fetchDashboardDataStream, fetchDashboardDataStatic } from "../../api/DashboardServices";

const DashboardContext = createContext(null);

export default function DashboardContextProvider({ children }) {

    const [machines, setMachines] = useState([]);
    const [machineStats, setMachineStats] = useState(null)
    const [currentMachine, setCurrentMachine] = useState(null);

    const [currentService, setCurrentService] = useState(null);
    const [currentContext, setCurrentContext] = useState("servers");

    const [services, setServices] = useState([]);

    const metricsHistoryRef = useRef([]);

    const socketRef = useRef(null);

    const [lastUpdate, setLastUpdate] = useState(Date.now());

    const setDashboardBaseValues = (config) => {
        if (!config) return;

        const foundIps = new Set();
        const machineList = [];

        const findEndpoints = (obj) => {
            if (!obj || typeof obj !== "object") return;

            const rawAddress = obj.endpoint || obj.ip;

            if (rawAddress) {
            const ipAdress = String(rawAddress).split(":")[0];

            if (!foundIps.has(ipAdress)) {
                foundIps.add(ipAdress);
                machineList.push({
                serverIp: ipAdress,
                running: true,
                });
            }
            }

            Object.values(obj).forEach(value => {
            if (typeof value === "object") {
                findEndpoints(value);
            }
            });
        };

        findEndpoints(config);

        if (machineList.length > 0) {
        setMachines(machineList);
        if (!currentMachine) {
            setCurrentMachine(machineList[0]);
        }
        }
    };

    useEffect(() => {

        if (!currentMachine?.serverIp) return;

        const targetIp = currentMachine.serverIp;

        setServices([]);
        metricsHistoryRef.current = [];

        if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
        }

        socketRef.current = fetchDashboardDataStream((data) => {
            if (!data?.serviceInfo) {
                console.error("Service info not present")
                return;
            }

            if (!data?.machineInfo) {
                console.error("Machine info not present.")
                return;
            }

            const parsed = Object.values(data.serviceInfo).map(normalizeService);

            setMachineStats(data.machineInfo)
            setServices(parsed);
            pushSnapshot(parsed);
            setLastUpdate(Date.now());
            }, targetIp);

            return () => {
            if (socketRef.current) socketRef.current.close();
            };
    }, [currentMachine]);

    function pushSnapshot(servicesData) {
        const timestamp = new Date().toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        metricsHistoryRef.current.push({
            time: timestamp,
            data: servicesData
        });

        if (metricsHistoryRef.current.length > 20) {
            metricsHistoryRef.current.shift();
        }
    }

    const getAggregatedMetrics = useCallback(() => {
    const snapshots = metricsHistoryRef.current;
    const servicesMap = {};

    snapshots.forEach((snap) => {
        snap.data.forEach((s) => {
        const name = s.container_name;
        if (!servicesMap[name]) {
            servicesMap[name] = { name, cpu: [], memory: [] };
        }
        servicesMap[name].cpu.push(s.cpu_percent || 0);
        servicesMap[name].memory.push(s.memory_mb || 0);
        });
    });

    return {
        agents: Object.values(servicesMap),
        timestamps: snapshots.map((snap) => snap.time),
    };
    }, [lastUpdate]);

    return (
        <DashboardContext.Provider value={{
        machines,
        setMachines,
        machineStats,
        setMachineStats,
        currentMachine,
        setCurrentMachine,
        currentService,
        setCurrentService,
        currentContext,
        setCurrentContext,
        setDashboardBaseValues,
        services,
        getAggregatedMetrics,
        lastUpdate
        }}>
        {children}
        </DashboardContext.Provider>
    );
}

export const useDashboardContext = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboardContext must be used inside a DashboardProvider");
  }
  return context;
};