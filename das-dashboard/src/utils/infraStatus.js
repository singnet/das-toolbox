import { fetchDashboardDataStatic } from "../api/MetricsAPI";

export const DEFAULT_INFRA_STATUS = {
  atomDbOnline: false,
  architectureOnline: false,
};

const ARCHITECTURE_COMMAND_LABELS = new Set([
  "attention-broker",
  "query-engine",
  "command-router",
  "context-broker",
  "link-creation-agent",
  "evolution-agent",
]);

const ATOMDB_NAME_MARKERS = [
  "mongodb",
  "redis",
  "morkdb",
  "database-adapter",
  "das-database-adapter",
];

const ATOMDB_COMMAND_LABELS = new Set(["db", "database-adapter", "database"]);

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isRunning(status) {
  return String(status ?? "").toLowerCase() === "running";
}

function isAtomDbEntry(entry) {
  const label = String(entry?.service_command_label ?? "").toLowerCase();
  if (ATOMDB_COMMAND_LABELS.has(label)) {
    return true;
  }

  const name = String(entry?.container_name ?? "").toLowerCase();
  return ATOMDB_NAME_MARKERS.some((marker) => name.includes(marker));
}

function isArchitectureEntry(entry) {
  const label = entry?.service_command_label;
  if (label && ARCHITECTURE_COMMAND_LABELS.has(label)) {
    return true;
  }

  const name = String(entry?.container_name ?? "").toLowerCase();
  if (name.includes("atomdb-broker")) {
    return false;
  }

  return [
    "query-engine",
    "attention-broker",
    "context-broker",
    "command-router",
    "link-creation",
    "evolution",
  ].some((marker) => name.includes(marker));
}

export function getRemoteDbServicesByHost(atomdb = {}) {
  if (atomdb.atomdb_type !== "remotedb") return {};
  const result = {};
  for (const peer of atomdb.remote_peers || []) {
    if (peer.type !== "redismongodb") continue;
    for (const [database, kind] of [["redis", "redis"], ["mongo", "mongodb"]]) {
      const endpoint = peer[`${database}_endpoint`];
      const port = peer[`${database}_port`];
      if (!endpoint || !port) continue;
      const host = ["localhost", "127.0.0.1", "0.0.0.0"].includes(endpoint) ? "localhost" : endpoint;
      (result[host] ||= []).push({ kind, port: Number(port) });
    }
  }
  return result;
}

export function getInfraStatusFromStaticMetrics(metrics, expectedDatabases = []) {
  const serviceInfo = metrics?.serviceInfo;

  if (!serviceInfo || typeof serviceInfo !== "object") {
    return { ...DEFAULT_INFRA_STATUS };
  }

  let atomDbOnline = false;
  let architectureOnline = false;

  for (const entry of Object.values(serviceInfo)) {
    if (!isRunning(entry?.status)) {
      continue;
    }

    if (isAtomDbEntry(entry)) {
      atomDbOnline = true;
    }

    if (isArchitectureEntry(entry)) {
      architectureOnline = true;
    }
  }

  if (expectedDatabases.length) {
    atomDbOnline = expectedDatabases.every(({ kind, port }) =>
      Object.values(serviceInfo).some((entry) =>
        isRunning(entry?.status) && Number(entry?.port) === port &&
        String(entry?.container_name || "").toLowerCase().includes(kind)
      )
    );
  }
  return { atomDbOnline, architectureOnline };
}

export async function fetchInfraStatusForAllHosts(hosts = [], expectedByHost = {}) {
  const uniqueHosts = [...new Set(hosts.filter(Boolean))];

  if (!uniqueHosts.length) {
    return {};
  }

  const entries = await Promise.all(
    uniqueHosts.map(async (host) => {
      try {
        const metrics = await fetchDashboardDataStatic("all", host);
        return [host, getInfraStatusFromStaticMetrics(metrics, expectedByHost[host])];
      } catch (error) {
        console.error(`Failed to fetch static metrics for ${host}:`, error);
        return [host, { ...DEFAULT_INFRA_STATUS }];
      }
    })
  );

  return Object.fromEntries(entries);
}

export async function pollInfraStatusForAllHosts(
  hosts = [],
  { attempts = 5, delayMs = 2000, expectedByHost = {} } = {}
) {
  let latest = {};

  for (let attempt = 0; attempt < attempts; attempt += 1) {
    if (attempt > 0) {
      await sleep(delayMs);
    }
    latest = await fetchInfraStatusForAllHosts(hosts, expectedByHost);
  }

  return latest;
}
