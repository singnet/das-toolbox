import { useEffect, useRef, useState, useCallback } from "react";
import { normalizeService } from "../utils/NormalizeMetrics";
import { createMetricsStream } from "../api/MetricsStreamService";

export function useDashboardMetrics(host) {
  const [machineStats, setMachineStats] = useState(null);
  const [services, setServices] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(Date.now());
  const [isConnected, setIsConnected] = useState(false);
  const [isSwitchingHost, setIsSwitchingHost] = useState(false);
  const [connectionError, setConnectionError] = useState(null);

  const metricsHistoryRef = useRef([]);
  const streamRef = useRef(null);
  const fatalErrorRef = useRef(false);
  const intentionalCloseRef = useRef(false);

  const pushSnapshot = useCallback((servicesData) => {
    metricsHistoryRef.current.push({ data: servicesData });

    if (metricsHistoryRef.current.length > 20) {
      metricsHistoryRef.current.shift();
    }
  }, []);

  useEffect(() => {
    if (!host) return;

    setIsSwitchingHost(true);
    metricsHistoryRef.current = [];
    setServices([]);
    setMachineStats(null);
    fatalErrorRef.current = false;
    intentionalCloseRef.current = false;
    setConnectionError(null);

    if (streamRef.current) {
      intentionalCloseRef.current = true;
      streamRef.current.close();
      streamRef.current = null;
    }

    const stream = createMetricsStream({
      host,
      onData: (incomingData) => {
        const data = Array.isArray(incomingData) ? incomingData[0] : incomingData;
        if (!data) return;

        if (data.type === "error") {
          fatalErrorRef.current = true;
          setIsConnected(false);
          setConnectionError({
            title: "Metrics stream failed",
            description: data.message
          });
          stream.close();
          return;
        }

        if (data.serviceInfo) {
          const parsedServices = Object.values(data.serviceInfo).map(normalizeService);
          setServices(parsedServices);
          pushSnapshot(parsedServices);
        }

        if (data.machineInfo) {
          setMachineStats(data.machineInfo);
        }

        setLastUpdate(Date.now());
      },

      onOpen: () => {
        intentionalCloseRef.current = false;
        setIsConnected(true);
        setIsSwitchingHost(false);
        setConnectionError(null);
      },

      onClose: () => {
        setIsConnected(false);
        metricsHistoryRef.current = [];
        setServices([]);
        setMachineStats(null);
        setConnectionError(null);
        setLastUpdate(Date.now());

        if (intentionalCloseRef.current || fatalErrorRef.current) return;

        setConnectionError({
          title: "Connection closed",
          description: "Metrics stream closed unexpectedly."
        });
      },

      onError: () => {
        setIsConnected(false);
        if (intentionalCloseRef.current || fatalErrorRef.current) return;

        setConnectionError({
          title: "Server connection error",
          description: "Unable to connect to metrics stream."
        });
      }
    });

    streamRef.current = stream;

    return () => {
      intentionalCloseRef.current = true;
      stream.close();
    };
  }, [host, pushSnapshot]);

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

    return { agents: Object.values(servicesMap) };
  }, [lastUpdate]);

  return {
    machineStats,
    services,
    lastUpdate,
    isConnected,
    isSwitchingHost,
    connectionError,
    getAggregatedMetrics
  };
}