const ATOMDB_MARKERS = { db: "mongodb", redis: "redis", morkdb: "morkdb", "adapter-backend": "adapter" };

function matchesRuntime(serviceKey, runtime) {
  if (runtime?.service_command_label === serviceKey) return true;

  const name = String(runtime?.container_name ?? "").toLowerCase();
  if (!name) return false;

  const marker = ATOMDB_MARKERS[serviceKey];
  if (marker) {
    if (!name.includes(marker)) return false;
    const label = runtime?.service_command_label;
    return !label || label === "db" || label === serviceKey;
  }

  return name.includes(String(serviceKey).toLowerCase());
}

export function patchServicesWithRuntime(baseServices = [], runtimeServices = []) {
  const used = new Set();

  return baseServices.map((row) => {
    const runtime = runtimeServices.find((entry) => {
      const name = entry?.container_name;
      return name && !used.has(name) && matchesRuntime(row.service_key, entry);
    });

    if (!runtime) return row;

    used.add(runtime.container_name);
    const running = String(runtime.status ?? "").toLowerCase() === "running";

    return {
      ...row,
      service_command_label: runtime.service_command_label ?? row.service_command_label,
      display_name: runtime.service_name ?? row.display_name,
      container_name: runtime.container_name,
      image: runtime.image ?? row.image,
      port: running ? (runtime.port ?? row.port) : row.port,
      age: runtime.age ?? row.age,
      cpu_percent: running ? runtime.cpu_percent ?? 0 : null,
      memory_mb: running ? runtime.memory_mb ?? 0 : null,
      status: runtime.status ?? row.status,
      service_health: runtime.service_health ?? row.service_health,
      is_running: running,
    };
  });
}

export function rollupMetricsHistory(snapshots = []) {
  const byContainer = {};

  snapshots.forEach(({ data = [] }) => {
    data.forEach((service) => {
      const name = service.container_name;
      if (!name) return;
      if (!byContainer[name]) byContainer[name] = { name, cpu: [], memory: [] };
      byContainer[name].cpu.push(service.cpu_percent || 0);
      byContainer[name].memory.push(service.memory_mb || 0);
    });
  });

  return { agents: Object.values(byContainer) };
}

export function formatCpuCell(agent) {
  return agent.cpu_percent == null ? "-" : `${agent.cpu_percent}%`;
}

export function formatMemoryCell(agent) {
  return agent.memory_mb == null ? "-" : `${Number(agent.memory_mb).toFixed(2)} GB`;
}
