export function isAtomDbService(service) {
  const label = String(service?.service_command_label ?? "").toLowerCase();
  if (["db", "database-adapter", "database", "redis", "morkdb", "adapterdb"].includes(label)) {
    return true;
  }

  const name = String(service?.container_name ?? "").toLowerCase();
  return ["mongodb", "redis", "morkdb", "database-adapter"].some((marker) => name.includes(marker));
}

export function serviceRowKey(service) {
  return service?.container_name || service?.service_command_label || "";
}

export function serviceDisplayName(service) {
  return service?.service_name || service?.container_name || service?.service_command_label || "-";
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
