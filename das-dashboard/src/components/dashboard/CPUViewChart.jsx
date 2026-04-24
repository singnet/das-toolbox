import { LineChart } from "@mui/x-charts";

export function CPUViewChart({ machine }) {
  if (!machine) return null;

  const series = machine.metrics.agents.map((agent) => ({
    data: agent.cpu,
    label: agent.name,
    curve: "monotoneX",
  }));

  return (
    <LineChart
      xAxis={[
        {
          data: machine.metrics.timestamps,
          scaleType: "point",
          label: "Time",
        },
      ]}
      yAxis={[
        {
          min: 0,
          max: 100,
          label: "CPU (%)",
        },
      ]}
      series={series}
      height={250}
      grid={{ horizontal: true }}
    />
  );
}