import { useEffect, useRef, useState, useCallback } from "react";
import { normalizeService } from "../utils/NormalizeMetrics";
import { createMetricsStream } from "../api/MetricsStreamService";

export function useDashboardMetrics(host) {
  const [machineStats, setMachineStats] = useState(null);
  const [services, setServices] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(Date.now());
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);

  const metricsHistoryRef = useRef([]);
  const streamRef = useRef(null);
  const fatalErrorRef = useRef(false);

  const pushSnapshot = useCallback((servicesData) => {
    const timestamp = new Date().toLocaleTimeString("pt-BR", {
      hour: "2-digit", minute: "2-digit", second: "2-digit"
    });

    metricsHistoryRef.current.push({ time: timestamp, data: servicesData });

    if (metricsHistoryRef.current.length > 20) {
      metricsHistoryRef.current.shift();
    }
  }, []);

  useEffect(() => {
  if (!host) {
    return;
  }

  console.log("Opening metrics stream for:", host);

  fatalErrorRef.current = false;

  setIsConnected(false);
  setConnectionError(null);

  if (streamRef.current) {
    streamRef.current.close();
    streamRef.current = null;
  }

  const stream = createMetricsStream({
    host,

    onData: (incomingData) => {
      console.log("WS DATA:", incomingData);

      const data = Array.isArray(incomingData)
        ? incomingData[0]
        : incomingData;

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
        const parsedServices =
          Object.values(data.serviceInfo).map(normalizeService);

        setServices(parsedServices);

        pushSnapshot(parsedServices);
      }

      if (data.machineInfo) {
        setMachineStats(data.machineInfo);
      }

      setLastUpdate(Date.now());
    },

    onOpen: () => {
      console.log("WS OPEN");

      if (fatalErrorRef.current) return;

      setIsConnected(true);
      setConnectionError(null);
    },

    onClose: () => {
      console.log("WS CLOSED");

      setIsConnected(false);

      if (fatalErrorRef.current) return;

      setConnectionError({
        title: "Connection closed.",
        description:
          "Metrics stream closed unexpectedly."
      });
    },

    onError: (err) => {
      console.error("WS ERROR:", err);

      setIsConnected(false);

      if (fatalErrorRef.current) return;

      setConnectionError({
        title: "Server connection error.",
        description:
          "Unable to connect to metrics stream."
      });
    }
  });

  streamRef.current = stream;

  return () => {
    console.log("Cleaning WS:", host);

    stream.close();
  };

}, [host]);

  const getAggregatedMetrics = useCallback(() => {
    const snapshots = metricsHistoryRef.current;
    const servicesMap = {};

    snapshots.forEach((snapshot) => {
      snapshot.data.forEach((service) => {
        const name = service.container_name;

        if (!servicesMap[name]) {
          servicesMap[name] = { name, cpu: [], memory: [] };
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

  return {
    machineStats,
    services,
    lastUpdate,
    isConnected,
    connectionError,
    getAggregatedMetrics
  };
}