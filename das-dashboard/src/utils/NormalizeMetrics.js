const formatCpuLabel = (cpu) => {
  const value = Number(cpu || 0);
  if (value === 0) return "0.00%";
  if (value > 0 && value < 1) return "<1%";
  return `${value.toFixed(2)}%`;
};

const formatMemoryLabel = (mb) => {
  const value = Number(mb || 0);
  if (value >= 1024) return `${(value / 1024).toFixed(2)} GB`;
  return `${value.toFixed(2)} MB`;
};

export function normalizeMachine(machine) {

  console.log(machine)

}

export function normalizeService(service) {
  const rawCpu = String(service?.cpu_percent || "0").replace("%", "").trim();
  const cpuNum = isNaN(parseFloat(rawCpu)) ? 0 : parseFloat(rawCpu);
  const memoryNum = isNaN(parseFloat(service?.memory_mb)) ? 0 : parseFloat(service?.memory_mb);

  return {
    ...service,
    cpu_percent: cpuNum,
    memory_mb: memoryNum,
    
    cpu_label: formatCpuLabel(cpuNum),
    memory_label: formatMemoryLabel(memoryNum),
    
    service_health:
      !service.service_health || service.service_health === "-"
        ? "healthy"
        : service.service_health,
  };
}