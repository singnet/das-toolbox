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

export function CPUViewChart({ machine, currentService }) {
  const { getAggregatedMetrics } = useDashboardContext();
  const data = machine || getAggregatedMetrics();

  if (!data?.agents?.length) {
    return null;
  }

  const filtered = currentService
    ? data.agents.filter((a) => a.name === currentService)
    : data.agents;

  const series = filtered.map((a) => ({
    data: a.cpu,
    label: a.name,
    color: stringToColor(a.name),
    curve: "catmullRom",
    area: true,
    showMark: false,
  }));

  const maxLength = Math.max(...filtered.map((a) => a.cpu.length), 0);
  const xAxisData = Array.from({ length: maxLength }, (_, i) => i + 1);

  return (
    <LineChart
      xAxis={[{ data: xAxisData, scaleType: "point", disableTicks: true, tickLabelStyle: { display: "none" },}]}
      yAxis={[{ min: 0, max: 100, label: "CPU (%/Core)" }]}
      series={series}
      height={250}
      margin={{ left: 60, right: 20, top: 40, bottom: 20 }}
      slotProps={{ legend: { hidden: filtered.length > 5 } }}
      skipAnimation={true}
    />
  );
}