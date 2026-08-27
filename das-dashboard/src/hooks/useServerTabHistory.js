import { useCallback, useEffect, useState } from "react";
import {
  fetchMetricsHistory,
  fetchCollectionStatus,
  setCollectionEnabled,
  deleteServerHistory,
  deleteUnusedHistory,
  deleteAllHistory,
} from "../api/MetricsAPI";

export const REALTIME_PERIOD = "realtime";

export const METRICS_PERIODS = [
  { value: REALTIME_PERIOD, label: "Real-time" },
  { value: "hour", label: "1 hour" },
  { value: "day", label: "1 day" },
  { value: "week", label: "1 week" },
];

function toMachineHistory(payload) {
  const services = payload?.services ?? {};

  return {
    agents: Object.entries(services).map(([name, points]) => ({
      name,
      cpu: (points ?? []).map((point) => Number(point.cpu) || 0),
      memory: (points ?? []).map((point) => Number(point.memory) || 0),
    })),
  };
}

export function useServerTabHistory(serverIp, period) {
  const [machineHistory, setMachineHistory] = useState({ agents: [] });
  const [historyLoading, setHistoryLoading] = useState(false);
  const [collecting, setCollecting] = useState(false);
  const [collectionBusy, setCollectionBusy] = useState(false);

  const refreshHistory = useCallback(async () => {
    if (!serverIp || !period || period === REALTIME_PERIOD) {
      setMachineHistory({ agents: [] });
      return;
    }

    setHistoryLoading(true);
    try {
      const payload = await fetchMetricsHistory(serverIp, period);
      setMachineHistory(toMachineHistory(payload));
    } catch (error) {
      console.error("Failed to load metrics history:", error);
      setMachineHistory({ agents: [] });
      throw error;
    } finally {
      setHistoryLoading(false);
    }
  }, [serverIp, period]);

  useEffect(() => {
    refreshHistory().catch(() => {});
  }, [refreshHistory]);

  useEffect(() => {
    let active = true;
    setCollecting(false);

    if (!serverIp) {
      return () => {
        active = false;
      };
    }

    fetchCollectionStatus(serverIp)
      .then((status) => {
        if (active) {
          setCollecting(Boolean(status?.collecting));
        }
      })
      .catch((error) => {
        console.error("Failed to load collection status:", error);
        if (active) {
          setCollecting(false);
        }
      });

    return () => {
      active = false;
    };
  }, [serverIp]);

  const toggleCollection = useCallback(async () => {
    if (!serverIp) return;

    setCollectionBusy(true);
    try {
      const status = await setCollectionEnabled(serverIp, !collecting);
      setCollecting(Boolean(status?.collecting));
    } finally {
      setCollectionBusy(false);
    }
  }, [serverIp, collecting]);

  const clearServerHistory = useCallback(async () => {
    if (!serverIp) return;
    await deleteServerHistory(serverIp);
    await refreshHistory();
  }, [serverIp, refreshHistory]);

  const clearUnusedHistory = useCallback(async () => {
    await deleteUnusedHistory();
    await refreshHistory();
  }, [refreshHistory]);

  const clearAllHistory = useCallback(async () => {
    await deleteAllHistory();
    await refreshHistory();
  }, [refreshHistory]);

  return {
    machineHistory,
    historyLoading,
    collecting,
    collectionBusy,
    refreshHistory,
    toggleCollection,
    clearServerHistory,
    clearUnusedHistory,
    clearAllHistory,
  };
}
