export const getStatusColor = (status) =>
  status === "Running" ? "#22c55e" : "#ef4444";

export const getHealthColor = (health) => {
  switch (health) {
    case "Healthy":
      return "#22c55e";
    case "Degraded":
      return "#f59e0b";
    case "Critical":
      return "#ef4444";
    default:
      return "#ffffff";
  }
};

export const parsePercent = (value) =>
  Number(String(value).replace("%", "")) || 0;

export const parseMemory = (value) => {
  const numeric =
    Number(String(value).replace(/[^\d.]/g, "")) || 0;

  return Math.min((numeric / 2500) * 100, 100);
};