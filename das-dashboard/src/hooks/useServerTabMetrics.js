import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { normalizeService } from "../utils/NormalizeMetrics";
import { rollupMetricsHistory } from "../utils/serviceRows";
import { createMetricsStream } from "../api/MetricsStreamService";

export function useServerTabMetrics(host) {
  const [hostMachineStats, setHostMachineStats] = useState(null);
  const [hostServices, setHostServices] = useState([]);
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
    if (snapshotHistoryRef.current.length > 30) snapshotHistoryRef.current.shift();
  }, []);

  useEffect(() => {
    if (!host) {
      setHostStreamSwitching(false);
      setHostStreamConnected(false);
      setHostStreamError(null);
      setHostServices([]);
      setHostMachineStats(null);
      return;
    }

    setHostStreamSwitching(true);
    snapshotHistoryRef.current = [];
    setHostServices([]);
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
          setHostStreamError({ title: "DAS CLI Error", description: payload.message });
          stream.close();
          return;
        }

        if (fatalErrorRef.current) return;

        if (payload.serviceInfo) {
          const runtime = Object.values(payload.serviceInfo).map(normalizeService);
          setHostServices(runtime);
          appendSnapshot(runtime);
        }

        if (payload.machineInfo) setHostMachineStats(payload.machineInfo);
        if (payload.serviceInfo || payload.machineInfo) setHostStreamSwitching(false);
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
        setHostServices([]);
        setHostMachineStats(null);
        setHostStreamTick(Date.now());
        setHostStreamError({
          title: "Connection closed",
          description: event.reason || `Metrics stream closed unexpectedly (Code: ${event.code}).`,
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
    () => rollupMetricsHistory(snapshotHistoryRef.current),
    [hostStreamTick]
  );

  return {
    hostMachineStats,
    hostServices,
    hostStreamTick,
    hostStreamConnected,
    hostStreamSwitching,
    hostStreamError,
    hostMetricsRollup,
  };
}
