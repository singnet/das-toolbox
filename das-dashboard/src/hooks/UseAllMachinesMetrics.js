import { useEffect, useMemo, useRef, useState } from "react";
import { createMetricsStream } from "../api/MetricsStreamService";
import { normalizeService } from "../utils/NormalizeMetrics";
import { mergeHostServices } from "../utils/serviceInventory";

function buildAggregatedMetrics(snapshots = []) {
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

  return { agents: Object.values(servicesMap) };
}

export function useAllMachinesMetrics(machines = []) {
  const [servicesByHost, setServicesByHost] = useState({});
  const [machineStatsByHost, setMachineStatsByHost] = useState({});
  const [connectionByHost, setConnectionByHost] = useState({});
  const [lastUpdate, setLastUpdate] = useState(Date.now());
  const streamsRef = useRef({});
  const historyRef = useRef({});

  useEffect(() => {
    const hosts = machines.map((machine) => machine.serverIp).filter(Boolean);
    const activeHosts = new Set(hosts);

    Object.entries(streamsRef.current).forEach(([host, stream]) => {
      if (!activeHosts.has(host)) {
        stream.close();
        delete streamsRef.current[host];
        delete historyRef.current[host];
        setConnectionByHost((prev) => {
          const next = { ...prev };
          delete next[host];
          return next;
        });
      }
    });

    setServicesByHost((prev) =>
      Object.fromEntries(
        Object.entries(prev).filter(([host]) => activeHosts.has(host))
      )
    );

    hosts.forEach((host) => {
      if (streamsRef.current[host]) {
        return;
      }

      historyRef.current[host] = [];

      const stream = createMetricsStream({
        host,
        onOpen: () => {
          setConnectionByHost((prev) => ({ ...prev, [host]: true }));
        },
        onData: (incomingData) => {
          const data = Array.isArray(incomingData) ? incomingData[0] : incomingData;
          if (!data || data.type === "error") {
            if (data?.type === "error") {
              setConnectionByHost((prev) => ({ ...prev, [host]: false }));
            }
            return;
          }

          if (data.serviceInfo) {
            const parsedServices = Object.values(data.serviceInfo).map(normalizeService);
            setServicesByHost((prev) => ({ ...prev, [host]: parsedServices }));

            historyRef.current[host].push({ data: parsedServices });
            if (historyRef.current[host].length > 20) {
              historyRef.current[host].shift();
            }
          }

          if (data.machineInfo) {
            setMachineStatsByHost((prev) => ({ ...prev, [host]: data.machineInfo }));
          }

          setLastUpdate(Date.now());
        },
        onClose: () => {
          setConnectionByHost((prev) => ({ ...prev, [host]: false }));
        },
        onError: () => {
          setConnectionByHost((prev) => ({ ...prev, [host]: false }));
        },
      });

      streamsRef.current[host] = stream;
    });
  }, [machines]);

  useEffect(() => {
    return () => {
      Object.values(streamsRef.current).forEach((stream) => stream.close());
      streamsRef.current = {};
      historyRef.current = {};
    };
  }, []);

  const allMergedServices = useMemo(
    () =>
      machines.flatMap((machine) => {
        const runtime = servicesByHost[machine.serverIp] || [];
        return mergeHostServices(machine.expectedServices ?? [], runtime).map((service) => ({
          ...service,
          serverIp: machine.serverIp,
        }));
      }),
    [machines, servicesByHost]
  );

  const aggregatedMetricsByHost = useMemo(() => {
    const result = {};

    Object.entries(historyRef.current).forEach(([host, snapshots]) => {
      result[host] = buildAggregatedMetrics(snapshots);
    });

    return result;
  }, [lastUpdate, servicesByHost]);

  return {
    allMergedServices,
    aggregatedMetricsByHost,
    servicesByHost,
    machineStatsByHost,
    connectionByHost,
    lastUpdate,
  };
}
