import { fetchDashboardDataStatic } from "../api/MetricsAPI";

export const DEFAULT_INFRA_STATUS = {
  atomDbOnline: false,
  architectureOnline: false,
};

const ATOMDB_CONTAINER_MARKERS = ["mongodb", "redis", "morkdb"];
const ARCHITECTURE_CONTAINER_MARKERS = [
  "query-engine",
  "attention-broker",
  "context-broker",
  "link-creation",
  "inference",
  "evolution",
  "command-router",
];

function isRunning(status) {
  return String(status ?? "").toLowerCase() === "running";
}

function containerName(entry, key) {
  return String(entry?.container_name ?? key ?? "").toLowerCase();
}

export function getInfraStatusFromStaticMetrics(metrics) {
  const serviceInfo = metrics?.serviceInfo;

  if (!serviceInfo || typeof serviceInfo !== "object") {
    return { ...DEFAULT_INFRA_STATUS };
  }

  let atomDbOnline = false;
  let architectureOnline = false;

  for (const [key, entry] of Object.entries(serviceInfo)) {
    if (!isRunning(entry?.status)) {
      continue;
    }

    const name = containerName(entry, key);

    if (ATOMDB_CONTAINER_MARKERS.some((marker) => name.includes(marker))) {
      atomDbOnline = true;
    }

    if (name.includes("atomdb-broker")) {
      continue;
    }

    if (ARCHITECTURE_CONTAINER_MARKERS.some((marker) => name.includes(marker))) {
      architectureOnline = true;
    }
  }

  return { atomDbOnline, architectureOnline };
}

export async function fetchInfraStatusForAllHosts(hosts = []) {
  const uniqueHosts = [...new Set(hosts.filter(Boolean))];

  if (!uniqueHosts.length) {
    return {};
  }

  const entries = await Promise.all(
    uniqueHosts.map(async (host) => {
      try {
        const metrics = await fetchDashboardDataStatic("all", host);
        return [host, getInfraStatusFromStaticMetrics(metrics)];
      } catch (error) {
        console.error(`Failed to fetch static metrics for ${host}:`, error);
        return [host, { ...DEFAULT_INFRA_STATUS }];
      }
    })
  );

  return Object.fromEntries(entries);
}
