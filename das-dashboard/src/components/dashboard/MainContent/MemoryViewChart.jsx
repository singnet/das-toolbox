import { LineChart } from "@mui/x-charts";

export function MemoryViewChart({ machine, currentService }) {
  if (!machine) return null;

  const filteredAgents = currentService
    ? machine.metrics.agents.filter(
        (agent) => agent.name === currentService
      )
    : machine.metrics.agents;

  const series = filteredAgents.map((agent) => ({
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
          label: "Memory (MB)",
        },
      ]}
      series={series}
      height={250}
      grid={{ horizontal: true }}
    />
  );
}