import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { normalizeService } from "../utils/NormalizeMetrics";
import { mergeHostServices } from "../utils/serviceInventory";
import { createMetricsStream } from "../api/MetricsStreamService";

function rollupServiceHistory(snapshots = []) {
  const byContainer = {};

  snapshots.forEach((snapshot) => {
    snapshot.data.forEach((service) => {
      const name = service.container_name;
      if (!byContainer[name]) {
        byContainer[name] = { name, cpu: [], memory: [] };
      }
      byContainer[name].cpu.push(service.cpu_percent || 0);
      byContainer[name].memory.push(service.memory_mb || 0);
    });
  });

  return { agents: Object.values(byContainer) };
}

export function useServerTabMetrics(host, expectedServices = []) {
  const [hostMachineStats, setHostMachineStats] = useState(null);
  const [hostRuntimeServices, setHostRuntimeServices] = useState([]);
  const [hostStreamTick, setHostStreamTick] = useState(Date.now());
  const [hostStreamConnected, setHostStreamConnected] = useState(false);
  const [hostStreamSwitching, setHostStreamSwitching] = useState(false);
  const [hostStreamError, setHostStreamError] = useState(null);

  const snapshotHistoryRef = useRef([]);
  const streamRef = useRef(null);
  const fatalErrorRef = useRef(false);
  const intentionalCloseRef = useRef(false);

  const appendSnapshot = useCallback((servicesData) => {
    snapshotHistoryRef.current.push({ data: servicesData });
    if (snapshotHistoryRef.current.length > 20) {
      snapshotHistoryRef.current.shift();
    }
  }, []);

  useEffect(() => {
    if (!host) {
      setHostStreamSwitching(false);
      setHostStreamConnected(false);
      setHostStreamError(null);
      setHostRuntimeServices([]);
      setHostMachineStats(null);
      return;
    }

    setHostStreamSwitching(true);
    snapshotHistoryRef.current = [];
    setHostRuntimeServices([]);
    setHostMachineStats(null);
    setHostStreamTick(Date.now());

    fatalErrorRef.current = false;
    intentionalCloseRef.current = false;
    setHostStreamError(null);

    if (streamRef.current) {
      intentionalCloseRef.current = true;
      streamRef.current.close();
      streamRef.current = null;
    }

    const stream = createMetricsStream({
      host,
      onData: (incomingData) => {
        const payload = Array.isArray(incomingData) ? incomingData[0] : incomingData;
        if (!payload) return;

        if (payload.type === "error") {
          fatalErrorRef.current = true;
          setHostStreamConnected(false);
          setHostStreamSwitching(false);
          setHostStreamError({
            title: "DAS CLI Error",
            description: payload.message,
          });
          stream.close();
          return;
        }

        if (fatalErrorRef.current) return;

        if (payload.serviceInfo) {
          const parsed = Object.values(payload.serviceInfo).map(normalizeService);
          setHostRuntimeServices(parsed);
          appendSnapshot(parsed);
        }

        if (payload.machineInfo) {
          setHostMachineStats(payload.machineInfo);
        }

        if (payload.serviceInfo || payload.machineInfo) {
          setHostStreamSwitching(false);
        }

        setHostStreamTick(Date.now());
      },
      onOpen: () => {
        intentionalCloseRef.current = false;
        setHostStreamConnected(true);
        setHostStreamError(null);
      },
      onClose: (event) => {
        setHostStreamSwitching(false);
        if (intentionalCloseRef.current || fatalErrorRef.current) {
          setHostStreamConnected(false);
          return;
        }

        setHostStreamConnected(false);
        snapshotHistoryRef.current = [];
        setHostRuntimeServices([]);
        setHostMachineStats(null);
        setHostStreamTick(Date.now());
        setHostStreamError({
          title: "Connection closed",
          description:
            event.reason ||
            `Metrics stream closed unexpectedly (Code: ${event.code}). Try refreshing the page and retry the connection.`,
        });
      },
      onError: (err) => {
        setHostStreamSwitching(false);
        if (intentionalCloseRef.current || fatalErrorRef.current) return;

        setHostStreamConnected(false);
        setHostStreamError({
          title: "Server connection error",
          description: err.message || "Unable to connect to metrics stream.",
        });
      },
    });

    streamRef.current = stream;

    return () => {
      intentionalCloseRef.current = true;
      stream.close();
    };
  }, [host, appendSnapshot]);

  const hostMetricsRollup = useMemo(
    () => rollupServiceHistory(snapshotHistoryRef.current),
    [hostStreamTick]
  );

  const hostMergedServices = useMemo(
    () => mergeHostServices(expectedServices, hostRuntimeServices),
    [expectedServices, hostRuntimeServices]
  );

  return {
    hostMachineStats,
    hostRuntimeServices,
    hostMergedServices,
    hostStreamTick,
    hostStreamConnected,
    hostStreamSwitching,
    hostStreamError,
    hostMetricsRollup,
  };
}
