import { LineChart } from "@mui/x-charts";

export function CPUViewChart({ machine, currentService }) {
  if (!machine) return null;

  const filteredAgents = currentService
    ? machine.metrics.agents.filter(
        (agent) => agent.name === currentService
      )
    : machine.metrics.agents;

  const series = filteredAgents.map((agent) => ({
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