import { useEffect, useMemo, useRef, useState } from "react";
import { createMetricsStream } from "../api/MetricsStreamService";
import { normalizeService } from "../utils/NormalizeMetrics";
import { mergeHostServices } from "../utils/serviceInventory";

function rollupFleetHistory(snapshots = []) {
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

export function useArchitectureTabMetrics(machines = []) {
  const [fleetRuntimeByHost, setFleetRuntimeByHost] = useState({});
  const [fleetHostStatsByHost, setFleetHostStatsByHost] = useState({});
  const [fleetLinkUpByHost, setFleetLinkUpByHost] = useState({});
  const [fleetStreamTick, setFleetStreamTick] = useState(Date.now());

  const fleetStreamsRef = useRef({});
  const fleetHistoryRef = useRef({});

  useEffect(() => {
    const hostList = machines.map((machine) => machine.serverIp).filter(Boolean);
    const activeHosts = new Set(hostList);

    Object.entries(fleetStreamsRef.current).forEach(([hostIp, stream]) => {
      if (!activeHosts.has(hostIp)) {
        stream.close();
        delete fleetStreamsRef.current[hostIp];
        delete fleetHistoryRef.current[hostIp];
        setFleetLinkUpByHost((prev) => {
          const next = { ...prev };
          delete next[hostIp];
          return next;
        });
      }
    });

    setFleetRuntimeByHost((prev) =>
      Object.fromEntries(Object.entries(prev).filter(([hostIp]) => activeHosts.has(hostIp)))
    );

    hostList.forEach((hostIp) => {
      if (fleetStreamsRef.current[hostIp]) {
        return;
      }

      fleetHistoryRef.current[hostIp] = [];

      const stream = createMetricsStream({
        host: hostIp,
        onOpen: () => {
          setFleetLinkUpByHost((prev) => ({ ...prev, [hostIp]: true }));
        },
        onData: (incomingData) => {
          const payload = Array.isArray(incomingData) ? incomingData[0] : incomingData;
          if (!payload || payload.type === "error") {
            if (payload?.type === "error") {
              setFleetLinkUpByHost((prev) => ({ ...prev, [hostIp]: false }));
            }
            return;
          }

          if (payload.serviceInfo) {
            const parsed = Object.values(payload.serviceInfo).map(normalizeService);
            setFleetRuntimeByHost((prev) => ({ ...prev, [hostIp]: parsed }));

            fleetHistoryRef.current[hostIp].push({ data: parsed });
            if (fleetHistoryRef.current[hostIp].length > 20) {
              fleetHistoryRef.current[hostIp].shift();
            }
          }

          if (payload.machineInfo) {
            setFleetHostStatsByHost((prev) => ({ ...prev, [hostIp]: payload.machineInfo }));
          }

          setFleetStreamTick(Date.now());
        },
        onClose: () => {
          setFleetLinkUpByHost((prev) => ({ ...prev, [hostIp]: false }));
        },
        onError: () => {
          setFleetLinkUpByHost((prev) => ({ ...prev, [hostIp]: false }));
        },
      });

      fleetStreamsRef.current[hostIp] = stream;
    });
  }, [machines]);

  useEffect(() => {
    return () => {
      Object.values(fleetStreamsRef.current).forEach((stream) => stream.close());
      fleetStreamsRef.current = {};
      fleetHistoryRef.current = {};
    };
  }, []);

  const fleetMergedServices = useMemo(
    () =>
      machines.flatMap((machine) => {
        const runtime = fleetRuntimeByHost[machine.serverIp] || [];
        return mergeHostServices(machine.expectedServices ?? [], runtime).map((service) => ({
          ...service,
          serverIp: machine.serverIp,
        }));
      }),
    [machines, fleetRuntimeByHost]
  );

  const fleetMetricsByHost = useMemo(() => {
    const result = {};
    Object.entries(fleetHistoryRef.current).forEach(([hostIp, snapshots]) => {
      result[hostIp] = rollupFleetHistory(snapshots);
    });
    return result;
  }, [fleetStreamTick, fleetRuntimeByHost]);

  return {
    fleetMergedServices,
    fleetMetricsByHost,
    fleetRuntimeByHost,
    fleetHostStatsByHost,
    fleetLinkUpByHost,
    fleetStreamTick,
  };
}
