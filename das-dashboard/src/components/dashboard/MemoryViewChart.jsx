import { LineChart } from "@mui/x-charts";


export function MemoryViewChart({ machine }) {
  if (!machine) return null;

  const series = machine.metrics.agents.map((agent) => ({
    data: agent.memory,
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
            label: "Memory (MB)"
        }
        ]}
      series={series}
      height={250}
      grid={{ horizontal: true }}
    />
  );
}