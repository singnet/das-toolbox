const EMPTY_VALUE = "-";
const ATOMDB_MARKERS = ["mongodb", "redis", "morkdb"];
const ARCH_MARKERS = ["agent", "broker"];

function containerMatches(containerName, patterns, serviceKey) {
  const matchPatterns = patterns?.length ? patterns : [serviceKey];
  return matchPatterns.some((pattern) => containerName.includes(pattern));
}

export function mergeHostServices(expectedServices = [], runtimeServices = []) {
  const usedContainers = new Set();

  return expectedServices.map((expected) => {
    const runtime = runtimeServices.find((service) => {
      const containerName = service?.container_name;
      if (!containerName || usedContainers.has(containerName)) {
        return false;
      }
      return containerMatches(containerName, expected.patterns, expected.key);
    });

    if (runtime?.container_name) {
      usedContainers.add(runtime.container_name);
    }

    const isRunning = runtime?.status === "running";

    return {
      service_key: expected.key,
      display_name: expected.displayName ?? expected.key,
      type: expected.type ?? "service",
      container_name: runtime?.container_name ?? expected.key,
      image: runtime?.image ?? EMPTY_VALUE,
      port: isRunning ? (runtime?.port ?? EMPTY_VALUE) : formatPort(expected.port),
      age: runtime?.age ?? EMPTY_VALUE,
      cpu_percent: isRunning ? runtime?.cpu_percent ?? 0 : null,
      memory_mb: isRunning ? runtime?.memory_mb ?? 0 : null,
      status: runtime?.status ?? "offline",
      service_health: runtime?.service_health ?? EMPTY_VALUE,
      is_running: isRunning,
    };
  });
}

export function getInfraStatus(services = []) {
  const running = services.filter((service) => service.is_running);
  const nameMatches = (name, markers) =>
    markers.some((marker) => name?.includes(marker));

  return {
    atomDbOnline: running.some((service) =>
      nameMatches(service.container_name, ATOMDB_MARKERS)
    ),
    architectureOnline: running.some((service) =>
      nameMatches(service.container_name, ARCH_MARKERS)
    ),
  };
}

function formatPort(port) {
  if (port === null || port === undefined || port === 0 || port === "") {
    return EMPTY_VALUE;
  }
  return String(port);
}

export function formatCpuCell(agent) {
  if (agent.cpu_percent === null || agent.cpu_percent === undefined) {
    return EMPTY_VALUE;
  }
  return `${agent.cpu_percent}%`;
}

export function formatMemoryCell(agent) {
  if (agent.memory_mb === null || agent.memory_mb === undefined) {
    return EMPTY_VALUE;
  }
  return `${Number(agent.memory_mb).toFixed(2)} GB`;
}

export function hostsToMachines(hosts = []) {
  return hosts.map(({ ip, services = [] }) => ({
    serverIp: ip,
    running: true,
    expectedServices: services,
  }));
}
