import { createContext, useContext, useRef, useState, useEffect, useCallback } from "react";
import { normalizeService } from "../../utils/NormalizeMetrics";
import { fetchDashboardDataStream } from "../../api/MetricsAPI";

const DashboardContext = createContext(null);

export default function DashboardContextProvider({ children }) {

    const [machines, setMachines] = useState([]);

    const [machineStats, setMachineStats] = useState(null);

    const [currentMachine, setCurrentMachine] = useState(null);
    const [currentService, setCurrentService] = useState(null);

    const [currentContext, setCurrentContext] = useState("servers");

    const [services, setServices] = useState([]);

    const [lastUpdate, setLastUpdate] = useState(Date.now());

    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState(false);

    const metricsHistoryRef = useRef([]);
    const socketRef = useRef(null);

    const setDashboardBaseValues = useCallback((config) => {

        if (!config) return;

        const foundIps = new Set();
        const machineList = [];

        const findEndpoints = (obj) => {

            if (!obj || typeof obj !== "object") return;

            const rawAddress = obj.endpoint || obj.ip;

            if (rawAddress) {

                const serverIp = String(rawAddress).split(":")[0];

                if (!foundIps.has(serverIp)) {
                    foundIps.add(serverIp);
                    machineList.push({ serverIp, running: true });
                }
            }

            Object.values(obj).forEach((value) => {
                if (typeof value === "object") findEndpoints(value);
            });
        };

        findEndpoints(config);

        setMachines(machineList);

        if (!currentMachine && machineList.length > 0) {
            setCurrentMachine(machineList[0]);
        }

    }, [currentMachine]);

    const pushSnapshot = useCallback((servicesData) => {

        const timestamp = new Date().toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

        metricsHistoryRef.current.push({
            time: timestamp,
            data: servicesData
        });

        if (metricsHistoryRef.current.length > 20) {
            metricsHistoryRef.current.shift();
        }

    }, []);

    useEffect(() => {
        if (!currentMachine?.serverIp) return;

        setIsConnected(false);
        setConnectionError(false);

        metricsHistoryRef.current = [];

        setServices([]);

        if (socketRef.current) {

            socketRef.current.close();

            socketRef.current = null;
        }

        socketRef.current = fetchDashboardDataStream(
            (incomingData) => {

                const data = Array.isArray(incomingData)
                    ? incomingData[0]
                    : incomingData;

                if (!data) return;

                if (data.serviceInfo) {

                    const parsedServices = Object
                        .values(data.serviceInfo)
                        .map(normalizeService);

                    setServices(parsedServices);

                    pushSnapshot(parsedServices);
                }

                if (data.machineInfo) {
                    setMachineStats(data.machineInfo);
                }

                setLastUpdate(Date.now());
            },

            currentMachine.serverIp,

            {
                onOpen: () => {
                    setIsConnected(true);
                    setConnectionError(false);
                },

                onClose: () => {
                    setIsConnected(false);
                    setConnectionError(true);
                },

                onError: () => {
                    setIsConnected(false);
                    setConnectionError(true);
                }
            }
        );

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
                socketRef.current = null;
            }
        };

    }, [currentMachine?.serverIp, pushSnapshot]);

    const getAggregatedMetrics = useCallback(() => {

        const snapshots = metricsHistoryRef.current;
        const servicesMap = {};

        snapshots.forEach((snapshot) => {

            snapshot.data.forEach((service) => {

                const name = service.container_name;

                if (!servicesMap[name]) {
                    servicesMap[name] = {
                        name,
                        cpu: [],
                        memory: []
                    };
                }

                servicesMap[name].cpu.push(service.cpu_percent || 0);
                servicesMap[name].memory.push(service.memory_mb || 0);

            });

        });

        return {
            agents: Object.values(servicesMap),
            timestamps: snapshots.map((snapshot) => snapshot.time)
        };

    }, [lastUpdate]);

    return (
        <DashboardContext.Provider
            value={{
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
                services,
                setServices,
                lastUpdate,
                isConnected,
                setIsConnected,
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
        throw new Error("useDashboardContext must be used inside DashboardContextProvider");
    }

    return context;
};