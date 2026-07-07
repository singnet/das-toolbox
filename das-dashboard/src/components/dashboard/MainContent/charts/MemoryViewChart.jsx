import { LineChart } from "@mui/x-charts";
import { useDashboardContext } from "../../../global_providers/DashboardContextProvider";

const stringToColor = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  let color = "#";
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 255;
    color += ("00" + value.toString(16)).slice(-2);
  }
  return color;
};

function formatAxisValue(value) {
  const numeric = Number(value);
  return Number.isInteger(numeric) ? String(numeric) : numeric.toFixed(2);
}

export function MemoryViewChart({ machine, currentService, stats }) {
  const { machineStats } = useDashboardContext();
  const data = machine;
  const totalMemoryGb = Number((stats ?? machineStats)?.MemoryInfo?.totalMemory) || 0;

  if (!data?.agents?.length) {
    return null;
  }

  const filtered = currentService
    ? data.agents.filter((a) => a.name === currentService)
    : data.agents;

  const series = filtered.map((a) => ({
    data: a.memory,
    label: a.name,
    color: stringToColor(a.name),
    curve: undefined,
    area: true,
    showMark: false,
    stack: "Memory",
  }));

  const maxLength = Math.max(...filtered.map((a) => a.memory.length), 0);
  const xAxisData = Array.from({ length: maxLength }, (_, i) => i + 1);

  const yAxis = {
    label: "Memory (GB)",
    min: 0,
    valueFormatter: formatAxisValue,
  };

  if (totalMemoryGb > 0) {
    yAxis.max = totalMemoryGb;
  }

  return (
    <LineChart
      xAxis={[{ data: xAxisData, scaleType: "point", disableTicks: true, tickLabelStyle: { display: "none" } }]}
      yAxis={[yAxis]}
      series={series}
      height={250}
      margin={{ left: 60, right: 20, top: 40, bottom: 20 }}
      slotProps={{ legend: { hidden: filtered.length > 5 } }}
      skipAnimation={true}
    />
  );
}
