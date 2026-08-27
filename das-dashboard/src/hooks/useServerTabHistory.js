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

export const HISTORY_CHUNK_COUNT = 30;

// This function fills up a default CPU and Memory metrics array with null values.
// Then iterates through the points we receive from the back-end and fills up the empty indexes with the correct value and position.
// Position is given by the points on the back-end's payload. Each point has a "bucket" value that represents it's position inside the whole time period.

function padMetricSeries(points = [], chunkCount = HISTORY_CHUNK_COUNT) {
  const cpu = Array(chunkCount).fill(null); // Empty CPU with 30 null spaces
  const memory = Array(chunkCount).fill(null); // Empty Memory with 30 null spaces

  points.forEach((point) => {
    const rawBucket = Number(point.bucket);
    if (!Number.isFinite(rawBucket)) {
      return;
    }

    const bucket = Math.min(chunkCount - 1, Math.max(0, Math.floor(rawBucket)));
    cpu[bucket] = Number(point.cpu) || 0;
    memory[bucket] = Number(point.memory) || 0;
  });

  return { cpu, memory };
}

function toMachineHistory(payload) {
  const services = payload?.services ?? {};
  const chunkCount = Number(payload?.chunk_count) || HISTORY_CHUNK_COUNT;

  return {
    agents: Object.entries(services).map(([name, points]) => ({
      name,
      ...padMetricSeries(points, chunkCount),
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
