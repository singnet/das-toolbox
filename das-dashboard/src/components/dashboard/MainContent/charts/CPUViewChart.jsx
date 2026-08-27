import { LineChart } from "@mui/x-charts";

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

function showIsolatedMark(data) {
  return ({ index }) => {
    if (data[index] == null) {
      return false;
    }

    const prevEmpty = index === 0 || data[index - 1] == null;
    const nextEmpty = index === data.length - 1 || data[index + 1] == null;
    return prevEmpty && nextEmpty;
  };
}

export function CPUViewChart({ machine, currentService }) {
  const data = machine;

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
    curve: undefined,
    area: false,
    showMark: showIsolatedMark(a.cpu),
    connectNulls: false,
  }));

  const maxLength = Math.max(...filtered.map((a) => a.cpu.length), 0);
  const xAxisData = Array.from({ length: maxLength }, (_, i) => i + 1);

  return (
    <LineChart
      xAxis={[{
        data: xAxisData,
        scaleType: "point",
        min: 1,
        max: maxLength,
        disableTicks: true,
        tickLabelStyle: { display: "none" },
      }]}
      yAxis={[{ min: 0, max: 100, label: "CPU (container %)" }]}
      series={series}
      height={250}
      margin={{ left: 60, right: 36, top: 40, bottom: 20 }}
      slotProps={{ legend: { hidden: filtered.length > 5 } }}
      skipAnimation={true}
    />
  );
}