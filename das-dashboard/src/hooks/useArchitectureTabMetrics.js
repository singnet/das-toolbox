import { useEffect, useMemo, useRef, useState } from "react";
import { createMetricsStream } from "../api/MetricsStreamService";
import { normalizeService } from "../utils/NormalizeMetrics";
import { rollupMetricsHistory } from "../utils/serviceRows";

export function useArchitectureTabMetrics(machines = []) {
  const [fleetServicesByHost, setFleetServicesByHost] = useState({});
  const [fleetHostStatsByHost, setFleetHostStatsByHost] = useState({});
  const [fleetLinkUpByHost, setFleetLinkUpByHost] = useState({});
  const [fleetStreamTick, setFleetStreamTick] = useState(Date.now());

  const fleetStreamsRef = useRef({});
  const fleetHistoryRef = useRef({});
  const hostKey = machines.map((machine) => machine.serverIp).filter(Boolean).join(",");

  useEffect(() => {
    const hostList = hostKey ? hostKey.split(",") : [];
    const activeHosts = new Set(hostList);

    Object.entries(fleetStreamsRef.current).forEach(([hostIp, stream]) => {
      if (activeHosts.has(hostIp)) return;
      stream.close();
      delete fleetStreamsRef.current[hostIp];
      delete fleetHistoryRef.current[hostIp];
      setFleetLinkUpByHost((prev) => {
        const next = { ...prev };
        delete next[hostIp];
        return next;
      });
    });

    setFleetServicesByHost((prev) =>
      Object.fromEntries(Object.entries(prev).filter(([hostIp]) => activeHosts.has(hostIp)))
    );

    setFleetHostStatsByHost((prev) =>
      Object.fromEntries(Object.entries(prev).filter(([hostIp]) => activeHosts.has(hostIp)))
    );

    hostList.forEach((hostIp) => {
      if (fleetStreamsRef.current[hostIp]) return;

      fleetHistoryRef.current[hostIp] = [];
      fleetStreamsRef.current[hostIp] = createMetricsStream({
        host: hostIp,
        onOpen: () => setFleetLinkUpByHost((prev) => ({ ...prev, [hostIp]: true })),
        onData: (incomingData) => {
          const payload = Array.isArray(incomingData) ? incomingData[0] : incomingData;
          if (!payload || payload.type === "error") {
            if (payload?.type === "error") {
              setFleetLinkUpByHost((prev) => ({ ...prev, [hostIp]: false }));
            }
            return;
          }

          if (payload.serviceInfo) {
            const runtime = Object.values(payload.serviceInfo).map(normalizeService);
            setFleetServicesByHost((prev) => ({ ...prev, [hostIp]: runtime }));
            fleetHistoryRef.current[hostIp].push({ data: runtime });
            if (fleetHistoryRef.current[hostIp].length > 20) fleetHistoryRef.current[hostIp].shift();
          }

          if (payload.machineInfo) {
            setFleetHostStatsByHost((prev) => ({ ...prev, [hostIp]: payload.machineInfo }));
          }
          setFleetStreamTick(Date.now());
        },
        onClose: () => setFleetLinkUpByHost((prev) => ({ ...prev, [hostIp]: false })),
        onError: () => setFleetLinkUpByHost((prev) => ({ ...prev, [hostIp]: false })),
      });
    });
  }, [hostKey]);

  useEffect(() => () => {
    Object.values(fleetStreamsRef.current).forEach((stream) => stream.close());
    fleetStreamsRef.current = {};
    fleetHistoryRef.current = {};
  }, []);

  const fleetServices = useMemo(
    () =>
      Object.entries(fleetServicesByHost).flatMap(([serverIp, services]) =>
        (services ?? []).map((service) => ({ ...service, serverIp }))
      ),
    [fleetServicesByHost]
  );

  const fleetMetricsByHost = useMemo(() => {
    const result = {};
    Object.entries(fleetHistoryRef.current).forEach(([hostIp, snapshots]) => {
      result[hostIp] = rollupMetricsHistory(snapshots);
    });
    return result;
  }, [fleetStreamTick, fleetServicesByHost]);

  return {
    fleetServices,
    fleetMetricsByHost,
    fleetServicesByHost,
    fleetHostStatsByHost,
    fleetLinkUpByHost,
    fleetStreamTick,
  };
}
